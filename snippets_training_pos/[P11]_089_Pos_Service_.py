# Project: P11_fastapi-clean-architecture
# Layer: Business Logic (Service)
# Source: app/services/base_service.py

from typing import Generic, TypeVar
from app.repository.base_repository import BaseRepository

T = TypeVar("T")

class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def get_by_id(self, id: int):
        return await self.repository.get_by_id(id)