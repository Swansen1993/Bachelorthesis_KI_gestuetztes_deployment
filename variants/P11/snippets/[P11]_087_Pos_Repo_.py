# Project: P11_fastapi-clean-architecture
# Layer: Database Query (Repository)
# Source: app/repository/base_repository.py
# Hinweis: realer Pfad fuer pos_087_tag_create (POST /api/v1/tag -> create_tag -> TagService.add -> create)

from typing import TypeVar

from app.model.base_model import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    def create(self, schema: T):
        with self.session_factory() as session:
            query = self.model(**schema.dict())
            try:
                session.add(query)
                session.commit()
                session.refresh(query)
            except IntegrityError as e:
                raise DuplicatedError(detail=str(e.orig))
            return query
