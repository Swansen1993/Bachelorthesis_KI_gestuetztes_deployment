# Project: P05_fastapi-clean-example
# Layer: Controller / HTTP
# Source: src/app/inbound/http/users/list_users.py

from typing import Annotated
from fastapi import APIRouter, Depends, Query, status

from app.core.queries.list_users import ListUsers
from app.core.queries.ports.user_reader import ListUsersQm
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams
from app.core.queries.query_support.sorting import SortingOrder, SortingParams
from app.inbound.http.dependencies.queries import get_list_users_query

router = APIRouter()


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    response_model=ListUsersQm,
)
async def list_users(
    query: Annotated[ListUsers, Depends(get_list_users_query)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    sort_by: Annotated[str, Query()] = "created_at",
    order: Annotated[SortingOrder, Query()] = SortingOrder.DESC,
) -> ListUsersQm:
    pagination = OffsetPaginationParams(limit=limit, offset=offset)
    sorting = SortingParams(field=sort_by, order=order)
    return await query.execute(pagination=pagination, sorting=sorting)