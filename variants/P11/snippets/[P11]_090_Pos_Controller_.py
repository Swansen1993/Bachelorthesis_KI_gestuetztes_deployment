# Project: P11_fastapi-clean-architecture
# Layer: Controller / HTTP
# Source: app/api/v1/endpoints/user.py

from fastapi import APIRouter, Depends, status
from app.services.user_service import UserService
from app.schema.user_schema import UserSchema, UserCreateSchema

router = APIRouter()

@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreateSchema,
    user_service: UserService = Depends()
):
    return await user_service.create_user(user_in)