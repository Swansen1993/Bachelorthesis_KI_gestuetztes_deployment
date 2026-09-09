# Project: P10_fastapi-users
# Layer: Business Logic (UserManager)
# Source: fastapi_users/manager.py

from typing import Any, Generic
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions, models
from fastapi_users.db import BaseUserDatabase

class BaseUserManager(Generic[models.UP, models.ID]):
    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> models.UP | None:
        try:
            user = await self.get_by_email(credentials.username)
        except exceptions.UserNotExists:
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user