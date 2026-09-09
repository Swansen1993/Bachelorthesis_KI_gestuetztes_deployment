# Project: P12_fastapi-beyond-CRUD
# Layer: Security / Utils
# Source: src/auth/utils.py

import logging
import jwt
from src.config import Config

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None