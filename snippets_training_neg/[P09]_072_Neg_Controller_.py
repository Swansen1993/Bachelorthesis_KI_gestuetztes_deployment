# Project: P09_fastapi-microservices
# Layer: Controller / HTTP API (MUTATED: Negativbeispiel)
# Antipattern: Empty Semi Trucks / Unbounded Fetching (Avritzer et al., 2025)

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_session, on_superuser
from app.crud.users import crud_user
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserOut], dependencies=[Depends(on_superuser)])
async def read_users(
    session: AsyncSession = Depends(get_session)  # <-- offset und limit entfernt
):
    # FEHLER (Empty Semi Trucks / Excessive Fetching):
    # Lädt unpaginiert die gesamte Tabelle in den RAM und serialisiert alles auf einmal
    users = await crud_user.get_all_unbounded(session)
    return users