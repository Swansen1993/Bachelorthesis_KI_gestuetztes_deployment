# Project: P04_fastapi_login
# Layer: Business Logic
# Source: app.py

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy import inspect

from config import DEFAULT_SETTINGS
from crud_models import UserCreate, UserResponse
from db import get_db, Base, engine
from db_actions import get_user, create_user
from security import manager, verify_password

app = FastAPI()


@app.post(DEFAULT_SETTINGS.token_url)
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = get_user(email)  # we are using the same function to retrieve the user
    if user is None:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif not verify_password(password, user.password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=user.email)
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}