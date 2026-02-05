#!/usr/bin/env python3
"""
Aplicație client NTP pentru obținerea orei exacte
Suportă zone GMT±X (X = 0-11)
"""

import socket
import struct
import time
import datetime
import os
import re

# Servere NTP publice
NTP_SERVERS = [
    'pool.ntp.org',
    'time.nist.gov',
    'time.google.com',
    'ntp1.stratum1.ru',
    'ntp.ubuntu.com'
]

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

def parse_timezone_input(tz_input):
    """Parsează input-ul zonei orare."""
    tz_input = tz_input.strip().upper()
    
    # Verifică formatul GMT±X
    pattern = r'^GMT([+-]\d+)$'
    match = re.match(pattern, tz_input)
    
    if match:
        offset_str = match.group(1)
        try:
            offset = int(offset_str)
            if -11 <= offset <= 11:
                return offset
            else:
                return None
        except ValueError:
            return None
    
    return None

def get_ntp_time(server='pool.ntp.org'):
    """Obține timpul de la un server NTP."""
    try:
        # NTP protocol port 123
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(5)
        
        # NTP packet (48 bytes)
        # LI=0, VN=4, Mode=3 (client)
        packet = b'\x1b' + 47 * b'\0'
        
        # Trimite cererea
        client.sendto(packet, (server, 123))
        
        # Primește răspunsul
        response, _ = client.recvfrom(1024)
        
        if len(response) < 48:
            raise ValueError("Răspuns NTP invalid")
        
        # Extrage transmit timestamp (bytes 40-47)
        transmit_timestamp = struct.unpack('!I', response[40:44])[0]
        
        # NTP timestamp-ul este numărul de secunde de la 1 Ianuarie 1900
        # Unix timestamp este de la 1 Ianuarie 1970
        ntp_to_unix = 2208988800  # Secunde între 1900 și 1970
        unix_timestamp = transmit_timestamp - ntp_to_unix
        
        client.close()
        return unix_timestamp
        
    except socket.timeout:
        raise Exception(f"Timeout la conectarea cu serverul {server}")
    except socket.gaierror:
        raise Exception(f"Nu s-a putut rezolva numele serverului {server}")
    except Exception as e:
        raise Exception(f"Eroare la conectarea cu {server}: {e}")

def get_ntp_time_with_fallback():
    """Încearcă să obțină timpul de la mai multe servere NTP."""
    for server in NTP_SERVERS:
        try:
            color_print(f"🔍 Încercare server NTP: {server}...", 'info')
            timestamp = get_ntp_time(server)
            color_print(f"✓ Conectat cu succes la {server}", 'success')
            return timestamp, server
        except Exception as e:
            color_print(f"✗ Eroare la {server}: {e}", 'error')
            continue
    
    raise Exception("Nu s-a putut conecta la niciun server NTP")

def format_time_with_timezone(timestamp, timezone_offset):
    """Formatează timpul cu offset-ul specificat."""
    # Convertește timestamp în datetime UTC
    utc_time = datetime.datetime.utcfromtimestamp(timestamp)
    
    # Aplică offset-ul zonei orare
    offset_hours = timezone_offset
    local_time = utc_time + datetime.timedelta(hours=offset_hours)
    
    # Formatează timpul
    formatted_time = local_time.strftime("%A, %d %B %Y, %H:%M:%S")
    
    # Determină prefixul zonei
    if timezone_offset >= 0:
        zone_str = f"GMT+{timezone_offset}"
    else:
        zone_str = f"GMT{timezone_offset}"
    
    return formatted_time, zone_str

def show_timezone_info():
    """Afișează informații despre zonele orare."""
    print_section("🌍 INFORMAȚII ZONE ORARE")
    
    color_print("Format acceptat: GMT±X", 'info')
    color_print("Unde X este un număr între 0 și 11", 'info')
    color_print("", 'white')
    
    # Exemple de zone orare comune
    zones = [
        ("GMT+0", "Londra, Lisabona, Dublin"),
        ("GMT+1", "Paris, Berlin, București, Roma"),
        ("GMT+2", "Cairo, Helsinki, Atena"),
        ("GMT+3", "Moscow, Istanbul, Nairobi"),
        ("GMT+4", "Dubai, Baku, Tbilisi"),
        ("GMT+5", "Karachi, Tashkent, Male"),
        ("GMT+6", "Dhaka, Almaty, Omsk"),
        ("GMT+7", "Bangkok, Jakarta, Hanoi"),
        ("GMT+8", "Beijing, Singapore, Manila"),
        ("GMT+9", "Tokyo, Seoul, Osaka"),
        ("GMT+10", "Sydney, Melbourne, Brisbane"),
        ("GMT+11", "Solomon Islands, Noumea"),
        ("GMT-1", "Azores, Cape Verde"),
        ("GMT-2", "South Georgia Islands"),
        ("GMT-3", "Buenos Aires, Rio de Janeiro, Montevideo"),
        ("GMT-4", "New York, Washington DC, Toronto"),
        ("GMT-5", "Chicago, Mexico City, Lima"),
        ("GMT-6", "Denver, Guatemala, Mexico City"),
        ("GMT-7", "Los Angeles, Phoenix, Calgary"),
        ("GMT-8", "San Francisco, Vancouver, Seattle"),
        ("GMT-9", "Anchorage, Juneau"),
        ("GMT-10", "Honolulu, Tahiti"),
        ("GMT-11", "American Samoa, Midway Island")
    ]
    
    color_print("📍 Zone orare comune:", 'info')
    for zone, locations in zones:
        print_result(zone, locations)

def show_server_info():
    """Afișează informații despre serverele NTP."""
    print_section("🌐 SERVERE NTP")
    
    color_print("Servere NTP publice utilizate:", 'info')
    for i, server in enumerate(NTP_SERVERS, 1):
        print_list_item(i, server)
    
    color_print("", 'white')
    color_print("ℹ  Aplicația încearcă serverele în ordine până găsește unul funcțional.", 'warning')

def display_clock(time_str, timezone_str):
    """Afișează un ceas vizual."""
    print_section(f"🕐 OREI EXACTĂ - {timezone_str}")
    
    # Afișează ceasul vizual
    clock_lines = [
        "    ┌─────────────────┐",
        "    │  🌍 NTP CLOCK   │",
        "    │─────────────────│",
        f"    │  {timezone_str:^15}  │",
        "    │─────────────────│",
        "    │                 │",
        f"    │  {time_str:^15}  │",
        "    │                 │",
        "    └─────────────────┘"
    ]
    
    for line in clock_lines:
        color_print(line, 'cyan')
    
    # Afișează informații suplimentare
    color_print("\n📋 Detalii:", 'info')
    print_result("Format dată", time_str)
    print_result("Zonă orară", timezone_str)
    print_result("Precizie", "Milisecunde (NTP)")

def main():
    """Funcția principală."""
    
    print_header("🕐 CLIENT NTP - ORĂ EXACTĂ")
    color_print("📝 Obține ora exactă de la servere NTP pentru orice zonă GMT±X", 'info')
    color_print("🌍 Suportă zone GMT±X unde X este între 0 și 11", 'info')
    
    while True:
        try:
            print_section("🎮 MENIU PRINCIPAL")
            
            color_print("  1. Obține ora exactă pentru o zonă", 'info')
            color_print("  2. Vezi informații despre zone orare", 'info')
            color_print("  3. Vezi informații despre servere NTP", 'info')
            color_print("  4. Ieșire", 'info')
            color_print("──────────────────────────────────────────────────", 'info')
            
            choice = color_input("\nAlege o opțiune: ")
            
            if choice == '1':
                print_section("🕐 OREI EXACTĂ")
                
                # Obține input-ul utilizatorului
                timezone_input = color_input("Introdu zona orară (ex: GMT+2, GMT-5, GMT0): ")
                
                # Validează input-ul
                timezone_offset = parse_timezone_input(timezone_input)
                
                if timezone_offset is None:
                    color_print("✗ Format invalid! Folosește formatul GMT±X (ex: GMT+2, GMT-5, GMT0)", 'error')
                    color_print("ℹ  X trebuie să fie un număr între 0 și 11", 'warning')
                    continue
                
                # Obține timpul NTP
                try:
                    color_print("🔍 Obținere timp NTP...", 'info')
                    timestamp, server_used = get_ntp_time_with_fallback()
                    
                    # Formatează timpul
                    formatted_time, timezone_str = format_time_with_timezone(timestamp, timezone_offset)
                    
                    # Afișează rezultatul
                    display_clock(formatted_time, timezone_str)
                    print_result("Server NTP utilizat", server_used)
                    print_result("Timestamp Unix", f"{timestamp:.2f}")
                    
                except Exception as e:
                    color_print(f"✗ EROARE: {e}", 'error')
                    color_print("ℹ  Verifică conexiunea la internet.", 'warning')
            
            elif choice == '2':
                show_timezone_info()
            
            elif choice == '3':
                show_server_info()
            
            elif choice == '4':
                color_print("👋 La revedere!", 'success')
                break
            
            else:
                color_print("✗ EROARE: Opțiune invalidă!", 'error')
        
        except KeyboardInterrupt:
            color_print("\n👋 La revedere!", 'success')
            break
        except EOFError:
            color_print("\n👋 La revedere!", 'success')
            break

if __name__ == "__main__":
    main()
