import socket
import threading
from utils.auth_manager import authenticate_user, signup_user

HOST = '0.0.0.0'
PORT = 12345

clients = {}
usernames = {}

def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            try:
                client.sendall(message)
            except:
                client.close()
                clients.pop(client, None)

def handle_client(conn, addr):
    try:
        conn.sendall("AUTH_MODE".encode())
        mode = conn.recv(1024).decode()
        
        conn.sendall("SEND_CREDENTIALS".encode())
        creds = conn.recv(1024).decode().split("||")
        if len(creds) != 2:
            conn.sendall("AUTH_FAIL||Invalid credential format.".encode())
            conn.close()
            return
        username, password = creds

        if mode == "LOGIN":
            status, msg = authenticate_user(username, password)
            if not status:
                conn.sendall(f"AUTH_FAIL||{msg}".encode())
                conn.close()
                return
            conn.sendall("AUTH_SUCCESS".encode())
        elif mode == "SIGNUP":
            status, msg = signup_user(username, password)
            if not status:
                conn.sendall(f"SIGNUP_FAIL||{msg}".encode())
                conn.close()
                return
            conn.sendall("SIGNUP_SUCCESS".encode())
        else:
            conn.sendall("AUTH_FAIL||Unknown mode.".encode())
            conn.close()
            return

        usernames[conn] = username
        clients[conn] = addr
        print(f"[+] {username} connected from {addr}")

        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            formatted = f"{username}: {msg.decode()}"
            print(f"[{addr}] {formatted}")
            broadcast(formatted.encode(), conn)

    except Exception as e:
        print(f"[-] Error with {addr}: {e}")
    finally:
        conn.close()
        clients.pop(conn, None)
        print(f"[-] {addr} disconnected.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[+] Server listening on {HOST}:{PORT}")
    
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
