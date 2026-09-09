# Project: P12_fastapi-beyond-CRUD
# Layer: Business Logic (Service)
# Source: src/reviews/service.py

import logging
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review
from src.reviews.schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()

async def add_review_to_book(
    self,
    user_email: str,
    book_uid: str,
    review_data: ReviewCreateModel,
    session: AsyncSession,
):
    try:
        book = await book_service.get_book(book_uid=book_uid, session=session)
        user = await user_service.get_user_by_email(
            email=user_email, session=session
        )
        review_data_dict = review_data.model_dump()
        if not book:
            raise HTTPException(
                detail="Book not found", status_code=status.HTTP_404_NOT_FOUND
            )
        if not user:
            raise HTTPException(
                detail="User not found", status_code=status.HTTP_404_NOT_FOUND
            )

        new_review = Review(**review_data_dict, user=user, book=book)
        session.add(new_review)
        await session.commit()
        return new_review

    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            detail="Oops... something went wrong!",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )