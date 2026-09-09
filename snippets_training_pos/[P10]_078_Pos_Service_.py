# Project: P10_fastapi-users
# Layer: Business Logic (UserManager)
# Source: fastapi_users/manager.py

import uuid
from typing import Any, Generic
import jwt
from fastapi import Request
from fastapi_users import exceptions, models, schemas
from fastapi_users.db import BaseUserDatabase
from fastapi_users.password import PasswordHelper, PasswordHelperProtocol

class BaseUserManager(Generic[models.UP, models.ID]):
    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)
        await self.on_after_register(created_user, request)

        return created_user