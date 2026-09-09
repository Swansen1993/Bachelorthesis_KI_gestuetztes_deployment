# Project: P07_ecommerce-backend
# Layer: Controller / HTTP API
# Source: Services/SalesServices/routes.py

from fastapi import APIRouter, Depends, HTTPException
from api.schemas import SalesCreate, Sales
from api.controller import create_product_sale_transaction
from common.db.session import get_db
from sqlalchemy.orm import Session
from common.custom_exceptions import (
    ProductNotFoundException,
    ProductOutofStockException,
    ProductInventoryUpdateException,
    InsufficientInventoryException,
)

router = APIRouter()

@router.post("/create/", response_model=Sales, status_code=201)
def create_product_sale(potential_sale: SalesCreate, db: Session = Depends(get_db)):
    try:
        created_sales_transaction = create_product_sale_transaction(potential_sale, db)
        return created_sales_transaction
    except InsufficientInventoryException as error:
        raise HTTPException(status_code=422, detail=str(error))
    except ProductOutofStockException as error:
        raise HTTPException(status_code=422, detail=str(error))
    except ProductNotFoundException as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ProductInventoryUpdateException as error:
        raise HTTPException(status_code=500, detail=str(error))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")