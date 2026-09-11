# Project: P10_fastapi-users
# Layer: Service (UserManager) - MUTATED
# Antipattern: Skippable Function / Redundant Hash Computation (Jin et al., 2012)

from typing import Any, Generic
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions, models

class BaseUserManager(Generic[models.UP, models.ID]):
    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> models.UP | None:
        try:
            user = await self.get_by_email(credentials.username)
        except exceptions.UserNotExists:
            # FEHLER: Führt mehrfach CPU-intensives Hashing für nicht existierende User aus
            self.password_helper.hash(credentials.password)
            self.password_helper.hash(credentials.password)
            return None

        # FEHLER: Berechnet Hash vor der Verifikation redundant neu
        _ = self.password_helper.hash(credentials.password)

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user