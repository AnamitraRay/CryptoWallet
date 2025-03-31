import socket
import json
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import sqlite3
from rsa_keys import generate_and_store_rsa_keys, load_private_key
from database import CLIENT_DB
from database import init_client_db  # Import the function

# Initialize the client database before any operation
init_client_db()

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

def send_request(request):
    """Sends a request to the server and returns the response."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    
    client_socket.send(json.dumps(request).encode())
    response = json.loads(client_socket.recv(4096).decode())
    
    client_socket.close()
    return response

def register():
    """Handles user registration, including key pair generation and storage."""
    username = input("Enter username: ")
    password = input("Enter password: ")

    generate_and_store_rsa_keys(username)
    
    conn = sqlite3.connect(CLIENT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT public_key FROM keys WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        public_key = row[0]
        request = {"action": "register", "username": username, "password": password, "public_key": public_key}
        response = send_request(request)
        print(response["message"])
    else:
        print("Failed to generate public key.")

def login():
    """Handles user login."""
    username = input("Enter username: ")
    password = input("Enter password: ")

    request = {"action": "login", "username": username, "password": password}
    response = send_request(request)
    
    print(response["message"])
    if response["success"]:
        return username
    return None

def send_tokens(username):
    """Handles sending tokens by signing transactions locally."""
    receiver = input("Enter receiver's username: ")

    try:
        amount = float(input("Enter amount to send: "))
        if amount <= 0:
            print("Amount must be positive.")
            return
    except ValueError:
        print("Invalid amount. Please enter a valid number.")
        return

    private_key = load_private_key(username)
    if not private_key:
        print("Private key not found. Ensure you're using the correct client.")
        return

    transaction_data = f"{username}-{receiver}-{amount}"
    hash_obj = SHA256.new(transaction_data.encode())

    try:
        signature = pkcs1_15.new(private_key).sign(hash_obj).hex()
    except ValueError:
        print("Error in signing transaction.")
        return

    request = {
        "action": "send_tokens",
        "sender_username": username,
        "receiver_username": receiver,
        "amount": amount,
        "signature": signature
    }

    response = send_request(request)
    print(response["message"])

def check_balance(username):
    """Requests the balance of the user's wallet from the server."""
    request = {"action": "check_balance", "username": username}
    response = send_request(request)
    if "balance" in response:
        print(f"Your current balance: {response['balance']}")
    else:
        print("Failed to fetch balance:", response.get("message", "Unknown error"))

def main():
    """Main client interface for interacting with the server."""
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            register()
        elif choice == "2":
            username = login()
            if username:
                while True:
                    print("\n1. Send Tokens\n2. Check Balance\n3. Logout")
                    action = input("Enter choice: ")
                    
                    if action == "1":
                        send_tokens(username)
                    elif action == "2":
                        check_balance(username)
                    elif action == "3":
                        print("Logging out...")
                        break
                    else:
                        print("Invalid option.")
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
