# Project: P11_fastapi-clean-architecture
# Layer: Database Query (Repository) - MUTATED
# Source: app/repository/base_repository.py
# Antipattern: Excessive Data / Python-Side Slicing (Chen et al., 2014)
# Hinweis: realer Listen-Pfad fuer pos_086_post_list (GET /api/v1/post -> get_post_list -> PostService.get_list -> read_by_options)

from contextlib import AbstractContextManager
from typing import Callable, Type, TypeVar

from sqlalchemy.orm import Session, joinedload

from app.core.config import configs
from app.model.base_model import BaseModel
from app.util.query_builder import dict_to_sqlalchemy_filter_options

T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
        model: Type[T],
    ) -> None:
        self.session_factory = session_factory
        self.model = model

    def read_by_options(self, schema: T, eager: bool = False) -> dict:
        with self.session_factory() as session:
            schema_as_dict: dict = schema.dict(exclude_none=True)
            ordering: str = schema_as_dict.get("ordering", configs.ORDERING)
            order_query = (
                getattr(self.model, ordering[1:]).desc()
                if ordering.startswith("-")
                else getattr(self.model, ordering).asc()
            )
            page = schema_as_dict.get("page", configs.PAGE)
            page_size = schema_as_dict.get("page_size", configs.PAGE_SIZE)
            filter_options = dict_to_sqlalchemy_filter_options(
                self.model, schema.dict(exclude_none=True)
            )
            query = session.query(self.model)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            filtered_query = query.filter(filter_options)
            query = filtered_query.order_by(order_query)
            if page_size == "all":
                query = query.all()
            else:
                # FEHLER (Excessive Data): SQL laedt ohne LIMIT/OFFSET alle Zeilen, die Seite wird erst im RAM geschnitten
                all_rows = query.all()
                query = all_rows[(page - 1) * page_size : page * page_size]
            total_count = filtered_query.count()
            return {
                "founds": query,
                "search_options": {
                    "page": page,
                    "page_size": page_size,
                    "ordering": ordering,
                    "total_count": total_count,
                },
            }
