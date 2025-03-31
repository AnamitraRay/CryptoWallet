import socket
import json
import auth
import transaction
from database import init_server_db
import sqlite3
from database import SERVER_DB

HOST = "127.0.0.1"
PORT = 8000

def get_balance(username):
    """Fetches the wallet balance for a user."""
    conn = sqlite3.connect(SERVER_DB)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT balance FROM wallets 
            WHERE wallet_id = (SELECT wallet_id FROM users WHERE username=?)
        """, (username,))
        row = cursor.fetchone()
        
        if row:
            return True, row[0]  # Success, return balance
        return False, "User wallet not found."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    finally:
        conn.close()

def handle_request(client_socket):
    try:
        request = json.loads(client_socket.recv(4096).decode())
        action = request.get("action")
        response = {}

        if action == "register":
            response["success"], response["message"] = auth.register(request["username"], request["password"], request["public_key"])

        elif action == "login":
            response["success"], response["message"] = auth.login(request["username"], request["password"])

        elif action == "check_balance":
            success, balance = get_balance(request["username"])
            response["success"] = success
            if success:
                response["balance"] = balance
            else:
                response["message"] = balance  # Send error message

        elif action == "send_tokens":  # Added missing transaction handling
            success, message = transaction.create_transaction(
                request["sender_username"],
                request["receiver_username"],
                request["amount"],
                request["signature"]
            )
            response["success"] = success
            response["message"] = message  # Always include "message"

        else:
            response["success"] = False
            response["message"] = "Invalid action."

        client_socket.send(json.dumps(response).encode())

    except Exception as e:
        error_response = {"success": False, "message": f"Server error: {str(e)}"}
        client_socket.send(json.dumps(error_response).encode())

    finally:
        client_socket.close()

# Ensure database is initialized before starting the server
init_server_db()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Server running on {HOST}:{PORT}")

while True:
    client_socket, _ = server_socket.accept()
    handle_request(client_socket)
