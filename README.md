# Dual-Mode Multi-Client Chatroom (TCP/UDP)

This is a Python-based terminal chatroom application that allows multiple clients to connect to a central server **using either TCP or UDP**, but not both simultaneously. The server automatically locks to the protocol of the first client to ensure consistent communication.

## Features

- Supports **either TCP or UDP**, dynamically locked at runtime.
- Multi-client chat with unique nicknames.
- Graceful connection rejection if protocol doesn't match.
- Broadcast system with clean disconnection handling.
- Threaded client handling for smooth performance.
- Command-line interface, works on any system with Python installed.

## File Structure

- `server.py`: The main server that accepts clients using either TCP or UDP.
- `client.py`: A terminal-based client that connects to the server using user-selected protocol.

## How It Works

### TCP Mode
- The server listens for TCP connections.
- Each client sends their nickname and then participates in the chat.
- Messages are broadcasted to all connected TCP clients except the sender.

### UDP Mode
- The server listens for UDP datagrams.
- Each client sends their nickname prefixed with `NICK:` to join.
- Messages are broadcasted to all known UDP addresses except the sender.

The server **locks to the first mode (TCP/UDP)** chosen by the first client. Clients of the other protocol will be rejected with a clear message.


## How to Run

### 1. Start the server:
```bash
python server.py
```

### 2. Run a client (choose TCP or UDP):
```bash
python client.py
```

You will be prompted to enter:
- `tcp` or `udp` for connection mode
- Your nickname

## Exit

- Type `!quit` to leave the chat gracefully.
- On forced exit (e.g., Ctrl+C), connections are closed automatically.


## Requirements

- Python 3.x
- No external libraries required (uses `socket` and `threading`)
