import pytest
from httpx import AsyncClient

from conduit.dtos.domain.article import ArticleDTO


@pytest.mark.anyio
async def test_article_delete_removes_access_to_comments_and_favorites(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    comment_payload = {"comment": {"body": "test comment"}}
    response = await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/comments", json=comment_payload
    )
    assert response.status_code == 200

    response = await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/favorite"
    )
    assert response.status_code == 200

    response = await authorized_test_client.delete(url=f"/articles/{test_article.slug}")
    assert response.status_code == 204

    response = await authorized_test_client.get(
        url=f"/articles/{test_article.slug}/comments"
    )
    assert response.status_code == 404

    response = await authorized_test_client.delete(
        url=f"/articles/{test_article.slug}/favorite"
    )
    assert response.status_code == 404
