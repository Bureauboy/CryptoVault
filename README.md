🚀 CryptoVault:
A Secure, Self-Protecting File Encryption & Decryption System

CryptoVault is a high-security file vault designed to protect sensitive files through AES-256 encryption, tamper detection (HMAC), and self-destruct protocols.
It provides a Sender UI, Receiver UI, and Admin Panel, backed by a FastAPI server.

Built for hackathons, cybersecurity demonstrations, and secure file exchange workflows.

🔐 Core Features
✅ AES-256 Encryption

Every file is encrypted using AES-256-CBC with a unique key + IV per file.

✅ Tamper Detection (HMAC)

Encrypted data is protected using HMAC-SHA256.
If a single byte changes → the file is rejected.

✅ Self-Destruct Mechanism

After 3 wrong decryption attempts, CryptoVault automatically:
✔ Deletes the encrypted file
✔ Flags metadata → destroyed: true

✅ Role-Based UI

Sender UI → Encrypt & upload files

Receiver UI → Download & decrypt

Admin Panel → Monitor & manage vault

✅ Secure Metadata Layer

Stores:

Original file hash

Encrypted file hash

AES key + IV

Wrong attempts

Destroyed state

✅ API-Driven System

Everything runs through FastAPI:

/encrypt

/decrypt

/auth/login

UI endpoints (/sender, /receiver, /server) 
