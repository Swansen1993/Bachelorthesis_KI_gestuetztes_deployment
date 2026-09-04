import os

from sqlalchemy import Enum, String, create_engine, text

from common.db import models
from common.db.base import Base
from common.db.models.category import Category

engine = create_engine(os.environ["DATABASE_URL"])

for table in Base.metadata.tables.values():
    for column in table.columns:
        if isinstance(column.type, Enum):
            column.type = String(50)

Base.metadata.create_all(engine, tables=[Category.__table__])
with engine.begin() as connection:
    connection.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_categories_name "
            "ON categories (name)"
        )
    )
Base.metadata.create_all(engine)
