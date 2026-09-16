# Project: P12_fastapi-beyond-CRUD
# Layer: Business Logic (Service)
# Source: src/books/service.py

from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Book
from src.books.schemas import BookCreateModel

async def create_book(
    self, book_data: BookCreateModel, user_uid: str, session: AsyncSession
):
    book_data_dict = book_data.model_dump()
    new_book = Book(**book_data_dict)
    new_book.published_date = datetime.strptime(
        book_data_dict["published_date"], "%Y-%m-%d"
    )
    new_book.user_uid = user_uid
    session.add(new_book)
    await session.commit()
    return new_book