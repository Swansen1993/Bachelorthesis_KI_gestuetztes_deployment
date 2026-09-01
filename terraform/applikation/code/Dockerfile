FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

WORKDIR /app/src/fastapi-realworld-backend-master/fastapi-realworld-backend-master

EXPOSE 8080

CMD ["uvicorn", "conduit.app:app", "--host", "0.0.0.0", "--port", "8080"]