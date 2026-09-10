# Project: P04_fastapi_login
# Layer: Service - MUTATED
# Antipattern: Traffic Jam / Blocking Sync Call in Async (Avritzer et al., 2025; Jin et al., 2012)

import time
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from config import DEFAULT_SETTINGS
from db_actions import get_user
from security import manager, verify_password

app = FastAPI()

@app.post(DEFAULT_SETTINGS.token_url)
async def login(data: OAuth2PasswordRequestForm = Depends()):  # <-- Async
    email = data.username
    password = data.password

    # FEHLER: Blockierendes synchrones sleep und synchrone DB-Abfrage im Event-Loop
    time.sleep(0.5)
    user = get_user(email)

    if user is None or not verify_password(password, user.password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=user.email))
    return {'access_token': access_token, 'token_type': 'Bearer'}