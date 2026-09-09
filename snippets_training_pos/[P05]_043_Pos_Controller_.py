# Project: P05_fastapi-clean-example
# Layer: Controller / HTTP
# Source: src/app/inbound/http/users/create_user.py

from typing import Annotated
from fastapi import APIRouter, Depends, status

from app.core.commands.create_user import CreateUser, CreateUserRequest, CreateUserResponse
from app.inbound.http.dependencies.commands import get_create_user_command

router = APIRouter()


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserResponse,
)
async def create_user(
    request: CreateUserRequest,
    command: Annotated[CreateUser, Depends(get_create_user_command)],
) -> CreateUserResponse:
    return await command.execute(request)