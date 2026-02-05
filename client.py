import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 65432


def receive_messages(client_socket):
    """Primește mesaje de la server și le afișează."""
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\n[INFO] Serverul a închis conexiunea.")
                break
            message = data.decode('utf-8')
            print(f"\n{message}")
            print("Tu: ", end="", flush=True)
        except ConnectionResetError:
            print("\n[INFO] Conexiunea a fost întreruptă de server.")
            break
        except OSError:
            break
        except Exception as e:
            print(f"\n[EROARE] {e}")
            break


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
        print(f"[CONECTAT] Conectat la server {HOST}:{PORT}")
        print("[INFO] Scrie mesaje și apasă Enter pentru a le trimite.")
        print("[INFO] Scrie 'exit' pentru a te deconecta.\n")
        
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True
        receive_thread.start()
        
        while True:
            message = input("Tu: ")
            
            if message.lower() == 'exit':
                print("[INFO] Deconectare...")
                break
            
            if message:
                client_socket.sendall(message.encode('utf-8'))
    
    except ConnectionRefusedError:
        print(f"[EROARE] Nu s-a putut conecta la server {HOST}:{PORT}")
        print("[INFO] Asigură-te că serverul este pornit.")
    except KeyboardInterrupt:
        print("\n[INFO] Deconectare...")
    except Exception as e:
        print(f"[EROARE] {e}")
    finally:
        client_socket.close()
        print("[DECONECTAT] Conexiunea a fost închisă.")


if __name__ == "__main__":
    main()
