# Project: P10_fastapi-users
# Layer: Database / IO (Base Adapter Protocol)
# Source: fastapi_users/db/base.py

from typing import Any, Generic
from fastapi_users.models import ID, OAP, UOAP, UP

class BaseUserDatabase(Generic[UP, ID]):
    async def get_by_email(self, email: str) -> UP | None:
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, Any]) -> UP:
        
        raise NotImplementedError()

    async def update(self, user: UP, update_dict: dict[str, Any]) -> UP:
      
        raise NotImplementedError()