# Project: P12_fastapi-beyond-CRUD
# Layer: Security / Utils
# Source: src/auth/utils.py

from itsdangerous import URLSafeTimedSerializer
from src.config import Config

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)

def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token