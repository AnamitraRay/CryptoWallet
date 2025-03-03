import sqlite3

DB_FILE = "wallets.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_id TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0.0,
            wallet_address TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            public_key TEXT NOT NULL,
            encrypted_private_key TEXT NOT NULL,
            aes_key TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            tx_id TEXT PRIMARY KEY,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            tx_hash TEXT NOT NULL,
            digital_signature TEXT NOT NULL,
            status TEXT CHECK(status IN ('pending', 'completed', 'failed')) NOT NULL,
            nonce INTEGER NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES wallets(wallet_id),
            FOREIGN KEY (receiver_id) REFERENCES wallets(wallet_id)
        )
    """)

    conn.commit()
    conn.close()
