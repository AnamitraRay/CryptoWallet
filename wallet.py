import sqlite3
import uuid
from database import DB_FILE
from rsa_keys import generate_and_store_rsa_keys

def create_wallet(username):
    """Creates a wallet linked to a username."""
    wallet_id = str(uuid.uuid4())[:8]
    wallet_address = f"wallet_{wallet_id}"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # ✅ Ensure wallet is created and linked to user
    cursor.execute("INSERT INTO wallets (wallet_id, balance, wallet_address) VALUES (?, ?, ?)",
                   (wallet_id, 100.0, wallet_address))
    conn.commit()

    cursor.execute("UPDATE users SET wallet_id = ? WHERE username = ?", (wallet_id, username))
    conn.commit()
    
    generate_and_store_rsa_keys(username)

    conn.close()
    return wallet_id, wallet_address

def get_wallet(username):
    """Retrieves wallet details using username."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT wallet_id, balance, wallet_address 
        FROM wallets 
        WHERE wallet_id = (SELECT wallet_id FROM users WHERE username = ?)
    """, (username,))
    
    wallet = cursor.fetchone()
    conn.close()

    if wallet:
        wallet_id, balance, wallet_address = wallet
        return {
            "wallet_id": wallet_id,
            "balance": balance,
            "wallet_address": wallet_address
        }
    return None
