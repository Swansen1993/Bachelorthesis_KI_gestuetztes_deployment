import abc
from typing import Any

from conduit.dtos.domain.auth import AuthResult
from conduit.dtos.domain.user import CreateUserDTO, LoginUserDTO


class IUserAuthService(abc.ABC):
    @abc.abstractmethod
    async def sign_up_user(
        self, session: Any, user_to_create: CreateUserDTO
    ) -> AuthResult: ...

    @abc.abstractmethod
    async def sign_in_user(
        self, session: Any, user_to_login: LoginUserDTO
    ) -> AuthResult: ...
