import logging, os
from datetime import datetime

log_file = os.path.join("logs", "encryption.log")
logging.basicConfig(filename=log_file, level=logging.INFO)

def log_event(event: str):
    logging.info(f"{datetime.utcnow()} - {event}")
  
