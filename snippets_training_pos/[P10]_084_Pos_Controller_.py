# Project: P10_fastapi-users
# Layer: Controller / HTTP
# Source: fastapi_users/router/reset.py

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import EmailStr
from fastapi_users import exceptions, models
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode

def get_reset_password_router(
    get_user_manager: UserManagerDependency[models.UP, models.ID],
) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/forgot-password",
        status_code=status.HTTP_202_ACCEPTED,
        name="reset:forgot_password",
    )
    async def forgot_password(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.get_by_email(email)
        except exceptions.UserNotExists:
            return None

        try:
            await user_manager.forgot_password(user, request)
        except exceptions.UserInactive:
            pass

        return None

    return router