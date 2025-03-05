import sqlite3
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from database import DB_FILE

def aes_encrypt(data, key):
    """Encrypts data using AES (EAX Mode)."""
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

def aes_decrypt(encrypted_data, key):
    """Decrypts AES-encrypted data."""
    encrypted_data = base64.b64decode(encrypted_data)
    nonce, tag, ciphertext = encrypted_data[:16], encrypted_data[16:32], encrypted_data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def generate_and_store_rsa_keys(username):
    """Generates an RSA key pair, encrypts the private key, and stores it securely in the database."""
    rsa_key = RSA.generate(2048)
    public_key = rsa_key.publickey().export_key()
    private_key = rsa_key.export_key()

    aes_key = get_random_bytes(16)
    encrypted_private_key = aes_encrypt(private_key, aes_key)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO keys (username, public_key, encrypted_private_key, aes_key) VALUES (?, ?, ?, ?)',
                   (username, public_key.decode(), encrypted_private_key, base64.b64encode(aes_key).decode()))
    conn.commit()
    conn.close()

    print(f"RSA keys generated and stored securely for User: {username}")

def load_rsa_keys(username):
    """Retrieves an RSA key pair from the database and decrypts the private key."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT public_key, encrypted_private_key, aes_key FROM keys WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        public_key_pem, encrypted_private_key, aes_key = row
        aes_key = base64.b64decode(aes_key)
        decrypted_private_key_pem = aes_decrypt(encrypted_private_key, aes_key)

        private_key = RSA.import_key(decrypted_private_key_pem)
        public_key = RSA.import_key(public_key_pem)

        return public_key, private_key
    else:
        print("User not found.")
        return None, None
