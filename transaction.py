import sqlite3
import uuid
import hashlib
from rsa_keys import load_rsa_keys
from database import DB_FILE

def validate_balance(username, amount):
    """Checks if the user has enough tokens to complete the transaction."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get the user's wallet balance
    cursor.execute("SELECT balance FROM wallets WHERE wallet_id = (SELECT wallet_id FROM users WHERE username = ?)", (username,))
    balance = cursor.fetchone()
    
    conn.close()
    return balance and balance[0] >= amount

def create_transaction(sender_username, receiver_username, amount):
    """Creates a transaction securely using usernames."""
    tx_id = str(uuid.uuid4())[:8]

    # Ensure sender & receiver exist
    if not user_exists(sender_username) or not user_exists(receiver_username):
        return False, "Invalid sender or receiver."

    if not validate_balance(sender_username, amount):
        return False, "Insufficient balance."

    public_key, private_key = load_rsa_keys(sender_username)
    if not private_key:
        return False, "Could not retrieve private key for signing."

    tx_data = f"{tx_id}{sender_username}{receiver_username}{amount}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
    signature = private_key.sign(tx_hash.encode(), '')[0]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (tx_id, sender_username, receiver_username, amount, tx_hash, digital_signature, status, nonce)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (tx_id, sender_username, receiver_username, amount, tx_hash, signature, "pending", uuid.uuid4().int))

    cursor.execute("UPDATE wallets SET balance = balance - ? WHERE wallet_id = (SELECT wallet_id FROM users WHERE username = ?)", (amount, sender_username))
    cursor.execute("UPDATE wallets SET balance = balance + ? WHERE wallet_id = (SELECT wallet_id FROM users WHERE username = ?)", (amount, receiver_username))

    conn.commit()
    conn.close()
    return True, f"Transaction {tx_id} created successfully."

def user_exists(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return bool(user)
