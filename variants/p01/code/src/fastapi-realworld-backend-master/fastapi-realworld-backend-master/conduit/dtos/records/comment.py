import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class CommentRecordDTO:
    id: int
    body: str
    author_id: int
    article_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
