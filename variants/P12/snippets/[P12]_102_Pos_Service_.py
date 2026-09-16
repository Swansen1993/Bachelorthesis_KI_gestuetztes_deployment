# Project: P12_fastapi-beyond-CRUD
# Layer: Business Logic (Service)
# Source: src/tags/service.py

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Tag
from src.tags.schemas import TagCreateModel
from src.errors import TagAlreadyExists

async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
    statement = select(Tag).where(Tag.name == tag_data.name)
    result = await session.exec(statement)
    tag = result.first()

    if tag:
        raise TagAlreadyExists()
    new_tag = Tag(name=tag_data.name)

    session.add(new_tag)
    await session.commit()
    return new_tag