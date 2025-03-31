import sqlite3
import uuid
from database import SERVER_DB

def create_wallet(username):
    """Creates a wallet for a new user and returns wallet_id."""
    conn = sqlite3.connect(SERVER_DB)
    cursor = conn.cursor()

    wallet_id = str(uuid.uuid4())[:8]  # Ensure unique wallet ID
    wallet_address = f"wallet_{wallet_id}"

    try:
        cursor.execute("INSERT INTO wallets (wallet_id, balance, wallet_address) VALUES (?, ?, ?)",
                       (wallet_id, 100.0, wallet_address))
        conn.commit()
        return wallet_id, wallet_address  # Return wallet_id for linking to user

    except sqlite3.Error as e:
        print(f"Wallet creation failed: {e}")
        return None, None

    finally:
        conn.close()
