# Project: P11_fastapi-clean-architecture
# Layer: Controller / HTTP
# Source: app/api/v1/endpoints/user.py
# Hinweis: realer Endpunkt create_user (POST /api/v1/user -> UserService.add)

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.core.dependencies import get_current_super_user
from app.core.middleware import inject
from app.model.user import User
from app.schema.user_schema import UpsertUser
from app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.post("", response_model=User)
@inject
def create_user(
    user: UpsertUser,
    service: UserService = Depends(Provide[Container.user_service]),
    current_user: User = Depends(get_current_super_user),
):
    return service.add(user)
