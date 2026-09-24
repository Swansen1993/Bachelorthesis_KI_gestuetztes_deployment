# Project: P11_fastapi-clean-architecture
# Layer: Database Query (Repository)
# Source: app/repository/post_repository.py

from sqlalchemy.future import select
from app.repository.base_repository import BaseRepository
from app.model.post import Post

class PostRepository(BaseRepository):
    async def get_posts_with_pagination(self, skip: int = 0, limit: int = 10):
        query = select(Post).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()