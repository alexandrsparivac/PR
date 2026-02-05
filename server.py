import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 65432

# Dict: nickname -> {socket, address}
clients = {}
clients_lock = threading.Lock()


def send_to_client(client_socket, msg_type, data):
    """Trimite un mesaj JSON către un client."""
    message = json.dumps({"type": msg_type, "data": data})
    try:
        client_socket.sendall(message.encode('utf-8'))
    except:
        pass


def broadcast(msg_type, data, exclude_nickname=None):
    """Trimite mesajul către toți clienții conectați."""
    with clients_lock:
        for nickname, info in list(clients.items()):
            if nickname != exclude_nickname:
                send_to_client(info['socket'], msg_type, data)


def get_user_list():
    """Returnează lista de utilizatori conectați."""
    with clients_lock:
        return list(clients.keys())


def handle_client(client_socket, address):
    """Gestionează comunicarea cu un client individual."""
    nickname = None
    
    try:
        # Primește nickname-ul
        data = client_socket.recv(1024)
        if not data:
            return
        
        msg = json.loads(data.decode('utf-8'))
        if msg['type'] == 'register':
            nickname = msg['data']['nickname']
            
            with clients_lock:
                if nickname in clients:
                    send_to_client(client_socket, 'error', {'message': 'Nickname-ul este deja folosit!'})
                    client_socket.close()
                    return
                clients[nickname] = {'socket': client_socket, 'address': address}
            
            print(f"[CONEXIUNE NOUĂ] {nickname} ({address}) s-a conectat.")
            send_to_client(client_socket, 'registered', {'nickname': nickname, 'ip': address[0], 'port': address[1]})
            broadcast('notification', {'message': f'{nickname} s-a alăturat chat-ului!'}, exclude_nickname=nickname)
        
        # Bucla principală pentru mesaje
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            
            msg = json.loads(data.decode('utf-8'))
            msg_type = msg['type']
            
            if msg_type == 'broadcast':
                print(f"[BROADCAST] {nickname}: {msg['data']['message']}")
                broadcast('message', {'from': nickname, 'message': msg['data']['message'], 'type': 'broadcast'})
            
            elif msg_type == 'private':
                target = msg['data']['to']
                message = msg['data']['message']
                print(f"[PRIVAT] {nickname} -> {target}: {message}")
                
                with clients_lock:
                    if target in clients:
                        send_to_client(clients[target]['socket'], 'message', 
                                      {'from': nickname, 'message': message, 'type': 'private'})
                        send_to_client(client_socket, 'message', 
                                      {'from': f'Tu -> {target}', 'message': message, 'type': 'private_sent'})
                    else:
                        send_to_client(client_socket, 'error', {'message': f'Utilizatorul {target} nu există!'})
            
            elif msg_type == 'list_users':
                users = get_user_list()
                send_to_client(client_socket, 'user_list', {'users': users})
            
            elif msg_type == 'my_info':
                with clients_lock:
                    info = clients.get(nickname)
                    if info:
                        send_to_client(client_socket, 'info', 
                                      {'nickname': nickname, 'ip': info['address'][0], 'port': info['address'][1]})
    
    except ConnectionResetError:
        print(f"[DECONECTARE] {nickname or address} s-a deconectat brusc.")
    except json.JSONDecodeError:
        print(f"[EROARE] Mesaj invalid de la {nickname or address}")
    except Exception as e:
        print(f"[EROARE] {nickname or address}: {e}")
    finally:
        if nickname:
            with clients_lock:
                if nickname in clients:
                    del clients[nickname]
            broadcast('notification', {'message': f'{nickname} a părăsit chat-ul.'})
            print(f"[DECONECTAT] {nickname} a închis conexiunea.")
        client_socket.close()


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
            for nickname, info in clients.items():
                info['socket'].close()
        server_socket.close()


if __name__ == "__main__":
    main()
