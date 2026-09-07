import asyncio
import os

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.utils import generate_passwd_hash
from src.db.main import async_engine
from src.db.models import User

email = os.getenv("SEED_USER_EMAIL", "bench@test.com")
password = os.getenv("SEED_USER_PASSWORD", "bench-pass-123")

session_factory = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def main():
    async with session_factory() as session:
        statement = select(User).where(User.email == email)
        user = (await session.exec(statement)).first()
        if user is None:
            session.add(
                User(
                    email=email,
                    username="bench",
                    first_name="Bench",
                    last_name="Admin",
                    role="admin",
                    is_verified=True,
                    password_hash=generate_passwd_hash(password),
                )
            )
            await session.commit()
            print("Seed-User angelegt")
        else:
            print("Seed-User existiert")


asyncio.run(main())
