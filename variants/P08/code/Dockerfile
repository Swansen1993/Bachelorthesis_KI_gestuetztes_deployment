FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
COPY db_migrate.py /app/db_migrate.py

WORKDIR /app/src
EXPOSE 8080
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
