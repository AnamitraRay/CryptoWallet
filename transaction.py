import sqlite3
import uuid
import hashlib
from rsa_keys import load_rsa_keys
from database import DB_FILE
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def user_exists(username):
    """Checks if a user exists in the users table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_wallet_id(username):
    """Fetches the wallet_id for a given username."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT wallet_id FROM users WHERE username = ?", (username,))
    wallet_id = cursor.fetchone()
    conn.close()
    return wallet_id[0] if wallet_id else None

def validate_balance(username, amount):
    """Checks if the sender has enough balance in their wallet."""
    wallet_id = get_wallet_id(username)
    if not wallet_id:
        print(f"Error: Wallet not found for {username}.")
        return False
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM wallets WHERE wallet_id = ?", (wallet_id,))
    balance = cursor.fetchone()
    conn.close()
    
    if balance is None:
        print(f"Error: Wallet {wallet_id} does not exist.")
        return False
    elif balance[0] < amount:
        print(f"Insufficient balance: {balance[0]} tokens.")
        return False
    return True

def create_transaction(sender_username, receiver_username, amount):
    """Processes a transaction using sender & receiver usernames."""
    tx_id = str(uuid.uuid4())[:12]  # Ensuring a unique transaction ID

    print(f"Checking if users exist: {sender_username}, {receiver_username}")
    if not user_exists(sender_username):
        return False, f"Sender {sender_username} does not exist."
    if not user_exists(receiver_username):
        return False, f"Receiver {receiver_username} does not exist."

    print(f"Validating balance for sender: {sender_username}")
    if not validate_balance(sender_username, amount):
        return False, "Sender has insufficient balance."

    print(f"Loading RSA keys for sender: {sender_username}")
    public_key, private_key = load_rsa_keys(sender_username)
    if not private_key:
        return False, "Could not retrieve private key for signing."

    print(f"Generating transaction signature...")
    tx_data = f"{tx_id}{sender_username}{receiver_username}{amount}"
    tx_hash = SHA256.new(tx_data.encode())

    try:
        signature = pkcs1_15.new(private_key).sign(tx_hash)
        signature_hex = signature.hex()
        print(f"Signature generated successfully for transaction {tx_id}")
    except Exception as e:
        return False, f"Signature generation failed: {str(e)}"
    
    sender_wallet = get_wallet_id(sender_username)
    receiver_wallet = get_wallet_id(receiver_username)

    print(f"Wallet IDs -> Sender: {sender_wallet}, Receiver: {receiver_wallet}")

    if not sender_wallet or not receiver_wallet:
        print("ERROR: One or both wallet IDs not found!")
        return False, "Wallet IDs missing. Transaction aborted."

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        print(f"Storing transaction in database...")
        cursor.execute("""
            INSERT INTO transactions (tx_id, sender_username, receiver_username, amount, tx_hash, digital_signature, status, nonce)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (tx_id, sender_username, receiver_username, amount, tx_hash.hexdigest(), signature_hex, "pending", uuid.uuid4().int%(10**10)))
        
        print(f"Transaction stored successfully!")

        print(f"Updating wallet balances...")

        # Log balance before updating
        cursor.execute("SELECT balance FROM wallets WHERE wallet_id = ?", (sender_wallet,))
        sender_balance = cursor.fetchone()[0]
        cursor.execute("SELECT balance FROM wallets WHERE wallet_id = ?", (receiver_wallet,))
        receiver_balance = cursor.fetchone()[0]

        print(f"Sender Balance Before: {sender_balance}")
        print(f"Receiver Balance Before: {receiver_balance}")

        cursor.execute("UPDATE wallets SET balance = balance - ? WHERE wallet_id = (SELECT wallet_id FROM users WHERE username = ?)", (amount, sender_username))
        cursor.execute("UPDATE wallets SET balance = balance + ? WHERE wallet_id = (SELECT wallet_id FROM users WHERE username = ?)", (amount, receiver_username))
        
        # Log balance after updating
        cursor.execute("SELECT balance FROM wallets WHERE wallet_id = ?", (sender_wallet,))
        sender_balance_after = cursor.fetchone()[0]
        cursor.execute("SELECT balance FROM wallets WHERE wallet_id = ?", (receiver_wallet,))
        receiver_balance_after = cursor.fetchone()[0]

        print(f"Sender Balance After: {sender_balance_after}")
        print(f"Receiver Balance After: {receiver_balance_after}")

        conn.commit()
        print(f"Transaction {tx_id} completed successfully!")

        return True, f"Transaction {tx_id} completed successfully."

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error while inserting transaction: {str(e)}")
        return False, f"Database error: {str(e)}"

    finally:
        conn.close()
