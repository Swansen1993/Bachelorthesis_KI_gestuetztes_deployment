# Project: P11_fastapi-clean-architecture
# Layer: Business Logic (Service)
# Source: app/services/auth_service.py

from app.core.security import verify_password, create_access_token
from app.repository.user_repository import UserRepository
from app.core.exceptions import AuthError

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise AuthError(detail="Incorrect email or password")
        return create_access_token(data={"sub": str(user.id)})