FROM python:3.11-slim
WORKDIR /src/fastapi-realworld-backend-master/fastapi-realworld-backend-master

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8080

CMD ["uvicorn", "conduit.app:app", "--host", "0.0.0.0", "--port", "8080"]