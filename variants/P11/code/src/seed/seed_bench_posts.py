import os

from sqlalchemy import create_engine, text

from app.core.config import configs

BATCH_SIZE = 2000


def count_posts(conn) -> int:
    return conn.execute(text("SELECT count(*) FROM post")).scalar_one()


def main() -> None:
    total = int(os.getenv("BENCH_BULK_POSTS", "20000"))
    engine = create_engine(configs.DATABASE_URI)
    with engine.begin() as conn:
        existing = count_posts(conn)
    created = 0
    while existing + created < total:
        size = min(BATCH_SIZE, total - existing - created)
        rows = [
            {
                "user_token": "bench-seed-token",
                "title": "Bench Post {:06d}".format(existing + created + offset),
                "content": "benchmark body {}".format(existing + created + offset),
                "is_published": True,
            }
            for offset in range(size)
        ]
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO post (user_token, title, content, is_published, created_at, updated_at) "
                    "VALUES (:user_token, :title, :content, :is_published, now(), now())"
                ),
                rows,
            )
        created += size
        print("Posts created: {}".format(created))
    print("Posts ready: {}".format(existing + created))


if __name__ == "__main__":
    main()
