import socket
import threading
import sys

host = "127.0.0.1"
port = 12345

mode = input("Enter mode (tcp/udp): ").strip().lower()
nickname = input("Nickname: ").strip()

if not nickname:
    print("Nickname cannot be empty")
    sys.exit(1)

running = True

if mode == "tcp":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except:
        print("Could not connect to server")
        sys.exit(1)

    def receive():
        global running
        while running:
            try:
                msg = client.recv(1024).decode()
                if msg == "NICK":
                    client.send(nickname.encode())
                elif msg:
                    if "Connection rejected" in msg or "rejected" in msg:
                        print(msg)
                        running = False
                        break
                    print(msg)
                else:
                    running = False
                    break
            except:
                running = False
                break
        client.close()

    def write():
        global running
        while running:
            try:
                msg = input()
                if msg == "!quit" or not running:
                    running = False
                    break
                client.send(f"{nickname}: {msg}".encode())
            except:
                running = False
                break

elif mode == "udp":
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        client.sendto(f"NICK:{nickname}".encode(), (host, port))
    except:
        print("Failed to connect to server")
        sys.exit(1)

    def receive():
        global running
        while running:
            try:
                msg, _ = client.recvfrom(1024)
                msg = msg.decode()
                if msg:
                    if "Connection rejected" in msg or "rejected" in msg:
                        print(msg)
                        running = False
                        break
                    print(msg)
            except:
                running = False
                break

    def write():
        global running
        while running:
            try:
                msg = input()
                if msg == "!quit" or not running:
                    running = False
                    break
                message = f"{nickname}: {msg}"
                client.sendto(message.encode(), (host, port))
            except:
                running = False
                break

else:
    print("Invalid mode. Use 'tcp' or 'udp'")
    sys.exit(1)

receive_thread = threading.Thread(target=receive, daemon=True)
write_thread = threading.Thread(target=write, daemon=True)

receive_thread.start()
write_thread.start()

try:
    write_thread.join()
except KeyboardInterrupt:
    running = False
    print("\nDisconnecting...")

client.close()