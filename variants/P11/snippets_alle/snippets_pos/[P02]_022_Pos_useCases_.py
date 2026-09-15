# Project: P02_async-fastapi-sqlalchemy
# Layer: Business Logic (Use-Case)
# Source: app/notes/use_cases/create_note.py

from fastapi import HTTPException
from app.db import AsyncSession
from app.models import Note, Notebook, NoteSchema

class CreateNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, notebook_id: int, title: str, content: str) -> NoteSchema:
        async with self.async_session.begin() as session:
            notebook = await Notebook.read_by_id(session, notebook_id)
            if not notebook:
                raise HTTPException(status_code=404)
            note = await Note.create(session, notebook.id, title, content)
            return NoteSchema.model_validate(note)