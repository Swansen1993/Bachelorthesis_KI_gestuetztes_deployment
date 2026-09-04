from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

from conduit.dtos.domain.user import CreateUserDTO, LoginUserDTO, UpdateUserDTO


class UserRegistrationData(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3)


class UserLoginData(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdateData(BaseModel):
    email: EmailStr | None = Field(None)
    password: str | None = Field(None, min_length=8)
    username: str | None = Field(None, min_length=3)
    bio: str | None = Field(None)
    image: str | None = Field(None)

    @field_validator("*", mode="before")
    @classmethod
    def empty_as_none(cls, v: Any) -> Any:
        return v or None if isinstance(v, (str,)) else v


class UserRegistrationRequest(BaseModel):
    user: UserRegistrationData

    def to_dto(self) -> CreateUserDTO:
        return CreateUserDTO(
            username=self.user.username,
            email=self.user.email,
            password=self.user.password,
        )


class UserLoginRequest(BaseModel):
    user: UserLoginData

    def to_dto(self) -> LoginUserDTO:
        return LoginUserDTO(email=self.user.email, password=self.user.password)


class UserUpdateRequest(BaseModel):
    user: UserUpdateData

    def to_dto(self) -> UpdateUserDTO:
        return UpdateUserDTO(
            email=self.user.email,
            password=self.user.password,
            username=self.user.username,
            bio=self.user.bio,
            image=self.user.image,
        )
