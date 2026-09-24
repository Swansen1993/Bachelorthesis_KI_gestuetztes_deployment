# Project: P11_fastapi-clean-architecture
# Layer: Database Query (Repository)
# Source: app/repository/tag_repository.py

from sqlalchemy.future import select
from app.repository.base_repository import BaseRepository
from app.model.tag import Tag

class TagRepository(BaseRepository):
    async def get_by_name(self, name: str):
        query = select(Tag).where(Tag.name == name)
        result = await self.db.execute(query)
        return result.scalars().first()