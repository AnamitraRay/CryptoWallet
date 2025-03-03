import socket
import json

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

def send_request(action, data={}):
    """Sends request to the server and returns the response."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    
    request_data = {"action": action}
    request_data.update(data)

    client_socket.send(json.dumps(request_data).encode())
    response = json.loads(client_socket.recv(1024).decode())
    client_socket.close()

    return response

def main():
    while True:
        print("\n1. Create Wallet")
        print("2. Get Wallet Info")
        print("3. Send Tokens")
        print("4. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            response = send_request("create_wallet")
            print(response)

        elif choice == "2":
            wallet_address = input("Enter wallet address: ")
            response = send_request("get_wallet", {"wallet_address": wallet_address})
            print(response)

        elif choice == "3":
            sender_wallet = input("Enter sender wallet address: ")
            receiver_wallet = input("Enter receiver wallet address: ")
            amount = float(input("Enter amount: "))
            response = send_request("send_tokens", {
                "sender_wallet": sender_wallet,
                "receiver_wallet": receiver_wallet,
                "amount": amount
            })
            print(response)

        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
