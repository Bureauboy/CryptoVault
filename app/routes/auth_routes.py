from fastapi import APIRouter, Form
from src.auth import create_access_token, get_password_hash, verify_password

router = APIRouter()

# Fake in-memory user store
users_db = {"admin": get_password_hash("admin123")}

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username not in users_db:
        return {"error": "User not found"}

    if not verify_password(password, users_db[username]):
        return {"error": "Invalid password"}

    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}
 
