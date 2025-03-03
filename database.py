import sqlite3
import bcrypt

DB_FILE = "wallets.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Users Table (New)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            wallet_id TEXT UNIQUE NOT NULL
        )
    """)

    # Wallets Table (Modified to Link with Users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_id TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0.0,
            wallet_address TEXT UNIQUE NOT NULL
        )
    """)

    # Keys Table (Linked with Users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            public_key TEXT NOT NULL,
            encrypted_private_key TEXT NOT NULL,
            aes_key TEXT NOT NULL
        )
    """)

    # Transactions Table (Linked with Usernames)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            tx_id TEXT PRIMARY KEY,
            sender_username TEXT NOT NULL,
            receiver_username TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            tx_hash TEXT NOT NULL,
            digital_signature TEXT NOT NULL,
            status TEXT CHECK(status IN ('pending', 'completed', 'failed')) NOT NULL,
            nonce INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()
