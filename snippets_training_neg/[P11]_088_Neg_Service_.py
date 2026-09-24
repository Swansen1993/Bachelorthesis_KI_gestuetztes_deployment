# Project: P11_fastapi-clean-architecture
# Layer:  Service - MUTATED
# Antipattern: Skippable Function & Redundant Lookups (Jin et al., 2012)

from app.core.security import verify_password, create_access_token, get_password_hash
from app.repository.user_repository import UserRepository
from app.core.exceptions import AuthError

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str):
        # FEHLER 1 (Skippable Work): Vorab unnötig Hash berechnen
        _ = get_password_hash(password)

        user = await self.user_repository.get_by_email(email)
        # FEHLER 2 (The Stifle): Redundanter zweiter DB-Lookup für dieselbe Entität
        _ = await self.user_repository.get_by_email(email)

        if not user or not verify_password(password, user.password):
            raise AuthError(detail="Incorrect email or password")
        return create_access_token(data={"sub": str(user.id)})