import sqlite3
import uuid
from database import DB_FILE
from rsa_keys import generate_and_store_rsa_keys, load_rsa_keys

def create_wallet():
    """Creates a new wallet, generates RSA keys, and stores everything securely."""
    wallet_id = str(uuid.uuid4())[:8]
    wallet_address = f"wallet_{wallet_id}"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO wallets (wallet_id, balance, wallet_address)
        VALUES (?, ?, ?)
    """, (wallet_id, 0.0, wallet_address))
    conn.commit()
    conn.close()

    generate_and_store_rsa_keys(wallet_id)

    print(f"Wallet created successfully.")
    print(f"Wallet Address: {wallet_address}")

def get_wallet(wallet_address):
    """Retrieves wallet details and RSA keys from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT wallet_id, balance FROM wallets WHERE wallet_address = ?", (wallet_address,))
    wallet = cursor.fetchone()
    conn.close()

    if wallet:
        wallet_id, balance = wallet
        public_key, private_key = load_rsa_keys(wallet_id)

        print(f"Wallet Address: {wallet_address}")
        print(f"Balance: {balance} ETH")
        print(f"Public Key:\n{public_key.export_key().decode()}")
        print(f"Private Key (Decrypted):\n{private_key.export_key().decode()}")

    else:
        print("Wallet not found.")

