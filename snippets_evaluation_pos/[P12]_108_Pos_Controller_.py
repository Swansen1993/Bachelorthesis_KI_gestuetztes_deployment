# Project: P12_fastapi-beyond-CRUD
# Layer: Controller / HTTP Route
# Source: src/tags/routes.py

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.schemas import Book
from src.db.main import get_session
from src.tags.schemas import TagAddModel
from src.tags.service import TagService

tag_service = TagService()

async def add_tags_to_book(
    book_uid: str, tag_data: TagAddModel, session: AsyncSession = Depends(get_session)
) -> Book:
    book_with_tag = await tag_service.add_tags_to_book(
        book_uid=book_uid, tag_data=tag_data, session=session
    )
    return book_with_tag