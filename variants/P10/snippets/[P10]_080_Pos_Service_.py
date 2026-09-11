# Project: P10_fastapi-users
# Layer: Business Logic (Authenticator)
# Source: fastapi_users/authentication/authenticator.py

from typing import Any, Generic, Sequence
from fastapi import HTTPException, status
from fastapi_users import models
from fastapi_users.authentication.backend import AuthenticationBackend
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.manager import BaseUserManager

class Authenticator(Generic[models.UP, models.ID]):
    async def _authenticate(
        self,
        *args,
        user_manager: BaseUserManager[models.UP, models.ID],
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        **kwargs,
    ) -> tuple[models.UP | None, str | None]:
        user: models.UP | None = None
        token: str | None = None
        enabled_backends: Sequence[AuthenticationBackend[models.UP, models.ID]] = (
            kwargs.get("enabled_backends", self.backends)
        )
        for backend in self.backends:
            if backend in enabled_backends:
                token = kwargs[name_to_variable_name(backend.name)]
                strategy: Strategy[models.UP, models.ID] = kwargs[
                    name_to_strategy_variable_name(backend.name)
                ]
                if token is not None:
                    user = await strategy.read_token(token, user_manager)
                    if user:
                        break

        status_code = status.HTTP_401_UNAUTHORIZED
        if user:
            status_code = status.HTTP_403_FORBIDDEN
            if active and not user.is_active:
                status_code = status.HTTP_401_UNAUTHORIZED
                user = None
            elif (
                verified and not user.is_verified or superuser and not user.is_superuser
            ):
                user = None
        if not user and not optional:
            raise HTTPException(status_code=status_code)
        return user, token