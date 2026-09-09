# Project: P02_async-fastapi-sqlalchemy
# Layer: Business Logic (Use-Case) / High-Performance
# Source: app/notes/use_cases/read_all_note.py

from typing import AsyncIterator
from app.db import AsyncSession
from app.models import Note, NoteSchema

class ReadAllNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self) -> AsyncIterator[NoteSchema]:
        async with self.async_session() as session:
            async for note in Note.read_all(session):
                yield NoteSchema.model_validate(note)