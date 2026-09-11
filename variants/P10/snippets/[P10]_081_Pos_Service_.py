# Project: P10_fastapi-users
# Layer: Business Logic (Backend)
# Source: fastapi_users/authentication/backend.py

from typing import Generic
from fastapi import Response, status
from fastapi_users import models
from fastapi_users.authentication.strategy import Strategy, StrategyDestroyNotSupportedError
from fastapi_users.authentication.transport import Transport, TransportLogoutNotSupportedError

class AuthenticationBackend(Generic[models.UP, models.ID]):
    async def logout(
        self, strategy: Strategy[models.UP, models.ID], user: models.UP, token: str
    ) -> Response:
        try:
            await strategy.destroy_token(token, user)
        except StrategyDestroyNotSupportedError:
            pass

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response