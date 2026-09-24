# Project: P07_ecommerce-backend
# Layer: Controller / HTTP API
# Source: Services/SalesServices/routes.py

from fastapi import APIRouter, Depends, HTTPException
from api.schemas import SalesRequestParams
from api.controller import fetch_sales
from common.db.session import get_db
from sqlalchemy.orm import Session
from common.custom_exceptions import (
    ProductNotFoundException,
    NoSalesDataFoundException,
)

router = APIRouter()

@router.post("/retrieve_sales")
def get_sales_for_product(params: SalesRequestParams, db: Session = Depends(get_db)):
    try:
        result = fetch_sales(
            db,
            product_id=params.product_id,
            category=params.category,
            start_date=params.start_date,
            end_date=params.end_date,
            group_by=params.group_by,
        )
        return result
    except ProductNotFoundException as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except NoSalesDataFoundException as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e