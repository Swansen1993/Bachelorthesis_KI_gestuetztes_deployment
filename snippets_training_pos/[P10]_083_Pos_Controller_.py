# Project: P10_fastapi-users
# Layer: Controller / HTTP
# Source: fastapi_users/router/users.py

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_users import exceptions, models, schemas
from fastapi_users.authentication import Authenticator
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode, ErrorModel

def get_users_router(
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    user_schema: type[schemas.U],
    user_update_schema: type[schemas.UU],
    authenticator: Authenticator[models.UP, models.ID],
    requires_verification: bool = False,
) -> APIRouter:
    router = APIRouter()
    get_current_active_user = authenticator.current_user(
        active=True, verified=requires_verification
    )

    @router.get(
        "/me",
        response_model=user_schema,
        name="users:current_user",
    )
    async def me(
        user: models.UP = Depends(get_current_active_user),
    ):
        return user_schema.model_validate(user)

    return router