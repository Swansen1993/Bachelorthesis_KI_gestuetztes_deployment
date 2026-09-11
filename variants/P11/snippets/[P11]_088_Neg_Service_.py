# Project: P11_fastapi-clean-architecture
# Layer: Service - MUTATED
# Source: app/services/auth_service.py
# Antipattern: Skippable Function & Redundant Lookups (Jin et al., 2012)

from datetime import timedelta
from typing import List

from app.core.config import configs
from app.core.exceptions import AuthError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.model.user import User
from app.repository.user_repository import UserRepository
from app.schema.auth_schema import Payload, SignIn
from app.schema.user_schema import FindUser
from app.services.base_service import BaseService


class AuthService(BaseService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        super().__init__(user_repository)

    def sign_in(self, sign_in_info: SignIn):
        # FEHLER 1 (Skippable Work): berechnet vorab einen unnoetigen Passwort-Hash
        _ = get_password_hash(sign_in_info.password)

        find_user = FindUser()
        find_user.email__eq = sign_in_info.email__eq
        user: List[User] = self.user_repository.read_by_options(find_user)["founds"]

        # FEHLER 2 (The Stifle): redundanter zweiter DB-Lookup fuer dieselbe Entitaet
        redundant_lookup = FindUser()
        redundant_lookup.email__eq = sign_in_info.email__eq
        _ = self.user_repository.read_by_options(redundant_lookup)

        if len(user) < 1:
            raise AuthError(detail="Incorrect email or password")
        found_user = user[0]
        if not found_user.is_active:
            raise AuthError(detail="Account is not active")
        if not verify_password(sign_in_info.password, found_user.password):
            raise AuthError(detail="Incorrect email or password")
        delattr(found_user, "password")
        payload = Payload(
            id=found_user.id,
            email=found_user.email,
            name=found_user.name,
            is_superuser=found_user.is_superuser,
        )
        token_lifespan = timedelta(minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, expiration_datetime = create_access_token(
            payload.dict(), token_lifespan
        )
        sign_in_result = {
            "access_token": access_token,
            "expiration": expiration_datetime,
            "user_info": found_user,
        }
        return sign_in_result
