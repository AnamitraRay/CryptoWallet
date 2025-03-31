import sqlite3
from Crypto.PublicKey import RSA  # Use pycryptodome's RSA
from database import CLIENT_DB

def generate_and_store_rsa_keys(username):
    """Generates RSA keys using pycryptodome and stores them in the database."""
    key = RSA.generate(2048)

    private_key_pem = key.export_key().decode()  # Export private key
    public_key_pem = key.publickey().export_key().decode()  # Export public key

    conn = sqlite3.connect(CLIENT_DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO keys (username, public_key, private_key) VALUES (?, ?, ?)",
                   (username, public_key_pem, private_key_pem))
    conn.commit()
    conn.close()

def load_private_key(username):
    """Loads the user's private key and returns an RSA key."""
    conn = sqlite3.connect(CLIENT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT private_key FROM keys WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return RSA.import_key(row[0])  # Load with Crypto.PublicKey.RSA
    return None
