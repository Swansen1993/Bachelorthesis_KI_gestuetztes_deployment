FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
COPY start.sh /app/start.sh
COPY schema_setup.py /app/schema_setup.py
COPY seed_categories.py /app/seed_categories.py

WORKDIR /app/src
EXPOSE 8080 8081
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["sh", "/app/start.sh"]
