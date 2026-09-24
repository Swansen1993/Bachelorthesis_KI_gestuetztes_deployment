# Project: P02_async-fastapi-sqlalchemy
# Layer: Business Logic (Use-Case)
# Source: app/notes/use_cases/read_note.py

from fastapi import HTTPException
from app.db import AsyncSession
from app.models import Note, NoteSchema

class ReadNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, note_id: int) -> NoteSchema:
        async with self.async_session() as session:
            note = await Note.read_by_id(session, note_id)
            if not note:
                raise HTTPException(status_code=404)
            return NoteSchema.model_validate(note)