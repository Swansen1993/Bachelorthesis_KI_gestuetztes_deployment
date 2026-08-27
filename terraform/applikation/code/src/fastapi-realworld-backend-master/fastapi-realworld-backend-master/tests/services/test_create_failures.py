import datetime

import pytest
from sqlalchemy.exc import NoResultFound

from conduit.core.exceptions import (
    ArticleCreateException,
    CommentCreateException,
    UserCreateException,
)
from conduit.dtos.domain.article import CreateArticleDTO
from conduit.dtos.domain.comment import CreateCommentDTO
from conduit.dtos.domain.user import CreateUserDTO, UserDTO
from conduit.dtos.records.article import ArticleRecordDTO
from conduit.services.article import ArticleService
from conduit.services.comment import CommentService
from conduit.services.user import UserService


class _FailingArticleRepo:
    async def add(self, *_: object, **__: object) -> ArticleRecordDTO:
        raise NoResultFound()


class _FailingUserRepo:
    async def get_by_email_or_none(self, *_: object, **__: object) -> UserDTO | None:
        return None

    async def get_by_username_or_none(self, *_: object, **__: object) -> UserDTO | None:
        return None

    async def add(self, *_: object, **__: object) -> UserDTO:
        raise NoResultFound()


class _FailingCommentRepo:
    async def add(self, *_: object, **__: object) -> object:
        raise NoResultFound()


class _ArticleRepo:
    async def get_by_slug(self, *_: object, **__: object) -> ArticleRecordDTO:
        return ArticleRecordDTO(
            id=1,
            author_id=1,
            slug="article-slug",
            title="title",
            description="description",
            body="body",
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )


class _NoopArticleTagRepo:
    async def add_many(self, *_: object, **__: object) -> list[object]:
        return []


class _NoopFavoriteRepo:
    async def count(self, *_: object, **__: object) -> int:
        return 0

    async def exists(self, *_: object, **__: object) -> bool:
        return False


class _NoopProfileService:
    async def get_profile_by_user_id(self, *_: object, **__: object) -> object:
        raise AssertionError("Not expected to be called")


@pytest.mark.anyio
async def test_article_create_raises_create_exception() -> None:
    service = ArticleService(
        article_repo=_FailingArticleRepo(),
        article_tag_repo=_NoopArticleTagRepo(),
        favorite_repo=_NoopFavoriteRepo(),
        profile_service=_NoopProfileService(),
    )
    create_article_dto = CreateArticleDTO(
        title="title", description="desc", body="body", tags=[]
    )
    with pytest.raises(ArticleCreateException):
        await service.create_new_article(
            session=None, author_id=1, article_to_create=create_article_dto
        )


@pytest.mark.anyio
async def test_user_create_raises_create_exception() -> None:
    service = UserService(user_repo=_FailingUserRepo())
    create_user_dto = CreateUserDTO(
        username="user", email="user@example.com", password="secret"
    )
    with pytest.raises(UserCreateException):
        await service.create_user(session=None, user_to_create=create_user_dto)


@pytest.mark.anyio
async def test_comment_create_raises_create_exception() -> None:
    current_user = UserDTO(
        id=1,
        username="user",
        email="user@example.com",
        password_hash="hash",
        bio="",
        image="",
        created_at=datetime.datetime.now(),
    )
    service = CommentService(
        article_repo=_ArticleRepo(),
        comment_repo=_FailingCommentRepo(),
        profile_service=_NoopProfileService(),
    )
    with pytest.raises(CommentCreateException):
        await service.create_article_comment(
            session=None,
            slug="article-slug",
            comment_to_create=CreateCommentDTO(body="body"),
            current_user=current_user,
        )
