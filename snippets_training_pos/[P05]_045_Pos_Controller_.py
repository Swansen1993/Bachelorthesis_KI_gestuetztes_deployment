# Project: P05_fastapi-clean-example
# Layer: Controller / HTTP
# Source: src/app/inbound/http/account/log_in.py

from typing import Annotated
from fastapi import APIRouter, Depends, status

from app.core.commands.log_in import LogIn, LogInRequest, LogInResponse
from app.inbound.http.dependencies.commands import get_log_in_command

router = APIRouter()


@router.post(
    "/account/log-in",
    status_code=status.HTTP_200_OK,
    response_model=LogInResponse,
)
async def log_in(
    request: LogInRequest,
    command: Annotated[LogIn, Depends(get_log_in_command)],
) -> LogInResponse:
    return await command.execute(request)