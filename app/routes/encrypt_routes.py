from fastapi import APIRouter, UploadFile, File, HTTPException
import os, shutil, hashlib
from src.encryption import CryptoVault
from src import file_handler
from config import ENC_DIR, UPLOAD_DIR
from src.utils import log_event
from app.utils.file_manager import save_metadata, load_metadata  # ✅ metadata helpers

router = APIRouter()


@router.post("/")
async def encrypt(file: UploadFile = File(...)):
    """Encrypt uploaded file using AES-256-CBC and store metadata for secure decryption."""
    try:
        # 1️⃣ Save uploaded file
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2️⃣ Encrypt file (unique key + IV for every upload)
        data = file_handler.load_file(file_path)
        vault = CryptoVault()
        encrypted, original_hash, key, iv = vault.encrypt_data(data)

        # 3️⃣ Save encrypted file
        os.makedirs(ENC_DIR, exist_ok=True)
        encrypted_name = file.filename + ".enc"
        output_path = os.path.join(ENC_DIR, encrypted_name)
        file_handler.save_file(output_path, encrypted)

        # 4️⃣ Compute SHA-256 checksum of *encrypted file*
        with open(output_path, "rb") as f:
            enc_sha256 = hashlib.sha256(f.read()).hexdigest()

        # 5️⃣ Store metadata for decryption tracking
        metadata = load_metadata()
        metadata[encrypted_name] = {
            "path": output_path,
            "key": key,                   # ⚠️ Keep plain only in dev — hash/encrypt in production
            "iv": iv,
            "hash": original_hash,        # ✅ store original (decrypted) hash for integrity check
            "enc_hash": enc_sha256,       # ✅ store encrypted file hash for reference
            "wrong_attempts": 0,
            "destroyed": False,
            "original_name": file.filename,
        }
        save_metadata(metadata)

        log_event(f"🔐 Encrypted: {file.filename} → {encrypted_name}")

        # 6️⃣ Return response for UI
        return {
            "status": "success",
            "encrypted_file": encrypted_name,
            "output_path": output_path,
            "key": key,
            "iv": iv,
            "original_hash": original_hash,
            "enc_hash": enc_sha256,
        }

    except Exception as e:
        log_event(f"❌ Encryption error: {e}")
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")
