# Project: P12_fastapi-beyond-CRUD
# Layer: Business Logic (Service) - MUTATED
# Antipattern: One-by-One Processing & Chatty Commits (Chen et al., 2014; Jin et al., 2012)

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

    # FEHLER: Einzel-Queries und Commit/Refresh innerhalb der Iteration
    for tag_item in tag_data.tags:
        result = await session.exec(select(Tag).where(Tag.name == tag_item.name))
        tag = result.one_or_none()
        if not tag:
            tag = Tag(name=tag_item.name)
            session.add(tag)
            await session.commit()
            await session.refresh(tag)
        book.tags.append(tag)
        await session.commit()

    return book