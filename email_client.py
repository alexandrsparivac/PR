#!/usr/bin/env python3
"""
Aplicație client Email pentru Gmail
- Suport POP3 și IMAP pentru primire email-uri
- Trimitere email-uri cu și fără atașamente
- Descărcare email-uri cu atașamente
"""

import poplib
import imaplib
import smtplib
import ssl
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json
import base64
from datetime import datetime
import getpass

# Configurare Gmail
GMAIL_POP3_SERVER = "pop.gmail.com"
GMAIL_POP3_PORT = 995
GMAIL_IMAP_SERVER = "imap.gmail.com"
GMAIL_IMAP_PORT = 993
GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587

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

def save_credentials(email_addr, password):
    """Salvează credențialele criptate."""
    try:
        credentials = {
            'email': email_addr,
            'password': base64.b64encode(password.encode()).decode()
        }
        with open('email_credentials.json', 'w') as f:
            json.dump(credentials, f)
        return True
    except:
        return False

def load_credentials():
    """Încarcă credențialele salvate."""
    try:
        with open('email_credentials.json', 'r') as f:
            credentials = json.load(f)
            return credentials['email'], base64.b64decode(credentials['password']).decode()
    except:
        return None, None

def get_credentials():
    """Obține credențialele de la utilizator."""
    # Încearcă să încarce credențialele salvate
    saved_email, saved_password = load_credentials()
    
    if saved_email and saved_password:
        use_saved = color_input(f"Se folosesc credențialele salvate pentru {saved_email}? (da/nu): ")
        if use_saved.lower() == 'da':
            return saved_email, saved_password
    
    email_addr = color_input("Introdu adresa de email Gmail: ")
    password = getpass.getpass("Introdu parola (sau app password): ")
    
    save_choice = color_input("Salvezi credențialele pentru viitor? (da/nu): ")
    if save_choice.lower() == 'da':
        if save_credentials(email_addr, password):
            color_print("✓ Credențialele au fost salvate.", 'success')
        else:
            color_print("✗ Nu s-au putut salva credențialele.", 'warning')
    
    return email_addr, password

def list_emails_pop3(email_addr, password):
    """Listează email-urile folosind POP3."""
    print_section("📧 LISTARE EMAIL-uri (POP3)")
    
    try:
        # Conectare POP3 cu SSL
        context = ssl.create_default_context()
        mail = poplib.POP3_SSL(GMAIL_POP3_SERVER, GMAIL_POP3_PORT, context=context)
        
        try:
            mail.user(email_addr)
            mail.pass_(password)
            
            # Obține numărul de email-uri
            num_messages = len(mail.list()[1])
            color_print(f"✓ Conectat! Ai {num_messages} email-uri în inbox.", 'success')
            
            if num_messages == 0:
                color_print("ℹ  Nu există email-uri.", 'warning')
                return
            
            # Afișează ultimele 10 email-uri
            max_emails = min(10, num_messages)
            color_print(f"\n📋 Ultimele {max_emails} email-uri:", 'info')
            
            for i in range(num_messages - max_emails + 1, num_messages + 1):
                try:
                    # Obține email-ul
                    raw_email = b"\n".join(mail.retr(i)[1])
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extrage informații
                    subject = msg.get('Subject', 'Fără subiect')
                    from_addr = msg.get('From', 'Fără expeditor')
                    date = msg.get('Date', 'Fără dată')
                    
                    # Decodifică subiectul
                    if subject.startswith('=?'):
                        decoded_subject = email.header.decode_header(subject)[0]
                        if isinstance(decoded_subject[0], bytes):
                            subject = decoded_subject[0].decode(decoded_subject[1] or 'utf-8')
                        else:
                            subject = decoded_subject[0]
                    
                    print_list_item(i, f"De la: {from_addr}")
                    print_result("  Subiect", subject)
                    print_result("  Data", date)
                    color_print("", 'white')
                    
                except Exception as e:
                    color_print(f"✗ Eroare la citirea email-ului {i}: {e}", 'error')
        
        finally:
            mail.quit()
            
    except poplib.error_proto as e:
        color_print(f"✗ EROARE POP3: {e}", 'error')
        color_print("ℹ  Asigură-te că ai activat POP3 în setările Gmail și folosești app password.", 'warning')
    except Exception as e:
        color_print(f"✗ EROARE: {e}", 'error')

def list_emails_imap(email_addr, password):
    """Listează email-urile folosind IMAP."""
    print_section("📧 LISTARE EMAIL-uri (IMAP)")
    
    try:
        # Conectare IMAP cu SSL
        mail = imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER, GMAIL_IMAP_PORT)
        
        try:
            mail.login(email_addr, password)
            
            # Selectează inbox
            mail.select('inbox')
            
            # Caută toate email-urile
            status, messages = mail.search(None, 'ALL')
            
            if status != 'OK':
                color_print("✗ Nu s-au putut găsi email-uri.", 'error')
                return
            
            email_ids = messages[0].split()
            color_print(f"✓ Conectat! Ai {len(email_ids)} email-uri în inbox.", 'success')
            
            if len(email_ids) == 0:
                color_print("ℹ  Nu există email-uri.", 'warning')
                return
            
            # Afișează ultimele 10 email-uri
            max_emails = min(10, len(email_ids))
            color_print(f"\n📋 Ultimele {max_emails} email-uri:", 'info')
            
            for i in range(-max_emails, 0):
                email_id = email_ids[i]
                
                try:
                    # Obține email-ul
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        # Extrage informații
                        subject = msg.get('Subject', 'Fără subiect')
                        from_addr = msg.get('From', 'Fără expeditor')
                        date = msg.get('Date', 'Fără dată')
                        
                        # Decodifică subiectul
                        if subject.startswith('=?'):
                            decoded_subject = email.header.decode_header(subject)[0]
                            if isinstance(decoded_subject[0], bytes):
                                subject = decoded_subject[0].decode(decoded_subject[1] or 'utf-8')
                            else:
                                subject = decoded_subject[0]
                        
                        print_list_item(email_id.decode(), f"De la: {from_addr}")
                        print_result("  Subiect", subject)
                        print_result("  Data", date)
                        color_print("", 'white')
                
                except Exception as e:
                    color_print(f"✗ Eroare la citirea email-ului {email_id}: {e}", 'error')
        
        finally:
            mail.logout()
            
    except imaplib.IMAP4.error as e:
        color_print(f"✗ EROARE IMAP: {e}", 'error')
        color_print("ℹ  Asigură-te că ai activat IMAP în setările Gmail și folosești app password.", 'warning')
    except Exception as e:
        color_print(f"✗ EROARE: {e}", 'error')

def download_email_with_attachments(email_addr, password):
    """Descarcă un email cu atașamente."""
    print_section("📥 DESCĂRCARE EMAIL CU ATAȘAMENTE")
    
    try:
        # Folosește IMAP pentru mai mult control
        mail = imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER, GMAIL_IMAP_PORT)
        
        try:
            mail.login(email_addr, password)
            mail.select('inbox')
            
            # Caută email-uri cu atașamente
            status, messages = mail.search(None, 'ALL')
            
            if status != 'OK':
                color_print("✗ Nu s-au putut găsi email-uri.", 'error')
                return
            
            email_ids = messages[0].split()
            
            # Caută email-uri cu atașamente
            emails_with_attachments = []
            
            for email_id in email_ids:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        # Verifică dacă are atașamente
                        has_attachment = False
                        for part in msg.walk():
                            if part.get_content_disposition() == 'attachment':
                                has_attachment = True
                                break
                        
                        if has_attachment:
                            subject = msg.get('Subject', 'Fără subiect')
                            from_addr = msg.get('From', 'Fără expeditor')
                            
                            if subject.startswith('=?'):
                                decoded_subject = email.header.decode_header(subject)[0]
                                if isinstance(decoded_subject[0], bytes):
                                    subject = decoded_subject[0].decode(decoded_subject[1] or 'utf-8')
                                else:
                                    subject = decoded_subject[0]
                            
                            emails_with_attachments.append({
                                'id': email_id,
                                'subject': subject,
                                'from': from_addr
                            })
                
                except:
                    continue
            
            if not emails_with_attachments:
                color_print("ℹ  Nu s-au găsit email-uri cu atașamente.", 'warning')
                return
            
            # Afișează email-urile cu atașamente
            color_print(f"✓ S-au găsit {len(emails_with_attachments)} email-uri cu atașamente:", 'success')
            
            for i, email_info in enumerate(emails_with_attachments[:10], 1):
                print_list_item(i, f"ID: {email_info['id'].decode()} - {email_info['subject']}")
                print_result("  De la", email_info['from'])
                color_print("", 'white')
            
            # Alege un email pentru descărcare
            choice = color_input("Alege numărul email-ului de descărcat: ")
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(emails_with_attachments):
                    selected_email = emails_with_attachments[choice_idx]
                    download_single_email(mail, selected_email['id'], selected_email['subject'])
                else:
                    color_print("✗ Număr invalid.", 'error')
            except ValueError:
                color_print("✗ Introdu un număr valid.", 'error')
        
        finally:
            mail.logout()
            
    except Exception as e:
        color_print(f"✗ EROARE: {e}", 'error')

def download_single_email(mail, email_id, subject):
    """Descarcă un singur email cu toate atașamentele."""
    try:
        # Creează director pentru email
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
        email_dir = f"email_{email_id.decode()}_{safe_subject}"
        os.makedirs(email_dir, exist_ok=True)
        
        # Obține email-ul complet
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        
        if status == 'OK':
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Salvează conținutul email-ului
            email_content = f"""
Subiect: {msg.get('Subject', 'Fără subiect')}
De la: {msg.get('From', 'Fără expeditor')}
Către: {msg.get('To', 'Fără destinatar')}
Data: {msg.get('Date', 'Fără dată')}

"""
            
            # Adaugă corpul email-ului
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain" and part.get_content_disposition() != 'attachment':
                        email_content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                email_content += msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            # Salvează email-ul
            with open(os.path.join(email_dir, 'email.txt'), 'w', encoding='utf-8') as f:
                f.write(email_content)
            
            # Salvează atașamentele
            attachment_count = 0
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        # Decodifică numele fișierului
                        if filename.startswith('=?'):
                            decoded_filename = email.header.decode_header(filename)[0]
                            if isinstance(decoded_filename[0], bytes):
                                filename = decoded_filename[0].decode(decoded_filename[1] or 'utf-8')
                            else:
                                filename = decoded_filename[0]
                        
                        filepath = os.path.join(email_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        
                        attachment_count += 1
                        color_print(f"✓ Atașament salvat: {filepath}", 'success')
            
            color_print(f"✓ Email descărcat în directorul: {email_dir}", 'success')
            color_print(f"✓ {attachment_count} atașamente salvate", 'success')
    
    except Exception as e:
        color_print(f"✗ EROARE la descărcare: {e}", 'error')

def send_email_text_only(email_addr, password):
    """Trimite un email doar cu text."""
    print_section("📤 TRIMITERE EMAIL (DOAR TEXT)")
    
    try:
        # Obține detalii email
        to_addr = color_input("Destinatar: ")
        subject = color_input("Subiect: ")
        reply_to = color_input("Reply-to (opțional): ")
        
        color_print("\nIntrodu corpul email-ului (linie goală pentru a termina):", 'info')
        body_lines = []
        while True:
            line = color_input("> ")
            if not line:
                break
            body_lines.append(line)
        body = '\n'.join(body_lines)
        
        # Creează mesajul
        msg = MIMEMultipart()
        msg['From'] = email_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        
        if reply_to:
            msg['Reply-To'] = reply_to
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Trimite email-ul
        send_email(msg, email_addr, password)
        
    except Exception as e:
        color_print(f"✗ EROARE: {e}", 'error')

def send_email_with_attachment(email_addr, password):
    """Trimite un email cu atașament."""
    print_section("📤 TRIMITERE EMAIL (CU ATAȘAMENT)")
    
    try:
        # Obține detalii email
        to_addr = color_input("Destinatar: ")
        subject = color_input("Subiect: ")
        reply_to = color_input("Reply-to (opțional): ")
        
        color_print("\nIntrodu corpul email-ului (linie goală pentru a termina):", 'info')
        body_lines = []
        while True:
            line = color_input("> ")
            if not line:
                break
            body_lines.append(line)
        body = '\n'.join(body_lines)
        
        # Obține calea către atașament
        attachment_path = color_input("Calea către fișierul de atașat: ")
        
        if not os.path.exists(attachment_path):
            color_print("✗ Fișierul nu există.", 'error')
            return
        
        # Creează mesajul
        msg = MIMEMultipart()
        msg['From'] = email_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        
        if reply_to:
            msg['Reply-To'] = reply_to
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Adaugă atașamentul
        filename = os.path.basename(attachment_path)
        
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        
        msg.attach(part)
        
        # Trimite email-ul
        send_email(msg, email_addr, password)
        
    except Exception as e:
        color_print(f"✗ EROARE: {e}", 'error')

def send_email(msg, email_addr, password):
    """Trimite un email prin SMTP."""
    try:
        # Creează context SSL
        context = ssl.create_default_context()
        
        # Conectare la SMTP
        with smtplib.SMTP(GMAIL_SMTP_SERVER, GMAIL_SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(email_addr, password)
            
            # Trimite email-ul
            text = msg.as_string()
            server.sendmail(email_addr, msg['To'], text)
            
            color_print("✓ Email trimis cu succes!", 'success')
            print_result("Destinatar", msg['To'])
            print_result("Subiect", msg['Subject'])
            
            if 'Reply-To' in msg:
                print_result("Reply-To", msg['Reply-To'])
    
    except smtplib.SMTPAuthenticationError:
        color_print("✗ EROARE: Autentificare eșuată.", 'error')
        color_print("ℹ  Folosește un App Password pentru Gmail.", 'warning')
    except smtplib.SMTPException as e:
        color_print(f"✗ EROARE SMTP: {e}", 'error')
    except Exception as e:
        color_print(f"✗ EROARE: {e}", 'error')

def show_main_menu():
    """Afișează meniul principal."""
    print_header("📧 CLIENT EMAIL GMAIL")
    
    color_print("📝 Meniu principal:", 'info')
    color_print("  1. Primește email-uri (POP3)", 'info')
    color_print("  2. Primește email-uri (IMAP)", 'info')
    color_print("  3. Descarcă email cu atașamente", 'info')
    color_print("  4. Trimite email (doar text)", 'info')
    color_print("  5. Trimite email (cu atașament)", 'info')
    color_print("  6. Ieșire", 'info')
    color_print("──────────────────────────────────────────────────", 'info')

def show_gmail_setup_info():
    """Afișează informații despre configurarea Gmail."""
    print_section("⚙️ CONFIGURARE GMAIL")
    
    color_print("Pentru a folosi acest client cu Gmail, trebuie să:", 'info')
    color_print("", 'white')
    color_print("1. Activezi IMAP/POP3 în setările Gmail:", 'yellow')
    color_print("   - Gmail → Setări → Forwarding and POP/IMAP", 'result')
    color_print("   - Activează IMAP și/sau POP3", 'result')
    color_print("", 'white')
    color_print("2. Generezi un App Password:", 'yellow')
    color_print("   - Google Account → Security", 'result')
    color_print("   - 2-Step Verification (activează dacă nu e deja)", 'result')
    color_print("   - App passwords", 'result')
    color_print("   - Generează o parolă nouă pentru 'Mail'", 'result')
    color_print("", 'white')
    color_print("ℹ  Folosește App Password în loc de parola normală!", 'warning')

def main():
    """Funcția principală."""
    
    print_header("📧 CLIENT EMAIL GMAIL")
    color_print("📝 Aplicație pentru primire și trimitere email-uri prin Gmail", 'info')
    
    # Afișează informații despre configurare
    show_gmail_setup_info()
    
    # Obține credențialele
    email_addr, password = get_credentials()
    
    if not email_addr or not password:
        color_print("✗ Credențiale invalide!", 'error')
        return
    
    color_print(f"✓ Conectat ca: {email_addr}", 'success')
    
    while True:
        try:
            show_main_menu()
            choice = color_input("\nAlege o opțiune: ")
            
            if choice == '1':
                list_emails_pop3(email_addr, password)
            elif choice == '2':
                list_emails_imap(email_addr, password)
            elif choice == '3':
                download_email_with_attachments(email_addr, password)
            elif choice == '4':
                send_email_text_only(email_addr, password)
            elif choice == '5':
                send_email_with_attachment(email_addr, password)
            elif choice == '6':
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
