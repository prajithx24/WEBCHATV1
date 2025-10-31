import socket
import threading
from getpass import getpass

SERVER_HOST = input("Enter server IP (e.g., 127.0.0.1): ")
SERVER_PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((SERVER_HOST, SERVER_PORT))
except Exception as e:
    print("[-] Connection failed:", e)
    exit()

def authenticate():
    server_prompt = client.recv(1024).decode()
    if server_prompt != "AUTH_MODE":
        print("❌ Unexpected server response.")
        exit()

    print("🔐 Choose authentication mode:")
    print("1. Login")
    print("2. Signup")
    choice = input("Enter choice [1/2]: ").strip()

    if choice == "2":
        client.sendall("SIGNUP".encode())
        username = input("Choose username: ")
        password = getpass("Choose password: ")
        creds = f"{username}||{password}"
        client.sendall(creds.encode())
        response = client.recv(1024).decode()
        if response.startswith("SIGNUP_FAIL"):
            print(f"❌ Signup failed: {response.split('||')[1]}")
            client.close()
            exit()
        else:
            print("✅ Signup successful.")
    else:
        client.sendall("LOGIN".encode())
        username = input("Username: ")
        password = getpass("Password: ")
        creds = f"{username}||{password}"
        client.sendall(creds.encode())
        result = client.recv(1024).decode()
        if result.startswith("AUTH_FAIL"):
            print(f"❌ Login failed: {result.split('||')[1]}")
            client.close()
            exit()
        elif result == "AUTH_SUCCESS":
            print(f"✅ Authenticated as {username}")

def receive_messages():
    while True:
        try:
            msg = client.recv(1024)
            if not msg:
                break
            print("\n" + msg.decode())
        except Exception as e:
            print("[ERROR] Receiving message failed:", e)
            break

def send_messages():
    while True:
        msg = input()
        if msg.lower() == "/exit":
            client.close()
            break
        try:
            client.sendall(msg.encode())
        except Exception as e:
            print("[ERROR] Sending message failed:", e)
            break

# Start authentication process.
authenticate()

# Start a thread to continuously receive messages.
recv_thread = threading.Thread(target=receive_messages, daemon=True)
recv_thread.start()

# Run the send_messages loop in the main thread.
send_messages()
