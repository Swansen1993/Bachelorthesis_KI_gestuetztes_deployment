# Project: P12_fastapi-beyond-CRUD
# Layer: Security / Utils
# Source: src/auth/utils.py

import uuid
from datetime import datetime, timedelta
import jwt
from src.config import Config

ACCESS_TOKEN_EXPIRY = 3600

def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )
    return token