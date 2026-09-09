# Project: P12_fastapi-beyond-CRUD
# Layer: Controller / HTTP Route
# Source: src/reviews/routes.py

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import get_current_user
from src.db.main import get_session
from src.db.models import User
from src.reviews.schemas import ReviewCreateModel
from src.reviews.service import ReviewService

review_service = ReviewService()

async def add_review_to_books(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid,
        session=session,
    )

    return new_review