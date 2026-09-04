import contextlib
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from conduit.core.config import get_app_settings
from conduit.core.settings.base import BaseAppSettings
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


class Container:
    """Dependency injector project container."""

    def __init__(self, settings: BaseAppSettings) -> None:
        self._settings = settings
        self._engine = create_async_engine(**settings.sqlalchemy_engine_props)
        self._session = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    @contextlib.asynccontextmanager
    async def context_session(self) -> AsyncIterator[AsyncSession]:
        session = self._session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    def user_repository(self) -> IUserRepository:
        return UserRepository()

    @staticmethod
    def follower_repository() -> IFollowerRepository:
        return FollowerRepository()

    def tags_repository(self) -> ITagRepository:
        return TagRepository()

    def article_repository(self) -> IArticleRepository:
        return ArticleRepository()

    def article_tag_repository(self) -> IArticleTagRepository:
        return ArticleTagRepository()

    def comment_repository(self) -> ICommentRepository:
        return CommentRepository()

    @staticmethod
    def favorite_repository() -> IFavoriteRepository:
        return FavoriteRepository()

    def auth_token_service(self) -> IAuthTokenService:
        return AuthTokenService(
            secret_key=self._settings.jwt_secret_key,
            token_expiration_minutes=self._settings.jwt_token_expiration_minutes,
            algorithm=self._settings.jwt_algorithm,
        )

    def user_auth_service(self) -> IUserAuthService:
        return UserAuthService(
            user_service=self.user_service(),
            auth_token_service=self.auth_token_service(),
        )

    def user_service(self) -> IUserService:
        return UserService(user_repo=self.user_repository())

    def profile_service(self) -> IProfileService:
        return ProfileService(
            user_service=self.user_service(), follower_repo=self.follower_repository()
        )

    def tag_service(self) -> ITagService:
        return TagService(tag_repo=self.tags_repository())

    def article_service(self) -> IArticleService:
        return ArticleService(
            article_repo=self.article_repository(),
            article_tag_repo=self.article_tag_repository(),
            favorite_repo=self.favorite_repository(),
            profile_service=self.profile_service(),
        )

    def comment_service(self) -> ICommentService:
        return CommentService(
            article_repo=self.article_repository(),
            comment_repo=self.comment_repository(),
            profile_service=self.profile_service(),
        )


container = Container(settings=get_app_settings())
