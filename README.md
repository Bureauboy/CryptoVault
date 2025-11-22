# CryptoVault

A secure, self-protecting file encryption and decryption system built with FastAPI.  
CryptoVault encrypts files with AES-256-CBC, protects integrity with HMAC-SHA256, and implements a configurable self‑destruct mechanism when repeated wrong decryption attempts are detected. It includes a Sender UI, Receiver UI, and an Admin Panel for monitoring and management.

This project was created for hackathons and cybersecurity demonstrations but is useful as a foundation for secure file exchange workflows.

---

Table of contents
- About
- Key features
- Security model (quick overview)
- How it works (high level)
- Quick start
- API reference (examples)
- Configuration
- File/metadata format
- Admin features
- Security notes & recommendations
- Contributing
- License
- Contact

---

About
-----
CryptoVault's goal is to securely transmit and store files while preventing tampering and limiting brute-force or repeated unauthorized decryption attempts. Each file receives a unique AES key + IV and an HMAC to validate integrity. The vault can autonomously "self-destruct" (delete the encrypted data and mark metadata) after a defined number of failed decrypt attempts.

Key features
------------
- AES-256-CBC per-file encryption (unique key + IV per file)
- HMAC-SHA256 tamper-detection for encrypted data
- Self-destruct protocol after configurable number of wrong attempts
- Role-based UI: Sender (upload/encrypt), Receiver (download/decrypt), Admin (monitor/manage)
- FastAPI-driven REST API
- Stores secure metadata: original/encrypted file hashes, AES key + IV, attempt counters, destroyed state

Security model (quick overview)
-------------------------------
- Confidentiality: AES-256-CBC with per-file unique keys.
- Integrity: HMAC-SHA256 ensures any modification to the encrypted blob is detected.
- Availability / tamper response: self-destruct removes files after configured threshold of failed decrypt attempts.
- Metadata: minimal metadata is stored alongside encrypted blobs to support auditing and enforcement; sensitive fields are handled with care (see configuration & recommendations).

How it works (high level)
-------------------------
1. Sender uploads a file via the Sender UI or /encrypt endpoint.
2. Server generates a random AES-256 key and IV, encrypts the file with AES-256-CBC, computes HMAC-SHA256 over the ciphertext, and stores:
   - Encrypted blob
   - HMAC
   - AES key + IV (stored per design — consider secure KMS for production)
   - Original file hash, encrypted file hash
   - Wrong attempt counter, destroyed flag
3. Receiver requests file and attempts decrypt via Receiver UI or /decrypt endpoint. The server verifies HMAC before attempting decryption.
4. On HMAC mismatch or incorrect passphrase/credentials, wrong attempt counter increments. When it reaches the configured threshold (default: 3), the server:
   - Deletes the encrypted blob
   - Marks metadata destroyed: true
   - (Optionally) logs the event/audits and notifies admins
5. Admin Panel allows viewing metadata, revoking access, and manual intervention.

Quick start
-----------
Requirements
- Python 3.10+
- Pip
- (Optional) Docker for containerized runs

Install
1. Clone the repo:
   git clone https://github.com/Bureauboy/CryptoVault.git
2. Enter directory and create a virtual environment:
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate      # Windows
3. Install dependencies:
   pip install -r requirements.txt

Running locally
1. Start the FastAPI server:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
2. Open the UIs:
   - Sender UI: http://localhost:8000/sender
   - Receiver UI: http://localhost:8000/receiver
   - Admin Panel: http://localhost:8000/admin

(If Docker support is included, look for a docker-compose.yml or Dockerfile and follow the repository instructions.)

API reference (examples)
------------------------

Note: adjust host, ports and auth as configured.

1) Encrypt (upload) — multipart/form-data
Request:
curl -X POST "http://localhost:8000/encrypt" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/path/to/local-file.zip" \
  -F "recipient_id=<recipient>"

Response (example):
{
  "file_id": "uuid-or-id",
  "encrypted_hash": "sha256hex...",
  "destroyed": false,
  "expires_at": "2025-XX-XXTXX:XX:XXZ"
}

2) Download metadata / download encrypted file
GET /files/{file_id}  (returns metadata)
GET /files/{file_id}/download (returns encrypted blob)

3) Decrypt
Request (server-side verifies HMAC first):
curl -X POST "http://localhost:8000/decrypt" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"file_id":"<file_id>","passphrase":"<if-used>"}'

Successful Response:
- Returns the decrypted file byte stream (or a download link), and resets wrong_attempts to 0.

Failure Response:
- 401/403 with message like "HMAC verification failed" or "Incorrect decryption credentials"
- Server increments wrong_attempts; when threshold reached, server deletes blob and marks destroyed: true.

Auth
----
Endpoints are protected; use /auth/login to obtain a token (JWT or session token depending on implementation). Sender, Receiver, and Admin roles are enforced based on token scopes/roles.

Configuration
-------------
Common environment variables (names may vary; check app config):
- CRYPTOVAULT_SECRET_KEY — app secret (JWT signing, etc.)
- STORAGE_PATH — where encrypted files are saved
- MAX_WRONG_ATTEMPTS — default 3
- HMAC_KEY — key used for HMAC (or HMAC can be derived per-file)
- USE_KMS — true/false (if integrating with external Key Management Service)
- LOG_LEVEL — info/debug

File & metadata format
----------------------
Per-file metadata structure (example fields)
{
  "file_id": "uuid",
  "original_filename": "report.pdf",
  "original_hash": "sha256:...",
  "encrypted_hash": "sha256:...",
  "aes_key_enc": "<stored aes key or reference>",
  "iv": "<base64 iv>",
  "hmac": "<base64 hmac>",
  "wrong_attempts": 0,
  "destroyed": false,
  "created_at": "ISO8601 timestamp",
  "destroyed_at": null
}

Important: In production, AES keys should not be stored in plaintext in application storage. Use a secure Key Management Service (KMS) or hardware module for key protection. This implementation stores keys for demonstration purposes.

Admin features
--------------
- View metadata for all files
- Force-delete or restore (if implemented)
- Adjust thresholds and policies
- Audit log viewer for failed attempts and self-destruct events

Security notes & recommendations
-------------------------------
- Threat model: CryptoVault protects confidentiality & integrity of stored files when the server is trusted. If the server or its storage is compromised, AES keys stored on the server could be exposed.
- For production:
  - Use a KMS (AWS KMS, Azure Key Vault, HashiCorp Vault) to store AES keys or to wrap per-file keys.
  - Use TLS (HTTPS) for all client-server communications.
  - Harden the server: up-to-date dependencies, minimal privileges, read-only storage where possible.
  - Secure environment variables and secrets, use vault solutions for them.
  - Consider rate-limiting and IP-based protections to defend against brute force and denial-of-service.
  - Log suspicious activity and implement alerting for self-destruct events.
- HMAC Key: Keep the HMAC key separate from the AES key. Consider rotating HMAC keys in a managed fashion.

Limitations
-----------
- This project stores AES keys and metadata locally for demonstration; adapt to a KMS before using in production.
- Self-destruct is irreversible — backups must be properly planned if you need recoverability.

Testing
-------
- Unit tests should cover encryption/decryption, HMAC verification, wrong attempt counting, and self-destruct logic.
- Integration tests should exercise API endpoints with sample files and role-based auth.

Contributing
------------
Contributions welcome!
- Open an issue to discuss significant changes or features.
- Fork, create a feature branch, and open a pull request.
- Please include tests and update documentation when adding features.

License
-------
Specify your license here (e.g., MIT). If you want me to add a LICENSE file, tell me which license to use and I can add it.

Contact
-------
Project maintainer: Bureauboy (https://github.com/Bureauboy)  
If you want, I can help:
- Add example Postman collection
- Add Docker/Docker Compose setup
- Replace local key storage with a KMS integration example
- Harden README with exact environment variables and a sample .env

Acknowledgements
----------------
Built as a demonstration and secure-file-exchange template. Use responsibly and follow recommended best practices before deploying to production.
