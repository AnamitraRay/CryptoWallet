import sqlite3
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA  # Use pycryptodome's RSA
from database import CLIENT_DB
import base64
import os

IV = os.urandom(16)  # Ensure this is securely managed
KEY_SIZE = 32  # AES-256

def encrypt_private_key(private_key_pem, aes_key):
    """Encrypts the private key using AES-CBC."""
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=IV)

    # PKCS7 Padding
    pad_length = 16 - (len(private_key_pem) % 16)
    padded_key = private_key_pem + (chr(pad_length) * pad_length)

    encrypted = cipher.encrypt(padded_key.encode())
    return base64.b64encode(encrypted).decode()  # Store as Base64

def decrypt_private_key(encrypted_private_key, aes_key):
    """Decrypts the AES-encrypted private key."""
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=IV)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_private_key)).decode()

    # Remove PKCS7 Padding
    pad_length = ord(decrypted[-1])
    return decrypted[:-pad_length]

def generate_and_store_rsa_keys(username):
    """Generates RSA keys and stores them in the database."""
    key = RSA.generate(2048)
    private_key_pem = key.export_key().decode()
    public_key_pem = key.publickey().export_key().decode()

    aes_key = os.urandom(KEY_SIZE)  # Generate AES-256 Key
    encrypted_private_key = encrypt_private_key(private_key_pem, aes_key)

    conn = sqlite3.connect(CLIENT_DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO keys (username, public_key, encrypted_private_key, aes_key) VALUES (?, ?, ?, ?)",
                   (username, public_key_pem, encrypted_private_key, base64.b64encode(aes_key).decode()))
    conn.commit()
    conn.close()

def load_private_key(username):
    """Loads the user's AES key, decrypts the private key, and returns an RSA key."""
    conn = sqlite3.connect(CLIENT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT encrypted_private_key, aes_key FROM keys WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        encrypted_private_key = row[0]
        aes_key = base64.b64decode(row[1])  # Decode AES key
        decrypted_private_key_pem = decrypt_private_key(encrypted_private_key, aes_key)
        return RSA.import_key(decrypted_private_key_pem)  # Import the decrypted RSA key

    return None
