import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.Enums.product_enums import ProductCategory
from common.db import models
from common.db.base import Base

engine = create_engine(os.environ["DATABASE_URL"])
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()
if session.query(models.Category).first() is None:
    for category in ProductCategory:
        session.add(models.Category(name=category, description="benchmark"))
    session.commit()
if session.query(models.Product).first() is None:
    product = models.Product(
        name="Benchmark Product",
        description="benchmark reference product",
        price=100.0,
        image="http://localhost/img.png",
        category_name=ProductCategory.ELECTRONICS,
        current_inventory=1000000000,
    )
    session.add(product)
    session.commit()
    session.add(
        models.Inventory(
            product_id=product.id,
            category_name=ProductCategory.ELECTRONICS,
            inventory_quantity=1000000000,
            low_stock_alert_threshold=10,
        )
    )
    session.commit()
session.close()
