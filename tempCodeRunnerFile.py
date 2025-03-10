import sqlite3
import bcrypt
import wallet
from database import DB_FILE

def register(username, password):
    """Registers a new user, creates their wallet, and stores credentials securely."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print("Username already taken.")
        conn.close()
        return False

    # Hash password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Create wallet
    wallet_id, wallet_address = wallet.create_wallet(username)

    # Store user details
    cursor.execute("INSERT INTO users (username, password_hash, wallet_id) VALUES (?, ?, ?)",
                   (username, password_hash, wallet_id))
    conn.commit()
    conn.close()
    
    print(f"✅ User '{username}' registered successfully! Wallet Address: {wallet_address}")
    return True

def login(username, password):
    """Validates login credentials."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if row and bcrypt.checkpw(password.encode(), row[0].encode()):
        print(f"Login successful! Welcome, {username}.")
        return True
    else:
        print("Invalid username or password.")
        return False
