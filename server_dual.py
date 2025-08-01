import socket
import threading

host = "127.0.0.1"
port = 12345

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tcp_server.bind((host, port))
tcp_server.listen()

tcp_clients = []
tcp_nicknames = {}
udp_clients = set()
udp_nicknames = {}
lock = threading.Lock()
first_protocol = None

def broadcast(message, sender=None, sender_addr=None):
    with lock:
        if first_protocol == "tcp":
            for client in tcp_clients[:]:
                try:
                    if client != sender:
                        client.send(message.encode())
                except:
                    tcp_clients.remove(client)
                    if client in tcp_nicknames:
                        del tcp_nicknames[client]
        
        elif first_protocol == "udp":
            for addr in list(udp_clients):
                try:
                    if addr != sender_addr:
                        udp_server.sendto(message.encode(), addr)
                except:
                    udp_clients.discard(addr)
                    if addr in udp_nicknames:
                        del udp_nicknames[addr]

def handle_tcp_client(client):
    try:
        client.send("NICK".encode())
        nick = client.recv(1024).decode().strip()
        if not nick:
            return
        
        with lock:
            tcp_nicknames[client] = nick
        
        broadcast(f"{nick} joined the chat", sender=client)
        
        while True:
            msg = client.recv(1024).decode().strip()
            if not msg:
                break
            broadcast(msg, sender=client)
    except:
        pass
    finally:
        with lock:
            if client in tcp_clients:
                tcp_clients.remove(client)
            if client in tcp_nicknames:
                nick = tcp_nicknames[client]
                del tcp_nicknames[client]
                broadcast(f"{nick} left the chat", sender=client)
        client.close()

def tcp_accept():
    global first_protocol
    while True:
        try:
            client, addr = tcp_server.accept()
            
            with lock:
                if first_protocol is None:
                    first_protocol = "tcp"
                    print("Server locked to TCP mode")
                elif first_protocol != "tcp":
                    client.send("Server is in UDP mode. Connection rejected.".encode())
                    client.close()
                    continue
                
                tcp_clients.append(client)
            
            threading.Thread(target=handle_tcp_client, args=(client,), daemon=True).start()
        except:
            break

def udp_receive():
    global first_protocol
    while True:
        try:
            msg, addr = udp_server.recvfrom(1024)
            msg = msg.decode().strip()
            
            with lock:
                if first_protocol is None:
                    first_protocol = "udp"
                    print("Server locked to UDP mode")
                elif first_protocol != "udp":
                    udp_server.sendto("Server is in TCP mode. Connection rejected.".encode(), addr)
                    continue
            
            if msg.startswith("NICK:"):
                nick = msg.split(":", 1)[1].strip()
                if addr not in udp_clients:
                    with lock:
                        udp_clients.add(addr)
                        udp_nicknames[addr] = nick
                    broadcast(f"{nick} joined the chat", sender_addr=addr)
            else:
                if addr in udp_clients:
                    broadcast(msg, sender_addr=addr)
        except:
            pass

print("Server starting...")
tcp_thread = threading.Thread(target=tcp_accept, daemon=True)
udp_thread = threading.Thread(target=udp_receive, daemon=True)

tcp_thread.start()
udp_thread.start()

try:
    tcp_thread.join()
except KeyboardInterrupt:
    print("\nServer shutting down...")
    tcp_server.close()
    udp_server.close()