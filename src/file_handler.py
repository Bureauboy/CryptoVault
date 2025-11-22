import os

def save_file(path: str, data: bytes):
    with open(path, "wb") as f:
        f.write(data)

def load_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()
  
