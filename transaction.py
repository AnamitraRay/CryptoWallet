import sqlite3
import uuid
import hashlib
from rsa_keys import load_rsa_keys
from database import DB_FILE

def create_transaction(sender_wallet, receiver_wallet, amount):
    tx_id = str(uuid.uuid4())[:8]
    sender_id = get_wallet_id(sender_wallet)
    receiver_id = get_wallet_id(receiver_wallet)

    if not sender_id or not receiver_id:
        return False, "Invalid wallet address."

    if not validate_balance(sender_id, amount):
        return False, "Insufficient balance."

    public_key, private_key = load_rsa_keys(sender_id)
    if not private_key:
        return False, "Could not retrieve private key for signing."

    tx_data = f"{tx_id}{sender_id}{receiver_id}{amount}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
    signature = private_key.sign(tx_hash.encode(), '')[0]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (tx_id, sender_id, receiver_id, amount, tx_hash, digital_signature, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (tx_id, sender_id, receiver_id, amount, tx_hash, signature, "pending"))

    cursor.execute("UPDATE wallets SET balance = balance - ? WHERE wallet_id = ?", (amount, sender_id))
    cursor.execute("UPDATE wallets SET balance = balance + ? WHERE wallet_id = ?", (amount, receiver_id))

    conn.commit()
    conn.close()
    return True, f"Transaction {tx_id} created successfully."

def get_wallet_id(wallet_address):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT wallet_id FROM wallets WHERE wallet_address = ?", (wallet_address,))
    wallet = cursor.fetchone()
    conn.close()
    return wallet[0] if wallet else None

def validate_balance(wallet_id, amount):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM wallets WHERE wallet_id = ?", (wallet_id,))
    balance = cursor.fetchone()
    conn.close()
    return balance and balance[0] >= amount
