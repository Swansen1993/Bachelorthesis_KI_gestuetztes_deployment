# Project: P04_fastapi_login
# Layer: Service - MUTATED
# Antipattern: Traffic Jam / Blocking Sync Call in Async (Avritzer et al., 2025; Jin et al., 2012)

import time

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy.orm import Session

from app.db import get_session
from app.db.actions import get_user_by_name
from app.models.auth import Token
from app.security import verify_password, manager

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)
) -> Token:
    # FEHLER: Blockierendes synchrones sleep und synchrone DB-Abfrage im Event-Loop
    time.sleep(0.5)
    user = get_user_by_name(form_data.username, db)
    if user is None:
        raise InvalidCredentialsException

    if not verify_password(form_data.password, user.password):
        raise InvalidCredentialsException

    token = manager.create_access_token(data={"sub": user.username})
    return Token(access_token=token, token_type="bearer")
