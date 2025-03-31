import bcrypt
import sqlite3
import uuid
from database import SERVER_DB

def hash_password(password):
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()  # Store as string

def verify_password(plain_password, hashed_password):
    """Verifies a password against a stored hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def register(username, password, public_key):
    """Registers a new user and creates a wallet."""
    conn = sqlite3.connect(SERVER_DB)
    cursor = conn.cursor()

    # Hash the password
    password_hash = hash_password(password)

    # Create wallet
    wallet_id = str(uuid.uuid4())[:8]
    wallet_address = f"wallet_{wallet_id}"

    try:
        # Insert into wallets table
        cursor.execute("INSERT INTO wallets (wallet_id, balance, wallet_address) VALUES (?, ?, ?)",
                       (wallet_id, 100.0, wallet_address))

        # Insert into users table
        cursor.execute("INSERT INTO users (username, password_hash, public_key, wallet_id) VALUES (?, ?, ?, ?)",
                       (username, password_hash, public_key, wallet_id))

        conn.commit()
        return True, f"User registered successfully! Wallet Address: {wallet_address}"

    except sqlite3.IntegrityError:
        return False, "Username already taken."

    finally:
        conn.close()

def login(username, password):
    """Verifies login credentials."""
    conn = sqlite3.connect(SERVER_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        stored_hash = row[0]
        if verify_password(password, stored_hash):
            return True, "Login successful!"
        else:
            return False, "Incorrect password."
    return False, "User not found."
