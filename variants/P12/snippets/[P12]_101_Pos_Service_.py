# Project: P12_fastapi-beyond-CRUD
# Layer: Business Logic (Service)
# Source: src/tags/service.py

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.models import Tag
from src.tags.schemas import TagAddModel
from src.errors import BookNotFound

book_service = BookService()

async def add_tags_to_book(
    self, book_uid: str, tag_data: TagAddModel, session: AsyncSession
):
    book = await book_service.get_book(book_uid=book_uid, session=session)

    if not book:
        raise BookNotFound()

    for tag_item in tag_data.tags:
        result = await session.exec(select(Tag).where(Tag.name == tag_item.name))
        tag = result.one_or_none()
        if not tag:
            tag = Tag(name=tag_item.name)
        book.tags.append(tag)

    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book