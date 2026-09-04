#!/bin/sh
export PRODUCT_SERVICE_URL="${PRODUCT_SERVICE_URL:-http://localhost:8080}"
cd /app/src/services/product_service
python -m uvicorn main:app --host 0.0.0.0 --port 8080 &
cd /app/src/services/sales_service
python -m uvicorn main:app --host 0.0.0.0 --port 8081 &
wait
