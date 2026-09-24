# Project: P12_fastapi-beyond-CRUD
# Layer: Database / IO (Query)
# Source: src/tags/service.py

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Tag

async def get_tags(self, session: AsyncSession):
    statement = select(Tag).order_by(desc(Tag.created_at))
    result = await session.exec(statement)
    return result.all()