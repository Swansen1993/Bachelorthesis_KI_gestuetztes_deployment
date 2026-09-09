# Project: P12_fastapi-beyond-CRUD
# Layer: Controller / HTTP Route - MUTATED
# Antipattern: Traffic Jam & The Stifle (Avritzer et al., 2025; Jin et al., 2012)

import time
from fastapi import Depends, status, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.schemas import UserCreateModel
from src.auth.service import UserService
from src.auth.utils import create_url_safe_token
from src.errors import UserAlreadyExists
from src.config import Config
from src.celery_tasks import send_email

user_service = UserService()

async def create_user_Account(
    user_data: UserCreateModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    # FEHLER 1 (Traffic Jam): Synchrone Blockade im Async Event-Loop
    time.sleep(0.3)

    email = user_data.email
    # FEHLER 2 (The Stifle): Redundanter zweifacher Check
    _ = await user_service.user_exists(email, session)
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)
    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    emails = [email]
    subject = "Verify Your email"

    send_email.delay(emails, subject, html)

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }