# Project: P05_fastapi-clean-example
# Layer: Business Logic (Query)
# Source: src/app/core/queries/list_users.py

import logging
from app.core.common.authorization.authorize import authorize
from app.core.common.authorization.current_user_service import CurrentUserService
from app.core.common.authorization.permissions import CanManageRole, RoleManagementContext
from app.core.common.entities.types_ import UserRole
from app.core.queries.ports.user_reader import ListUsersQm, UserReader
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams
from app.core.queries.query_support.sorting import SortingParams

logger = logging.getLogger(__name__)


class ListUsers:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_reader: UserReader,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_reader = user_reader

    async def execute(
        self,
        *,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQm:
        logger.info("List users: started.")

        current_user = await self._current_user_service.get_current_user()
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )
        result = await self._user_reader.list_users(
            pagination=pagination,
            sorting=sorting,
        )

        logger.info("List users: done.")
        return result