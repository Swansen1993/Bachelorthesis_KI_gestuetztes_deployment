# Project: P09_fastapi-microservices
# Layer: Controller / HTTP API (MUTATED: Negativbeispiel)
# Source: users/app/api/v1/login.py
# Antipattern: Empty Semi Trucks / Unbounded Fetching (Avritzer et al., 2025)

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_session
from app.core.security import create_access_token, is_valid_password
from app.crud.users import crud_user
from app.schemas.token import Token

router = APIRouter(tags=["Login"])


@router.post("/login/", response_model=Token)
async def login(
    data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    # FEHLER (Empty Semi Trucks / Unbounded Fetching):
    # Kein begrenzter Lookup mehr: die gesamte Usertabelle wird geladen und in Python gefiltert
    users = await crud_user.get_multi(session, limit=None)
    user = next((u for u in users if u.email == data.username), None)
    if user is None or not is_valid_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return {"access_token": create_access_token(user), "token_type": "bearer"}
