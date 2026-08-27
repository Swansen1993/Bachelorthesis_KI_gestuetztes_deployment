from dataclasses import dataclass


@dataclass(frozen=True)
class CreateUserRecordDTO:
    username: str
    email: str
    password_hash: str


@dataclass(frozen=True)
class UpdateUserRecordDTO:
    username: str | None = None
    email: str | None = None
    password_hash: str | None = None
    bio: str | None = None
    image: str | None = None
