import socket
import json
import auth
import wallet
import transaction

SERVER_HOST = "127.0.0.1"  
SERVER_PORT = 8000         

def send_request(action, data={}):
    """Sends request to the server and returns the response."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        request_data = {"action": action}
        request_data.update(data)

        client_socket.send(json.dumps(request_data).encode())
        response = json.loads(client_socket.recv(1024).decode())
        client_socket.close()

        return response

    except ConnectionRefusedError:
        print("Could not connect to the server. Is it running?")
        return {"error": "Server unavailable"}

def main():
    while True:
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            response = send_request("login", {"username": username, "password": password})
            if response.get("success"):
                user_menu(username)
            else:
                print("Invalid username or password.")

        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            response = send_request("register", {"username": username, "password": password})
            print(response.get("message", "Registration failed."))

        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

def user_menu(username):
    while True:
        print("\n1. Send Tokens")
        print("2. Check Wallet")
        print("3. Logout")
        choice = input("Enter choice: ")

        if choice == "1":
            receiver = input("Enter receiver username: ")
            amount = float(input("Enter amount: "))
            response = send_request("send_tokens", {
                "sender_username": username,
                "receiver_username": receiver,
                "amount": amount
            })
            print(response.get("message", "Transaction failed."))

        elif choice == "2":
            response = send_request("get_wallet", {"username": username})
            print(response)

        elif choice == "3":
            break

if __name__ == "__main__":
    main()
