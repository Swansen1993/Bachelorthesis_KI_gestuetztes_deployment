# Project: P02_async-fastapi-sqlalchemy
# Layer: Business Logic (Use-Case)
# Source: app/notes/use_cases/delete_note.py

from app.db import AsyncSession
from app.models import Note

class DeleteNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, note_id: int) -> None:
        async with self.async_session.begin() as session:
            note = await Note.read_by_id(session, note_id)
            if not note:
                return
            await Note.delete(session, note)