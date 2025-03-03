import sqlite3

DB_FILE = "transaction_ledger.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_ledger (
            tr_id TEXT PRIMARY KEY,
            sender_id TEXT UNIQUE NOT NULL,
            receiver_id TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            tx_hash TEXT NOT NULL,
            digital_signature TEXT NOT NULL,
            status TEXT CHECK(status IN ('pending', 'completed', 'failed')) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

import sqlite3

conn = sqlite3.connect("crypto_wallet.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        tx_id TEXT PRIMARY KEY,
        sender_id TEXT NOT NULL,
        receiver_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        
    )
''')

conn.commit()
conn.close()
