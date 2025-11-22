
# ---

# 🔹 config.py
# ```python
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretjwtkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

UPLOAD_DIR = "uploads"
ENC_DIR = "data/encrypted"
DEC_DIR = "data/decrypted"
LOG_DIR = "logs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ENC_DIR, exist_ok=True)
os.makedirs(DEC_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
 
