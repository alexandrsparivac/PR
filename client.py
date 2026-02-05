import socket
import threading
import json
import sys

HOST = '127.0.0.1'
PORT = 65432

running = True


def send_message(client_socket, msg_type, data):
    """Trimite un mesaj JSON către server."""
    message = json.dumps({"type": msg_type, "data": data})
    client_socket.sendall(message.encode('utf-8'))


def receive_messages(client_socket):
    """Primește mesaje de la server și le afișează."""
    global running
    while running:
        try:
            data = client_socket.recv(4096)
            if not data:
                print("\n[INFO] Serverul a închis conexiunea.")
                running = False
                break
            
            msg = json.loads(data.decode('utf-8'))
            msg_type = msg['type']
            msg_data = msg['data']
            
            if msg_type == 'registered':
                print(f"\n[OK] Înregistrat ca: {msg_data['nickname']}")
                print(f"[INFO] IP-ul tău: {msg_data['ip']}:{msg_data['port']}")
            
            elif msg_type == 'message':
                if msg_data['type'] == 'broadcast':
                    print(f"\n[GENERAL] {msg_data['from']}: {msg_data['message']}")
                elif msg_data['type'] == 'private':
                    print(f"\n[PRIVAT de la {msg_data['from']}]: {msg_data['message']}")
                elif msg_data['type'] == 'private_sent':
                    print(f"\n[PRIVAT] {msg_data['from']}: {msg_data['message']}")
            
            elif msg_type == 'notification':
                print(f"\n[NOTIFICARE] {msg_data['message']}")
            
            elif msg_type == 'user_list':
                print("\n=== UTILIZATORI CONECTAȚI ===")
                for i, user in enumerate(msg_data['users'], 1):
                    print(f"  {i}. {user}")
                print("=============================")
            
            elif msg_type == 'info':
                print(f"\n=== INFORMAȚIILE TALE ===")
                print(f"  Nickname: {msg_data['nickname']}")
                print(f"  IP: {msg_data['ip']}")
                print(f"  Port: {msg_data['port']}")
                print("==========================")
            
            elif msg_type == 'error':
                print(f"\n[EROARE] {msg_data['message']}")
            
            print("\n> ", end="", flush=True)
        
        except json.JSONDecodeError:
            print("\n[EROARE] Mesaj invalid de la server.")
        except ConnectionResetError:
            print("\n[INFO] Conexiunea a fost întreruptă de server.")
            running = False
            break
        except OSError:
            break
        except Exception as e:
            if running:
                print(f"\n[EROARE] {e}")
            break


def show_menu():
    """Afișează meniul principal."""
    print("\n========== MENIU ==========")
    print("  1. Trimite mesaj la toți")
    print("  2. Trimite mesaj privat")
    print("  3. Vezi utilizatori conectați")
    print("  4. Vezi informațiile tale (IP)")
    print("  5. Ieșire")
    print("=============================")


def main():
    global running
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
        print(f"[CONECTAT] Conectat la server {HOST}:{PORT}")
        
        # Cere nickname
        nickname = input("Introdu nickname-ul tău: ").strip()
        while not nickname:
            nickname = input("Nickname-ul nu poate fi gol. Introdu nickname-ul: ").strip()
        
        send_message(client_socket, 'register', {'nickname': nickname})
        
        # Pornește thread-ul pentru primirea mesajelor
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True
        receive_thread.start()
        
        # Așteaptă puțin pentru confirmare
        import time
        time.sleep(0.5)
        
        while running:
            show_menu()
            choice = input("> ").strip()
            
            if choice == '1':
                message = input("Mesaj pentru toți: ").strip()
                if message:
                    send_message(client_socket, 'broadcast', {'message': message})
            
            elif choice == '2':
                # Mai întâi arată lista de utilizatori
                send_message(client_socket, 'list_users', {})
                import time
                time.sleep(0.3)
                
                target = input("Către cine (nickname): ").strip()
                if target:
                    message = input("Mesaj privat: ").strip()
                    if message:
                        send_message(client_socket, 'private', {'to': target, 'message': message})
            
            elif choice == '3':
                send_message(client_socket, 'list_users', {})
            
            elif choice == '4':
                send_message(client_socket, 'my_info', {})
            
            elif choice == '5':
                print("[INFO] Deconectare...")
                running = False
                break
            
            else:
                print("[EROARE] Opțiune invalidă!")
    
    except ConnectionRefusedError:
        print(f"[EROARE] Nu s-a putut conecta la server {HOST}:{PORT}")
        print("[INFO] Asigură-te că serverul este pornit.")
    except KeyboardInterrupt:
        print("\n[INFO] Deconectare...")
        running = False
    except Exception as e:
        print(f"[EROARE] {e}")
    finally:
        running = False
        client_socket.close()
        print("[DECONECTAT] Conexiunea a fost închisă.")


if __name__ == "__main__":
    main()
