import datetime
from dataclasses import dataclass

from conduit.dtos.records.tag import TagRecordDTO


@dataclass(frozen=True)
class TagDTO:
    id: int
    tag: str
    created_at: datetime.datetime

    @classmethod
    def from_record(cls, record: TagRecordDTO) -> "TagDTO":
        return cls(id=record.id, tag=record.tag, created_at=record.created_at)
