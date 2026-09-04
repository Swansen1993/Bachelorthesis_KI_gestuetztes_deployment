FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN sed -i 's/, connect_args={"check_same_thread": False}//' /app/src/examples/full-example/app/db/__init__.py

ENV PYTHONPATH=/app/src

COPY docker-entrypoint.sh /app/docker-entrypoint.sh

WORKDIR /app/src/examples/full-example
EXPOSE 8080
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8080"]
