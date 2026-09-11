import asyncio
import logging
import os

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.users import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 2000


async def create_first_user(session: AsyncSession) -> User:
    email = settings.FIRST_USER_EMAIL
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None:
        user = User(
            email=email,
            hashed_password=get_password_hash(
                settings.FIRST_USER_PASSWORD.get_secret_value()
            ),
            is_active=True,
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
    return user


async def create_bench_users(
    session: AsyncSession, password_hash: str, total: int
) -> int:
    result = await session.execute(
        select(func.count()).select_from(User).where(User.is_superuser.is_(False))
    )
    existing = result.scalar_one()
    created = 0
    while existing + created < total:
        size = min(BATCH_SIZE, total - existing - created)
        rows = [
            {
                "email": "bench_user_{:06d}@bench.local".format(
                    existing + created + offset
                ),
                "full_name": "Bench User {:06d}".format(existing + created + offset),
                "hashed_password": password_hash,
                "is_active": True,
                "is_superuser": False,
            }
            for offset in range(size)
        ]
        await session.execute(insert(User), rows)
        await session.commit()
        created += size
        logger.info("Bench users created: %s", created)
    return existing + created


async def main() -> None:
    total = int(os.getenv("BENCH_BULK_USERS", "20000"))
    logger.info("Creating benchmark data")
    async with SessionLocal() as session:
        admin = await create_first_user(session)
        bench_users = await create_bench_users(session, admin.hashed_password, total)
    logger.info("Benchmark data created: %s users", bench_users + 1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
