# Project: P02_async-fastapi-sqlalchemy
# Layer: Business Logic (Use-Case)
# Source: app/notes/use_cases/update_note.py

from fastapi import HTTPException
from app.db import AsyncSession
from app.models import Note, Notebook, NoteSchema

class UpdateNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, note_id: int, notebook_id: int, title: str, content: str) -> NoteSchema:
        async with self.async_session.begin() as session:
            note = await Note.read_by_id(session, note_id)
            if not note:
                raise HTTPException(status_code=404)

            if note.notebook_id != notebook_id:
                notebook = await Notebook.read_by_id(session, notebook_id)
                if not notebook:
                    raise HTTPException(status_code=404)
                notebook_id_ = notebook.id
            else:
                notebook_id_ = note.notebook_id

            await note.update(session, notebook_id_, title, content)
            await session.refresh(note)
            return NoteSchema.model_validate(note)