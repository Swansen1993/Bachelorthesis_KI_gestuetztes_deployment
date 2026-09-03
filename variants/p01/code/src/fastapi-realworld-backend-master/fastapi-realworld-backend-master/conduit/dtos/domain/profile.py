from dataclasses import dataclass

from conduit.dtos.domain.user import UserDTO


@dataclass(frozen=True)
class ProfileDTO:
    user_id: int
    username: str
    bio: str = ""
    image: str | None = None
    following: bool = False

    @classmethod
    def from_user(cls, user: UserDTO, following: bool) -> "ProfileDTO":
        return cls(
            user_id=user.id,
            username=user.username,
            bio=user.bio,
            image=user.image,
            following=following,
        )
