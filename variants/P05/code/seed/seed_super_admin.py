import asyncio
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.common.entities.types_ import UserId, UserRole
from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username
from app.core.common.value_objects.utc_datetime import UtcDatetime
from app.main.config.loader import (
    load_password_hasher_settings,
    load_postgres_settings,
)
from app.outbound.adapters.bcrypt_password_hasher import BcryptPasswordHasher
from app.outbound.persistence_sqla.mappings.all import map_tables
from app.outbound.persistence_sqla.registry import mapper_registry

SEED_USERNAME = os.getenv("SEED_ADMIN_USERNAME", "bench_admin")
SEED_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "bench-admin-pass-123")


async def main() -> None:
    postgres_settings = load_postgres_settings()
    hasher_settings = load_password_hasher_settings()
    map_tables()

    engine = create_async_engine(postgres_settings.dsn)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="bcrypt-seed")
    semaphore = asyncio.Semaphore(1)
    hasher = BcryptPasswordHasher(
        pepper=hasher_settings.PEPPER.encode(),
        work_factor=hasher_settings.WORK_FACTOR,
        executor=executor,
        semaphore=semaphore,
        semaphore_wait_timeout_s=hasher_settings.SEMAPHORE_WAIT_TIMEOUT_S,
    )
    user_service = UserService(hasher)

    users_table = mapper_registry.metadata.tables["users"]
    try:
        async with session_factory() as session:
            existing = await session.execute(
                select(users_table.c.id).where(users_table.c.username == SEED_USERNAME)
            )
            if existing.scalar_one_or_none() is not None:
                print(
                    f"super_admin '{SEED_USERNAME}' existiert bereits - uebersprungen",
                    flush=True,
                )
                return

            now = UtcDatetime(datetime.now(UTC))
            user = await user_service.create_user_with_raw_password(
                user_id=UserId(uuid.uuid4()),
                username=Username(SEED_USERNAME),
                raw_password=RawPassword(SEED_PASSWORD),
                now=now,
                role=UserRole.USER,
                is_active=True,
            )
            user.role = UserRole.SUPER_ADMIN
            session.add(user)
            await session.commit()
            print(f"super_admin '{SEED_USERNAME}' angelegt", flush=True)
    finally:
        executor.shutdown(wait=True)
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
