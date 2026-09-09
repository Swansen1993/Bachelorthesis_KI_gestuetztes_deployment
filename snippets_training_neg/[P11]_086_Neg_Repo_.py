# Project: P11_fastapi-clean-architecture
# Layer: Database Query (Repository) - MUTATED
# Antipattern: Excessive Data / Python-Side Slicing (Chen et al., 2014)

from sqlalchemy.future import select
from app.repository.base_repository import BaseRepository
from app.model.post import Post

class PostRepository(BaseRepository):
    async def get_posts_with_pagination(self, skip: int = 0, limit: int = 10):
        # FEHLER (Excessive Data): SQL führt Full-Table-Scan aus; Slice erfolgt im RAM
        query = select(Post)
        result = await self.db.execute(query)
        all_posts = result.scalars().all()
        return all_posts[skip : skip + limit]