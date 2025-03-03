import sqlite3
import socket
import json
import wallet
import transaction
import database 

DB_FILE = "wallets.db"
HOST = "127.0.0.1" 
PORT = 8000

def handle_request(client_socket):
    """Handles client requests safely and returns responses."""
    try:
        request = client_socket.recv(1024).decode()
        request_data = json.loads(request)

        action = request_data.get("action")
        response = {}

        if action == "create_wallet":
            wallet_address = wallet.create_wallet()
            response = {"wallet_address": wallet_address, "message": "Wallet created successfully."}

        elif action == "get_wallet":
            wallet_address = request_data.get("wallet_address")
            wallet_data = wallet.get_wallet(wallet_address)
            response = wallet_data if wallet_data else {"error": "Wallet not found"}

        elif action == "send_tokens":
            sender_wallet = request_data["sender_wallet"]
            receiver_wallet = request_data["receiver_wallet"]
            amount = request_data["amount"]

            success, message = transaction.create_transaction(sender_wallet, receiver_wallet, amount)
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
    """Starts the wallet server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, _ = server_socket.accept()
        handle_request(client_socket)

if __name__ == "__main__":
    print("Initializing database...")
    database.init_db() 
    start_server()
