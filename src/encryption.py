from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, hashlib

class CryptoVault:
    def __init__(self, key: bytes = None):
        # Generate 256-bit key (AES-256)
        self.key = key or AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.key)

    def encrypt_data(self, data: bytes):
        """
        Encrypts file data using AES-256-GCM.
        Returns (ciphertext, sha256 hash of plaintext, key_hex, iv_hex)
        """
        # Compute SHA-256 hash of original data (for tamper check)
        file_hash = hashlib.sha256(data).hexdigest()

        # 12-byte nonce (IV)
        nonce = os.urandom(12)

        # Encrypt using AES-GCM (authenticated encryption)
        encrypted = self.aesgcm.encrypt(nonce, data, None)

        # Return all encryption details
        return nonce + encrypted, file_hash, self.key.hex(), nonce.hex()

    def decrypt_data(self, enc_data: bytes, key_hex: str):
        """
        Decrypts AES-256-GCM data using the provided key.
        Returns (decrypted data, sha256 hash)
        """
        # Extract nonce (IV)
        nonce, ciphertext = enc_data[:12], enc_data[12:]

        # Recreate AESGCM object with provided key
        key = bytes.fromhex(key_hex)
        aesgcm = AESGCM(key)

        # Decrypt
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)

        # Compute hash of decrypted file for verification
        file_hash = hashlib.sha256(decrypted).hexdigest()

        return decrypted, file_hash
