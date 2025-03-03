from wallet import create_wallet, get_wallet
from database import init_db

init_db()

if __name__ == "__main__":
    while True:
        print("\nCrypto Wallet System with RSA Keys")
        print("1. Create Wallet (RSA)")
        print("2. Retrieve Wallet")
        print("3. Exit")
        
        choice = input("Select an option: ")

        if choice == "1":
            create_wallet()
        elif choice == "2":
            wallet_address = input("Enter Wallet Address: ")
            get_wallet(wallet_address)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")
