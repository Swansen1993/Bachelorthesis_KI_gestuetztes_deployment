from sqlalchemy.ext.asyncio import AsyncSession

from conduit.dtos.domain.article import CreateArticleDTO
from conduit.dtos.domain.user import CreateUserDTO, UserDTO
from conduit.dtos.records.article import ArticleRecordDTO
from conduit.infrastructure.repositories.article import ArticleRepository
from conduit.interfaces.services.user import IUserService


async def create_another_test_user(
    session: AsyncSession, user_service: IUserService
) -> UserDTO:
    create_user_dto = CreateUserDTO(
        username="temp-user", email="temp-user@gmail.com", password="password"
    )
    return await user_service.create_user(
        session=session, user_to_create=create_user_dto
    )


async def create_another_test_article(
    session: AsyncSession, article_repository: ArticleRepository, author_id: int
) -> ArticleRecordDTO:
    create_article_dto = CreateArticleDTO(
        title="One More Test Article",
        description="Test Description",
        body="Test Body Content",
        tags=["tag1", "tag2", "tag3"],
    )
    return await article_repository.add(
        session=session, author_id=author_id, create_item=create_article_dto
    )
