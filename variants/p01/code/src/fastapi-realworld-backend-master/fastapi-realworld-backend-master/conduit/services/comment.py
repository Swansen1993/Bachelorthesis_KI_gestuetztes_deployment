from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.exceptions import CommentCreateException, CommentPermissionException
from conduit.dtos.domain.comment import CommentDTO, CommentsListDTO, CreateCommentDTO
from conduit.dtos.domain.profile import ProfileDTO
from conduit.dtos.domain.user import UserDTO
from conduit.dtos.records.comment import CommentRecordDTO
from conduit.interfaces.repositories.article import IArticleRepository
from conduit.interfaces.repositories.comment import ICommentRepository
from conduit.interfaces.services.comment import ICommentService
from conduit.interfaces.services.profile import IProfileService


class CommentService(ICommentService):
    def __init__(
        self,
        article_repo: IArticleRepository,
        comment_repo: ICommentRepository,
        profile_service: IProfileService,
    ) -> None:
        self._article_repo = article_repo
        self._comment_repo = comment_repo
        self._profile_service = profile_service

    async def create_article_comment(
        self,
        session: AsyncSession,
        slug: str,
        comment_to_create: CreateCommentDTO,
        current_user: UserDTO,
    ) -> CommentDTO:
        article = await self._article_repo.get_by_slug(session=session, slug=slug)
        profile = ProfileDTO.from_user(user=current_user, following=False)
        try:
            comment_record_dto = await self._comment_repo.add(
                session=session,
                author_id=current_user.id,
                article_id=article.id,
                create_item=comment_to_create,
            )
        except (NoResultFound, MultipleResultsFound) as exc:
            raise CommentCreateException() from exc
        return CommentDTO.from_record(record=comment_record_dto, author=profile)

    async def get_article_comments(
        self, session: AsyncSession, slug: str, current_user: UserDTO | None = None
    ) -> CommentsListDTO:
        article = await self._article_repo.get_by_slug(session=session, slug=slug)
        comment_records = await self._comment_repo.list(
            session=session, article_id=article.id
        )
        profiles_map = await self._get_profiles_mapping(
            session=session, comments=comment_records, current_user=current_user
        )
        comments = [
            CommentDTO.from_record(
                comment_record_dto, profiles_map[comment_record_dto.author_id]
            )
            for comment_record_dto in comment_records
        ]
        comments_count = await self._comment_repo.count(
            session=session, article_id=article.id
        )
        return CommentsListDTO(comments=comments, comments_count=comments_count)

    async def delete_article_comment(
        self, session: AsyncSession, slug: str, comment_id: int, current_user: UserDTO
    ) -> None:
        # Check if article exists before deleting the comment.
        await self._article_repo.get_by_slug(session=session, slug=slug)

        comment = await self._comment_repo.get(session=session, comment_id=comment_id)
        if comment.author_id != current_user.id:
            raise CommentPermissionException()

        await self._comment_repo.delete(session=session, comment_id=comment_id)

    async def _get_profiles_mapping(
        self,
        session: AsyncSession,
        comments: list[CommentRecordDTO],
        current_user: UserDTO | None,
    ) -> dict[int, ProfileDTO]:
        comments_profiles = await self._profile_service.get_profiles_by_user_ids(
            session=session,
            user_ids=list({comment.author_id for comment in comments}),
            current_user=current_user,
        )
        return {profile.user_id: profile for profile in comments_profiles}
