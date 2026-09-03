from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.config import get_app_settings
from conduit.core.container import container
from conduit.infrastructure.repositories.article import ArticleRepository
from conduit.infrastructure.repositories.article_tag import ArticleTagRepository
from conduit.infrastructure.repositories.comment import CommentRepository
from conduit.infrastructure.repositories.favorite import FavoriteRepository
from conduit.infrastructure.repositories.follower import FollowerRepository
from conduit.infrastructure.repositories.tag import TagRepository
from conduit.infrastructure.repositories.user import UserRepository
from conduit.interfaces.repositories.article import IArticleRepository
from conduit.interfaces.repositories.article_tag import IArticleTagRepository
from conduit.interfaces.repositories.comment import ICommentRepository
from conduit.interfaces.repositories.favorite import IFavoriteRepository
from conduit.interfaces.repositories.follower import IFollowerRepository
from conduit.interfaces.repositories.tag import ITagRepository
from conduit.interfaces.repositories.user import IUserRepository
from conduit.interfaces.services.article import IArticleService
from conduit.interfaces.services.auth import IUserAuthService
from conduit.interfaces.services.auth_token import IAuthTokenService
from conduit.interfaces.services.comment import ICommentService
from conduit.interfaces.services.profile import IProfileService
from conduit.interfaces.services.tag import ITagService
from conduit.interfaces.services.user import IUserService
from conduit.services.article import ArticleService
from conduit.services.auth import UserAuthService
from conduit.services.auth_token import AuthTokenService
from conduit.services.comment import CommentService
from conduit.services.profile import ProfileService
from conduit.services.tag import TagService
from conduit.services.user import UserService


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async for session in container.session():
        yield session


@lru_cache
def get_user_repo() -> IUserRepository:
    return UserRepository()


@lru_cache
def get_article_repo() -> IArticleRepository:
    return ArticleRepository()


@lru_cache
def get_article_tag_repo() -> IArticleTagRepository:
    return ArticleTagRepository()


@lru_cache
def get_comment_repo() -> ICommentRepository:
    return CommentRepository()


@lru_cache
def get_tag_repo() -> ITagRepository:
    return TagRepository()


@lru_cache
def get_favorite_repo() -> IFavoriteRepository:
    return FavoriteRepository()


@lru_cache
def get_follower_repo() -> IFollowerRepository:
    return FollowerRepository()


@lru_cache
def get_auth_token_service() -> IAuthTokenService:
    settings = get_app_settings()
    return AuthTokenService(
        secret_key=settings.jwt_secret_key,
        token_expiration_minutes=settings.jwt_token_expiration_minutes,
        algorithm=settings.jwt_algorithm,
    )


@lru_cache
def get_user_service() -> IUserService:
    return UserService(user_repo=get_user_repo())


@lru_cache
def get_profile_service() -> IProfileService:
    return ProfileService(
        user_service=get_user_service(), follower_repo=get_follower_repo()
    )


@lru_cache
def get_user_auth_service() -> IUserAuthService:
    return UserAuthService(
        user_service=get_user_service(), auth_token_service=get_auth_token_service()
    )


@lru_cache
def get_tag_service() -> ITagService:
    return TagService(tag_repo=get_tag_repo())


@lru_cache
def get_article_service() -> IArticleService:
    return ArticleService(
        article_repo=get_article_repo(),
        article_tag_repo=get_article_tag_repo(),
        favorite_repo=get_favorite_repo(),
        profile_service=get_profile_service(),
    )


@lru_cache
def get_comment_service() -> ICommentService:
    return CommentService(
        article_repo=get_article_repo(),
        comment_repo=get_comment_repo(),
        profile_service=get_profile_service(),
    )
