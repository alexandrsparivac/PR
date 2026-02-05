import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

clients = []
clients_lock = threading.Lock()


def broadcast(message, sender_socket=None):
    """Trimite mesajul către toți clienții conectați."""
    with clients_lock:
        for client in clients[:]:
            try:
                client.sendall(message)
            except:
                clients.remove(client)


def handle_client(client_socket, address):
    """Gestionează comunicarea cu un client individual."""
    print(f"[CONEXIUNE NOUĂ] {address} s-a conectat.")
    
    with clients_lock:
        clients.append(client_socket)
    
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8')
            print(f"[{address}] {message}")
            
            broadcast_msg = f"[{address}]: {message}".encode('utf-8')
            broadcast(broadcast_msg)
    
    except ConnectionResetError:
        print(f"[DECONECTARE] {address} s-a deconectat brusc.")
    except Exception as e:
        print(f"[EROARE] {address}: {e}")
    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        print(f"[DECONECTAT] {address} a închis conexiunea.")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    
    print(f"[SERVER PORNIT] Ascultă pe {HOST}:{PORT}")
    print("[INFO] Apasă Ctrl+C pentru a opri serverul.")
    
    try:
        while True:
            client_socket, address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, address))
            thread.daemon = True
            thread.start()
            print(f"[CONEXIUNI ACTIVE] {threading.active_count() - 1}")
    
    except KeyboardInterrupt:
        print("\n[SERVER OPRIT] Închidere...")
    finally:
        with clients_lock:
            for client in clients:
                client.close()
        server_socket.close()


if __name__ == "__main__":
    main()
