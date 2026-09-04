import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.dtos.domain.article import CreateArticleDTO
from conduit.dtos.domain.user import CreateUserDTO, UserDTO
from conduit.interfaces.services.article import IArticleService
from conduit.interfaces.services.user import IUserService


async def create_user(
    session: AsyncSession, user_service: IUserService, username: str
) -> UserDTO:
    return await user_service.create_user(
        session=session,
        user_to_create=CreateUserDTO(
            username=username,
            email=f"{username}@example.com",
            password="password",
        ),
    )


async def create_article(
    session: AsyncSession,
    article_service: IArticleService,
    author_id: int,
    title: str,
    tags: list[str],
) -> None:
    await article_service.create_new_article(
        session=session,
        author_id=author_id,
        article_to_create=CreateArticleDTO(
            title=title,
            description="description",
            body="body",
            tags=tags,
        ),
    )


@pytest.mark.anyio
async def test_article_filters_by_tag(
    test_client: AsyncClient,
    session: AsyncSession,
    user_service: IUserService,
    article_service: IArticleService,
) -> None:
    author = await create_user(session, user_service, "tag-author")
    await create_article(session, article_service, author.id, "Tagged One", ["tag-one"])
    await create_article(session, article_service, author.id, "Tagged Two", ["tag-two"])

    response = await test_client.get(url="/articles", params={"tag": "tag-one"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["articlesCount"] == 1
    assert payload["articles"][0]["title"] == "Tagged One"
    assert "tag-one" in payload["articles"][0]["tagList"]


@pytest.mark.anyio
async def test_article_filters_by_author(
    test_client: AsyncClient,
    session: AsyncSession,
    user_service: IUserService,
    article_service: IArticleService,
) -> None:
    author = await create_user(session, user_service, "author-a")
    another_author = await create_user(session, user_service, "author-b")
    await create_article(
        session, article_service, author.id, "Author A Article", ["tag-a"]
    )
    await create_article(
        session, article_service, another_author.id, "Author B Article", ["tag-b"]
    )

    response = await test_client.get(
        url="/articles", params={"author": author.username}
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["articlesCount"] == 1
    assert payload["articles"][0]["author"]["username"] == author.username


@pytest.mark.anyio
async def test_article_filters_by_favorited(
    authorized_test_client: AsyncClient,
    test_client: AsyncClient,
    session: AsyncSession,
    user_service: IUserService,
    article_service: IArticleService,
    test_user: UserDTO,
) -> None:
    author = await create_user(session, user_service, "favorite-author")
    await create_article(
        session, article_service, author.id, "Favorited Article", ["tag-f"]
    )
    await create_article(
        session, article_service, author.id, "Not Favorited", ["tag-f"]
    )

    response = await test_client.get(url="/articles")
    articles = response.json()["articles"]
    favorited_article = next(
        article for article in articles if article["title"] == "Favorited Article"
    )
    slug = favorited_article["slug"]
    await authorized_test_client.post(url=f"/articles/{slug}/favorite")

    response = await authorized_test_client.get(
        url="/articles", params={"favorited": test_user.username}
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["articlesCount"] == 1
    assert payload["articles"][0]["favorited"] is True


@pytest.mark.anyio
async def test_articles_pagination_limit_and_offset(
    test_client: AsyncClient,
    session: AsyncSession,
    user_service: IUserService,
    article_service: IArticleService,
) -> None:
    author = await create_user(session, user_service, "pagination-author")
    await create_article(session, article_service, author.id, "Article One", ["tag-p"])
    await create_article(session, article_service, author.id, "Article Two", ["tag-p"])

    response = await test_client.get(url="/articles", params={"limit": 1, "offset": 0})
    assert response.status_code == 200
    payload = response.json()
    assert payload["articlesCount"] == 2
    assert len(payload["articles"]) == 1
    first_slug = payload["articles"][0]["slug"]

    response = await test_client.get(url="/articles", params={"limit": 1, "offset": 1})
    assert response.status_code == 200
    payload = response.json()
    assert payload["articlesCount"] == 2
    assert len(payload["articles"]) == 1
    assert payload["articles"][0]["slug"] != first_slug


@pytest.mark.anyio
async def test_user_feed_returns_followed_articles_only(
    authorized_test_client: AsyncClient,
    session: AsyncSession,
    user_service: IUserService,
    article_service: IArticleService,
) -> None:
    followed_author = await create_user(session, user_service, "followed-author")
    unfollowed_author = await create_user(session, user_service, "unfollowed-author")
    await create_article(
        session,
        article_service,
        followed_author.id,
        "Followed Article",
        ["tag-feed"],
    )
    await create_article(
        session,
        article_service,
        unfollowed_author.id,
        "Unfollowed Article",
        ["tag-feed"],
    )

    response = await authorized_test_client.post(
        url=f"/profiles/{followed_author.username}/follow"
    )
    assert response.status_code == 200

    response = await authorized_test_client.get(url="/articles/feed")
    assert response.status_code == 200
    payload = response.json()
    assert payload["articlesCount"] == 1
    assert payload["articles"][0]["author"]["username"] == followed_author.username
