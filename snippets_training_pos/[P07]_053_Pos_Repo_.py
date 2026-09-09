# Project: P07_ecommerce-backend
# Layer: Database Access
# Source: Services/SalesServices/controller.py

from datetime import datetime
from common.db.models.sales import Sales
from common.custom_exceptions import (
    ProductNotFoundException,
    NoSalesDataFoundException,
)
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

def fetch_sales(
    db: Session,
    product_id=None,
    category=None,
    start_date=None,
    end_date=None,
    group_by=None,
):
    try:
        sales_query = db.query(
            Sales.product_id,
            Sales.category_name,
            func.max(Sales.sold_at).label("last_sold_at"),
            func.sum(Sales.units_sold).label("total_units_sold"),
            func.sum(Sales.total_price).label("total_revenue"),
        )

        if product_id is not None:
            sales_query = sales_query.filter(Sales.product_id == product_id)

        if category is not None:
            sales_query = sales_query.filter(Sales.category_name == category)

        if start_date is None:
            start_date = datetime.min
        if end_date is None:
            end_date = datetime.now()

        sales_query = sales_query.filter(
            Sales.sold_at >= start_date, Sales.sold_at <= end_date
        )

        result = sales_query.all()

        if not result:
            raise NoSalesDataFoundException(
                "No sales data found for the specified criteria"
            )

        return result

    except NoResultFound as exc:
        raise ProductNotFoundException("Product not found") from exc
    except Exception as e:
        raise e