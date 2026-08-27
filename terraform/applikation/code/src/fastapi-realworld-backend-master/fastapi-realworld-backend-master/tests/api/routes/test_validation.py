import pytest
from httpx import AsyncClient

from conduit.dtos.domain.article import ArticleDTO


@pytest.mark.parametrize(
    "payload",
    (
        {
            "user": {
                "email": "not-an-email",
                "username": "validuser",
                "password": "password",
            }
        },
        {
            "user": {
                "email": "user@example.com",
                "username": "ab",
                "password": "password",
            }
        },
        {
            "user": {
                "email": "user@example.com",
                "username": "validuser",
                "password": "short",
            }
        },
    ),
)
@pytest.mark.anyio
async def test_user_registration_validation_errors(
    test_client: AsyncClient, payload: dict
) -> None:
    response = await test_client.post("/users", json=payload)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    (
        {
            "article": {
                "title": "abcd",
                "description": "long enough description",
                "body": "long enough body",
                "tagList": [],
            }
        },
        {
            "article": {
                "title": "Valid Title",
                "description": "short",
                "body": "long enough body",
                "tagList": [],
            }
        },
        {
            "article": {
                "title": "Valid Title",
                "description": "long enough description",
                "body": "short",
                "tagList": [],
            }
        },
    ),
)
@pytest.mark.anyio
async def test_article_create_validation_errors(
    authorized_test_client: AsyncClient, payload: dict
) -> None:
    response = await authorized_test_client.post("/articles", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_comment_create_validation_error(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/comments",
        json={"comment": {"body": ""}},
    )
    assert response.status_code == 422
