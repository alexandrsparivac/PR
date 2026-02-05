#!/usr/bin/env python3
"""
Aplicație de tip client DNS
- resolve <domain> - găsește IP-urile pentru un domeniu
- resolve <ip> - găsește domeniile pentru un IP (reverse DNS)
- use dns <ip> - schimbă serverul DNS utilizat
"""

import socket
import struct
import random
import re
import os

# DNS server implicit (Google DNS)
current_dns_server = None  # None = folosește DNS-ul sistemului

# Culori pentru terminal
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'bold': '\033[1m',
    'underline': '\033[4m',
    'reset': '\033[0m',
    'header': '\033[95m\033[1m',
    'success': '\033[92m\033[1m',
    'error': '\033[91m\033[1m',
    'info': '\033[94m\033[1m',
    'warning': '\033[93m\033[1m',
    'result': '\033[96m',
    'command': '\033[93m'
}

def color_print(text, color='white'):
    """Afișează text cu culoare."""
    if os.name == 'nt':  # Windows - fără culori
        print(text)
    else:
        print(f"{COLORS.get(color, COLORS['white'])}{text}{COLORS['reset']}")

def color_input(prompt, color='command'):
    """Input cu culoare."""
    if os.name == 'nt':  # Windows - fără culori
        return input(prompt)
    else:
        return input(f"{COLORS.get(color, COLORS['white'])}{prompt}{COLORS['reset']}")

def print_header(text):
    """Afișează un header decorat."""
    separator = "=" * 60
    color_print(separator, 'header')
    color_print(f"{text:^60}", 'header')
    color_print(separator, 'header')

def print_section(title):
    """Afișează o secțiune."""
    color_print(f"\n{'─' * 50}", 'info')
    color_print(f"  {title}", 'info')
    color_print(f"{'─' * 50}", 'info')

def print_result(label, value):
    """Afișează un rezultat formatat."""
    color_print(f"  {label}: ", 'info')
    color_print(value, 'result')

def print_list_item(index, item):
    """Afișează un element din listă."""
    color_print(f"  [{index}] ", 'yellow')
    color_print(item, 'result')


def is_valid_ip(address):
    """Verifică dacă adresa este un IP valid."""
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False


def get_system_dns():
    """Returnează DNS-ul sistemului (pentru afișare)."""
    return "DNS-ul sistemului"


def build_dns_query(domain, query_type=1):
    """
    Construiește un pachet DNS query.
    query_type: 1 = A (IPv4), 12 = PTR (reverse)
    """
    # Header DNS
    transaction_id = random.randint(0, 65535)
    flags = 0x0100  # Standard query, recursion desired
    questions = 1
    answer_rrs = 0
    authority_rrs = 0
    additional_rrs = 0
    
    header = struct.pack('>HHHHHH', transaction_id, flags, questions, 
                         answer_rrs, authority_rrs, additional_rrs)
    
    # Question section
    question = b''
    for part in domain.split('.'):
        question += bytes([len(part)]) + part.encode('utf-8')
    question += b'\x00'  # Null terminator
    
    # Query type și class
    question += struct.pack('>HH', query_type, 1)  # Type și Class IN
    
    return header + question, transaction_id


def parse_dns_response(response, query_type):
    """Parsează răspunsul DNS și extrage adresele."""
    results = []
    
    # Header: 12 bytes
    if len(response) < 12:
        return results
    
    header = struct.unpack('>HHHHHH', response[:12])
    answer_count = header[3]
    
    # Sari peste header și question section
    offset = 12
    
    # Sari peste question section
    while offset < len(response) and response[offset] != 0:
        length = response[offset]
        if length >= 192:  # Pointer
            offset += 2
            break
        offset += length + 1
    else:
        offset += 1  # Null terminator
    
    offset += 4  # Query type și class
    
    # Parsează answer section
    for _ in range(answer_count):
        if offset >= len(response):
            break
        
        # Name (poate fi pointer)
        if response[offset] >= 192:
            offset += 2
        else:
            while offset < len(response) and response[offset] != 0:
                offset += response[offset] + 1
            offset += 1
        
        if offset + 10 > len(response):
            break
        
        rtype, rclass, ttl, rdlength = struct.unpack('>HHIH', response[offset:offset+10])
        offset += 10
        
        if offset + rdlength > len(response):
            break
        
        rdata = response[offset:offset+rdlength]
        offset += rdlength
        
        if rtype == 1 and rdlength == 4:  # A record (IPv4)
            ip = '.'.join(str(b) for b in rdata)
            results.append(ip)
        elif rtype == 12:  # PTR record
            # Parsează numele de domeniu
            name = parse_domain_name(response, offset - rdlength)
            if name:
                results.append(name)
    
    return results


def parse_domain_name(response, offset):
    """Parsează un nume de domeniu din răspunsul DNS."""
    parts = []
    visited = set()
    
    while offset < len(response):
        if offset in visited:
            break
        visited.add(offset)
        
        length = response[offset]
        
        if length == 0:
            break
        elif length >= 192:  # Pointer
            if offset + 1 >= len(response):
                break
            pointer = ((length & 0x3F) << 8) | response[offset + 1]
            return parse_domain_name(response, pointer)
        else:
            offset += 1
            if offset + length > len(response):
                break
            parts.append(response[offset:offset+length].decode('utf-8', errors='ignore'))
            offset += length
    
    return '.'.join(parts) if parts else None


def resolve_with_custom_dns(query, dns_server):
    """Trimite query DNS către un server specific."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    
    try:
        sock.sendto(query, (dns_server, 53))
        response, _ = sock.recvfrom(512)
        return response
    finally:
        sock.close()


def resolve_domain(domain):
    """Rezolvă un domeniu în adrese IP."""
    global current_dns_server
    
    if current_dns_server:
        # Folosește DNS-ul personalizat
        try:
            query, _ = build_dns_query(domain, query_type=1)
            response = resolve_with_custom_dns(query, current_dns_server)
            return parse_dns_response(response, query_type=1)
        except socket.timeout:
            color_print(f"✗ EROARE: Timeout la conectarea cu DNS server {current_dns_server}", 'error')
            return []
        except Exception as e:
            color_print(f"✗ EROARE: {e}", 'error')
            return []
    else:
        # Folosește DNS-ul sistemului
        try:
            _, _, ip_list = socket.gethostbyname_ex(domain)
            return ip_list
        except socket.gaierror as e:
            color_print(f"✗ EROARE: Nu s-a putut rezolva domeniul: {e}", 'error')
            return []


def resolve_ip(ip_address):
    """Rezolvă un IP în nume de domeniu (reverse DNS)."""
    global current_dns_server
    
    # Construiește adresa PTR (reverse)
    parts = ip_address.split('.')
    ptr_domain = '.'.join(reversed(parts)) + '.in-addr.arpa'
    
    if current_dns_server:
        # Folosește DNS-ul personalizat
        try:
            query, _ = build_dns_query(ptr_domain, query_type=12)
            response = resolve_with_custom_dns(query, current_dns_server)
            return parse_dns_response(response, query_type=12)
        except socket.timeout:
            color_print(f"✗ EROARE: Timeout la conectarea cu DNS server {current_dns_server}", 'error')
            return []
        except Exception as e:
            color_print(f"✗ EROARE: {e}", 'error')
            return []
    else:
        # Folosește DNS-ul sistemului
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            return [hostname]
        except socket.herror as e:
            color_print(f"✗ EROARE: Nu s-a putut rezolva IP-ul: {e}", 'error')
            return []


def handle_resolve(argument):
    """Gestionează comanda resolve."""
    if is_valid_ip(argument):
        print_section(f"🔍 REVERSE DNS - IP: {argument}")
        domains = resolve_ip(argument)
        if domains:
            color_print(f"✓ Domenii găsite pentru {argument}:", 'success')
            for i, domain in enumerate(domains, 1):
                print_list_item(i, domain)
        else:
            color_print(f"ℹ  Nu s-au găsit domenii pentru {argument}", 'warning')
    else:
        print_section(f"🔍 DNS LOOKUP - DOMENIU: {argument}")
        ips = resolve_domain(argument)
        if ips:
            color_print(f"✓ Adrese IP pentru {argument}:", 'success')
            for i, ip in enumerate(ips, 1):
                print_list_item(i, ip)
        else:
            color_print(f"ℹ  Nu s-au găsit adrese IP pentru {argument}", 'warning')


def handle_use_dns(dns_ip):
    """Gestionează comanda use dns."""
    global current_dns_server
    
    if not is_valid_ip(dns_ip):
        color_print(f"✗ EROARE: '{dns_ip}' nu este o adresă IP validă!", 'error')
        return
    
    current_dns_server = dns_ip
    color_print(f"✓ DNS server schimbat la: {dns_ip}", 'success')


def show_help():
    """Afișează ajutorul."""
    print_header("AJUTOR - COMENZI DISPONIBILE")
    
    commands = [
        ("resolve <domain>", "Găsește IP-urile pentru un domeniu"),
        ("resolve <ip>", "Găsește domeniile pentru un IP (reverse DNS)"),
        ("use dns <ip>", "Schimbă serverul DNS utilizat"),
        ("use dns system", "Revine la DNS-ul sistemului"),
        ("status", "Afișează DNS-ul curent utilizat"),
        ("help", "Afișează acest ajutor"),
        ("exit", "Ieșire din aplicație")
    ]
    
    for cmd, desc in commands:
        print_result(cmd, desc)
    
    color_print("\n📌 Exemple de servere DNS populare:", 'info')
    dns_examples = [
        "Google DNS: 8.8.8.8, 8.8.4.4",
        "Cloudflare: 1.1.1.1, 1.0.0.1",
        "OpenDNS: 208.67.222.222",
        "Quad9: 9.9.9.9"
    ]
    
    for example in dns_examples:
        color_print(f"  • {example}", 'result')


def show_status():
    """Afișează statusul curent."""
    global current_dns_server
    print_section("📊 STATUS DNS")
    
    if current_dns_server:
        print_result("DNS Server curent", current_dns_server)
        color_print("ℹ  Se utilizează un server DNS personalizat", 'info')
    else:
        print_result("DNS Server", "DNS-ul sistemului")
        color_print("ℹ  Se utilizează DNS-ul configurat în sistem", 'info')


def main():
    global current_dns_server
    
    print_header("🌍 APLICAȚIE CLIENT DNS")
    color_print("📝 Tastează 'help' pentru lista de comenzi.", 'info')
    color_print("🔍 Rezolvă domenii și adrese IP cu servere DNS personalizate.", 'info')
    
    while True:
        try:
            command = color_input("\ndns> ", 'command')
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == 'exit' or cmd == 'quit':
                color_print("👋 La revedere!", 'success')
                break
            
            elif cmd == 'help':
                show_help()
            
            elif cmd == 'status':
                show_status()
            
            elif cmd == 'resolve':
                if len(parts) < 2:
                    color_print("✗ EROARE: Utilizare: resolve <domain> sau resolve <ip>", 'error')
                else:
                    handle_resolve(parts[1])
            
            elif cmd == 'use':
                if len(parts) < 3 or parts[1].lower() != 'dns':
                    color_print("✗ EROARE: Utilizare: use dns <ip> sau use dns system", 'error')
                else:
                    if parts[2].lower() == 'system':
                        current_dns_server = None
                        color_print("✓ S-a revenit la DNS-ul sistemului", 'success')
                    else:
                        handle_use_dns(parts[2])
            
            else:
                color_print(f"✗ EROARE: Comandă necunoscută: '{cmd}'. Tastează 'help' pentru ajutor.", 'error')
        
        except KeyboardInterrupt:
            color_print("\n👋 La revedere!", 'success')
            break
        except EOFError:
            color_print("\n👋 La revedere!", 'success')
            break


if __name__ == "__main__":
    main()
