import sqlite3

SERVER_DB = "server_db.db"
CLIENT_DB = "client_db.db"


def init_server_db():
    """Initializes the server-side database with users, wallets, and transactions."""
    conn = sqlite3.connect(SERVER_DB)
    cursor = conn.cursor()

    # Drop tables if they exist to reset the database (optional, remove if needed)
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS wallets")
    cursor.execute("DROP TABLE IF EXISTS transactions")

    # Create users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            public_key TEXT NOT NULL,
            wallet_id TEXT UNIQUE NOT NULL
        )
    """)

    # Create wallets table
    cursor.execute("""
        CREATE TABLE wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_id TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 100.0,
            wallet_address TEXT UNIQUE NOT NULL  -- Fix: Add wallet_address column
        )
    """)


    # Create transactions table
    cursor.execute("""
        CREATE TABLE transactions (
            tx_id TEXT PRIMARY KEY,
            sender_username TEXT NOT NULL,
            receiver_username TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            digital_signature TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Server database initialized successfully.")

def init_client_db():
    """Initializes the client-side database for storing private keys securely."""
    conn = sqlite3.connect(CLIENT_DB)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS keys")

    cursor.execute("""
        CREATE TABLE keys (
            username TEXT UNIQUE NOT NULL,
            public_key TEXT NOT NULL,
            private_key TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Client database initialized successfully.")

if __name__ == "__main__":
    init_server_db()
    init_client_db()
