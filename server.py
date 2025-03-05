import sqlite3
import socket
import json
import threading
import auth
import wallet
import transaction
import database

DB_FILE = "wallets.db"
HOST = "127.0.0.1"
PORT = 8000

def handle_request(client_socket):
    """Handles client requests safely and returns responses."""
    try:
        request = client_socket.recv(1024).decode().strip()
        
        if not request:
            client_socket.send(json.dumps({"error": "Empty request"}).encode())
            return
        
        try:
            request_data = json.loads(request)
        except json.JSONDecodeError:
            client_socket.send(json.dumps({"error": "Invalid JSON format"}).encode())
            return

        action = request_data.get("action")
        response = {}

        if action == "register":
            username = request_data.get("username")
            password = request_data.get("password")
            if not username or not password:
                response = {"error": "Username and password are required"}
            else:
                success = auth.register(username, password)
                response = {"success": success, "message": "Registration successful" if success else "Registration failed"}

        elif action == "login":
            username = request_data.get("username")
            password = request_data.get("password")
            if not username or not password:
                response = {"error": "Username and password are required"}
            else:
                success = auth.login(username, password)
                response = {"success": success, "message": "Login successful" if success else "Invalid username or password"}

        elif action == "get_wallet":
            username = request_data.get("username")
            if not username:
                response = {"error": "Username is required"}
            else:
                wallet_data = wallet.get_wallet(username)
                response = wallet_data if wallet_data else {"error": "Wallet not found"}

        elif action == "send_tokens":
            sender = request_data.get("sender_username")
            receiver = request_data.get("receiver_username")
            amount = request_data.get("amount")

            if not sender or not receiver or amount is None:
                response = {"error": "Missing transaction details"}
            else:
                success, message = transaction.create_transaction(sender, receiver, amount)
                response = {"message": message, "success": success}

        else:
            response = {"error": "Invalid request"}

        client_socket.send(json.dumps(response).encode())

    except sqlite3.OperationalError as e:
        response = {"error": f"Database error: {str(e)}"}
        client_socket.send(json.dumps(response).encode())

    except Exception as e:
        response = {"error": f"Server error: {str(e)}"}
        client_socket.send(json.dumps(response).encode())

    finally:
        client_socket.close()

def start_server():
    """Starts the wallet server with threading to handle multiple clients."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, _ = server_socket.accept()
        client_thread = threading.Thread(target=handle_request, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    print("🛠 Initializing database...")
    database.init_db()  # Ensure database is initialized before starting
    start_server()
