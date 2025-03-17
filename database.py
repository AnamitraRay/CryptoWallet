import sqlite3

DB_FILE = "wallets.db"

def init_db():
    """Initializes the database and creates necessary tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Enable Foreign Keys
    cursor.execute("PRAGMA foreign_keys = ON;")  

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                wallet_id TEXT UNIQUE NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                wallet_id TEXT PRIMARY KEY,
                balance REAL DEFAULT 100.0,
                wallet_address TEXT UNIQUE NOT NULL
            )
        """)

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
                nonce INTEGER NOT NULL,
                FOREIGN KEY (sender_username) REFERENCES users(username),
                FOREIGN KEY (receiver_username) REFERENCES users(username)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                public_key TEXT NOT NULL,
                encrypted_private_key TEXT NOT NULL,
                aes_key TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)

        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    init_db()
