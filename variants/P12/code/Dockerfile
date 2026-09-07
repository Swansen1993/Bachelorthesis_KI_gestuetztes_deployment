FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY overlay/src/middleware.py /app/src/src/middleware.py
COPY overlay/src/db/redis.py /app/src/src/db/redis.py
COPY overlay/src/db/main.py /app/src/src/db/main.py
COPY overlay/src/celery_tasks.py /app/src/src/celery_tasks.py
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
COPY seed /app/seed

ENV PYTHONPATH=/app/src

WORKDIR /app/src
EXPOSE 8080
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8080"]
