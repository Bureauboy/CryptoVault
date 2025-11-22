from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os, shutil
from src.encryption import CryptoVault
from src import file_handler
from config import DEC_DIR, UPLOAD_DIR
from src.utils import log_event
from app.utils.file_manager import load_metadata, save_metadata, sha256_bytes  # ✅ updated import

router = APIRouter()


@router.post("/")
async def decrypt(file: UploadFile = File(...), key: str = Form(...)):
    """Decrypt uploaded file using the provided AES key."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # ✅ Save uploaded file temporarily
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    metadata = load_metadata()
    file_id = file.filename

    # ✅ Validate file entry in metadata
    file_entry = metadata.get(file_id)
    if not file_entry:
        raise HTTPException(status_code=404, detail="File not found in metadata")

    # ✅ Check if file already destroyed
    if file_entry.get("destroyed", False):
        log_event(f"Attempted access to destroyed file {file.filename}")
        raise HTTPException(status_code=410, detail="File already destroyed after failed attempts")

    # ✅ Validate key
    if key != file_entry.get("key"):
        file_entry["wrong_attempts"] = file_entry.get("wrong_attempts", 0) + 1

        # ❌ If 3 failed attempts → destroy file
        if file_entry["wrong_attempts"] >= 3:
            file_entry["destroyed"] = True

            if os.path.exists(file_entry.get("path", "")):
                try:
                    os.remove(file_entry["path"])
                except Exception as e:
                    log_event(f"Error deleting file {file.filename}: {e}")

            save_metadata(metadata)
            log_event(f"File {file.filename} self-destructed after 3 wrong attempts")
            raise HTTPException(status_code=410, detail="File self-destructed after 3 failed attempts")

        save_metadata(metadata)
        raise HTTPException(status_code=401, detail=f"Wrong key! Attempts: {file_entry['wrong_attempts']}")

    # ✅ Correct key → reset attempts
    file_entry["wrong_attempts"] = 0
    save_metadata(metadata)

    # ✅ Load encrypted file
    if not os.path.exists(file_entry["path"]):
        raise HTTPException(status_code=404, detail="Encrypted file missing on server")

    enc_data = file_handler.load_file(file_entry["path"])
    vault = CryptoVault()

    try:
        decrypted, file_hash = vault.decrypt_data(enc_data, key)
    except Exception as e:
        log_event(f"Decryption failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Decryption failed")

    # ✅ Integrity check using SHA-256
    calc_hash = sha256_bytes(decrypted)

    stored_hash = file_entry.get("hash")
    if not stored_hash:
        raise HTTPException(status_code=400, detail="Hash not found in metadata — cannot verify integrity")

    if calc_hash != stored_hash:
        raise HTTPException(status_code=409, detail="File integrity check failed (SHA-256 mismatch)")

    # ✅ Save decrypted file
    output_path = os.path.join(DEC_DIR, file.filename.replace(".enc", ""))
    file_handler.save_file(output_path, decrypted)

    log_event(f"Decrypted file {file.filename} successfully")
    return {
        "message": "File decrypted successfully",
        "hash": calc_hash,
        "output": output_path
    }
