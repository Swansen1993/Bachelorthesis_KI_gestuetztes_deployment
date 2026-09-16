# Project: P12_fastapi-beyond-CRUD
# Layer: Business Logic (Service)
# Source: src/reviews/service.py

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService

user_service = UserService()

async def delete_review_to_from_book(
    self, review_uid: str, user_email: str, session: AsyncSession
):
    user = await user_service.get_user_by_email(user_email, session)
    review = await self.get_review(review_uid, session)

    if not review or (review.user != user):
        raise HTTPException(
            detail="Cannot delete this review",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    session.delete(review)
    await session.commit()