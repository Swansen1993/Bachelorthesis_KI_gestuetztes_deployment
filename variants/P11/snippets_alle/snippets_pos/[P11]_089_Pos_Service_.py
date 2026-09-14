# Project: P11_fastapi-clean-architecture
# Layer: Business Logic (Service)
# Source: app/services/base_service.py
# Hinweis: realer Pfad fuer pos_089_post_by_id (GET /api/v1/post/{id} -> get_post -> get_by_id -> read_by_id)

from typing import Any, Protocol


class RepositoryProtocol(Protocol):
    def read_by_id(self, id: int) -> Any: ...


class BaseService:
    def __init__(self, repository: RepositoryProtocol) -> None:
        self._repository = repository

    def get_by_id(self, id: int) -> Any:
        return self._repository.read_by_id(id)
