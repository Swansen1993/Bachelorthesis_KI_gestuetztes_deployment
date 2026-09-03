import datetime
from dataclasses import dataclass, replace

from conduit.dtos.records.article import ArticleFeedRecordDTO, ArticleRecordDTO


@dataclass(frozen=True)
class ArticleAuthorDTO:
    username: str
    bio: str = ""
    image: str | None = None
    following: bool = False
    id: int | None = None


@dataclass(frozen=True)
class ArticleDTO:
    id: int
    author_id: int
    slug: str
    title: str
    description: str
    body: str
    tags: list[str]
    author: ArticleAuthorDTO
    created_at: datetime.datetime
    updated_at: datetime.datetime
    favorited: bool
    favorites_count: int

    @classmethod
    def with_updated_fields(
        cls, dto: "ArticleDTO", updated_fields: dict
    ) -> "ArticleDTO":
        return replace(dto, **updated_fields)

    @classmethod
    def from_record(
        cls,
        record: ArticleRecordDTO,
        author: ArticleAuthorDTO,
        tags: list[str],
        favorited: bool,
        favorites_count: int,
    ) -> "ArticleDTO":
        return cls(
            id=record.id,
            author_id=record.author_id,
            slug=record.slug,
            title=record.title,
            description=record.description,
            body=record.body,
            tags=tags,
            author=author,
            created_at=record.created_at,
            updated_at=record.updated_at,
            favorited=favorited,
            favorites_count=favorites_count,
        )

    @classmethod
    def from_feed_record(cls, record: ArticleFeedRecordDTO) -> "ArticleDTO":
        return cls(
            id=record.id,
            author_id=record.author_id,
            slug=record.slug,
            title=record.title,
            description=record.description,
            body=record.body,
            tags=record.tags,
            author=ArticleAuthorDTO(
                username=record.author_username,
                bio=record.author_bio or "",
                image=record.author_image,
                following=record.author_following,
            ),
            created_at=record.created_at,
            updated_at=record.updated_at,
            favorited=record.favorited,
            favorites_count=record.favorites_count,
        )


@dataclass(frozen=True)
class ArticlesFeedDTO:
    articles: list[ArticleDTO]
    articles_count: int


@dataclass(frozen=True)
class CreateArticleDTO:
    title: str
    description: str
    body: str
    tags: list[str]


@dataclass(frozen=True)
class UpdateArticleDTO:
    title: str | None
    description: str | None
    body: str | None
