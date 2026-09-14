# Project: P09_fastapi-microservices
# Layer: Database Access (CRUD)
# Source: users/app/crud/users.py

from app.crud.base import CRUDBase
from app.models.users import User
from app.schemas.user import UserInDB, UserUpdateDB

CRUDUser = CRUDBase[User, UserInDB, UserUpdateDB]
crud_user = CRUDUser(User)