import datetime
from dataclasses import dataclass

from conduit.dtos.domain.profile import ProfileDTO
from conduit.dtos.records.comment import CommentRecordDTO


@dataclass(frozen=True)
class CommentDTO:
    id: int
    body: str
    author: ProfileDTO
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @classmethod
    def from_record(cls, record: CommentRecordDTO, author: ProfileDTO) -> "CommentDTO":
        return cls(
            id=record.id,
            body=record.body,
            author=author,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


@dataclass(frozen=True)
class CommentsListDTO:
    comments: list[CommentDTO]
    comments_count: int


@dataclass(frozen=True)
class CreateCommentDTO:
    body: str
