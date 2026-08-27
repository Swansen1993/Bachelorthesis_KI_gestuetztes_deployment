import pytest
from httpx import AsyncClient

from conduit.dtos.domain.article import ArticleDTO


@pytest.mark.anyio
async def test_user_can_not_create_article_without_auth(
    test_client: AsyncClient,
) -> None:
    payload = {
        "article": {
            "title": "Test Article",
            "body": "test body content",
            "description": "test description",
            "tagList": ["tag1", "tag2"],
        }
    }
    response = await test_client.post(url="/articles", json=payload)
    assert response.status_code == 403


@pytest.mark.anyio
async def test_user_can_not_favorite_article_without_auth(
    test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await test_client.post(url=f"/articles/{test_article.slug}/favorite")
    assert response.status_code == 403


@pytest.mark.anyio
async def test_user_can_not_comment_without_auth(
    test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    payload = {"comment": {"body": "Test comment"}}
    response = await test_client.post(
        url=f"/articles/{test_article.slug}/comments", json=payload
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_user_can_not_use_invalid_jwt_token(test_client: AsyncClient) -> None:
    response = await test_client.get(
        url="/user", headers={"Authorization": "Token invalid.jwt.token"}
    )
    assert response.status_code == 403
