from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.queries.models.user import UserQm
from app.core.queries.ports.user_reader import ListUsersQm, UserReader
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams
from app.core.queries.query_support.sorting import SortingParams
from app.outbound.exceptions import ReaderError
from app.outbound.persistence_sqla.mappings.user import users_table


class SqlaUserReader(UserReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_users(
        self,
        *,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQm:
        stmt = select(
            users_table.c.id,
            users_table.c.username,
            users_table.c.role,
            users_table.c.is_active,
            users_table.c.created_at,
            users_table.c.updated_at,
        )
        try:
            result = await self._session.execute(stmt)
            all_rows = result.all()
        except SQLAlchemyError as e:
            raise ReaderError from e

        total = len(all_rows)
        paged_rows = all_rows[pagination.offset : pagination.offset + pagination.limit]

        users = [
            UserQm(
                id=row.id,
                username=row.username,
                role=row.role,
                is_active=row.is_active,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in paged_rows
        ]
        return ListUsersQm(
            users=users,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        )
