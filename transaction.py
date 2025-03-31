import sqlite3
from database import SERVER_DB
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

def create_transaction(sender, receiver, amount, signature):
    """Verifies and processes transactions."""
    conn = sqlite3.connect(SERVER_DB)
    cursor = conn.cursor()

    try:
        # Fetch sender's public key
        cursor.execute("SELECT public_key FROM users WHERE username = ?", (sender,))
        row = cursor.fetchone()
        if not row:
            return False, "Sender not found."

        sender_public_key = RSA.import_key(row[0])  # Correct public key import

        # Hash the transaction data
        transaction_data = f"{sender}-{receiver}-{amount}"
        hash_obj = SHA256.new(transaction_data.encode())

        # Verify the signature
        try:
            pkcs1_15.new(sender_public_key).verify(hash_obj, bytes.fromhex(signature))
            print("Signature is valid!")
        except (ValueError, TypeError):
            return False, "Signature verification failed!"

        # Fetch sender's wallet balance
        cursor.execute("SELECT balance FROM wallets WHERE wallet_id = (SELECT wallet_id FROM users WHERE username=?)", (sender,))
        sender_balance = cursor.fetchone()

        if not sender_balance or sender_balance[0] < amount:
            return False, "Insufficient balance."

        # Fetch receiver's wallet
        cursor.execute("SELECT wallet_id FROM users WHERE username=?", (receiver,))
        receiver_wallet = cursor.fetchone()
        if not receiver_wallet:
            return False, "Receiver not found."

        # Update balances
        cursor.execute("UPDATE wallets SET balance = balance - ? WHERE wallet_id = (SELECT wallet_id FROM users WHERE username=?)", (amount, sender))
        cursor.execute("UPDATE wallets SET balance = balance + ? WHERE wallet_id = (SELECT wallet_id FROM users WHERE username=?)", (amount, receiver))

        # Insert transaction record
        cursor.execute("INSERT INTO transactions (tx_id, sender_username, receiver_username, amount, digital_signature) VALUES (hex(randomblob(16)), ?, ?, ?, ?)",
                       (sender, receiver, amount, signature))
        conn.commit()

        return True, "Transaction successful."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    finally:
        conn.close()

def get_balance(username):
    """Fetches the balance of the user's wallet from the database."""
    conn = sqlite3.connect(SERVER_DB)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT balance FROM wallets WHERE wallet_id = (SELECT wallet_id FROM users WHERE username=?)", (username,))
        row = cursor.fetchone()
        
        if row:
            return True, row[0]
        return False, "Wallet not found."

    except sqlite3.Error as e:
        return False, f"Database error: {e}"

    finally:
        conn.close()
