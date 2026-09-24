# Project: P03_mailer
# Layer: Controller / HTTP
# Source: mailer/api.py

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from . import recaptcha
from .mailer import Mailer
from .settings import Settings

router = APIRouter()

@router.post(
    "/mail",
    summary="Send e-mail",
    description="Send an e-mail from a contact",
    dependencies=[Depends(check_origin)],
    response_model=MailSchema,
    responses={
        str(int(HTTPStatus.UNAUTHORIZED)): {"description": "Unauthorized operation"}
    },
)
def post_mail(req: Request, mail: MailSchema) -> MailSchema:
    settings: Settings = req.app.state.settings

    mailer = Mailer(
        settings.sender_email,
        settings.to_email,
        settings.to_name,
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_tls,
        settings.smtp_ssl,
        settings.smtp_user,
        settings.smtp_password,
        settings.pgp_public_key,
    )

    try:
        recaptcha.verify(
            secret_key=settings.recaptcha_secret_key, response=mail.g_recaptcha_response
        )

        mailer.send_email(
            from_email=mail.email,
            from_name=mail.name,
            subject=mail.subject,
            message=mail.message,
            public_key=mail.public_key,
        )
    except RuntimeError:
        raise HTTPException(HTTPStatus.UNAUTHORIZED)

    return mail