import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class UserDTO:
    id: int
    username: str
    email: str
    password_hash: str
    bio: str
    image: str
    created_at: datetime.datetime


@dataclass(frozen=True)
class UpdatedUserDTO:
    id: int
    email: str
    username: str
    bio: str
    image: str


@dataclass(frozen=True)
class CreateUserDTO:
    username: str
    email: str
    password: str


@dataclass(frozen=True)
class LoginUserDTO:
    email: str
    password: str


@dataclass(frozen=True)
class UpdateUserDTO:
    username: str | None = None
    email: str | None = None
    password: str | None = None
    bio: str | None = None
    image: str | None = None
