from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Use Argon2 instead of bcrypt (bcrypt breaks on Python 3.12)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def verify_password(plain_password, hashed_password):
    """
    Verify password using Argon2 hash comparison.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Return Argon2 hashed password.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: int = None):
    """
    Create JWT access token with expiration.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
