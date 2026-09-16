FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY fixtures /app/fixtures
COPY seed /app/seed

ARG SEED_ROWS=1
ARG SEED_SEARCH_ROWS=1
ARG SEED_TRANSFERS=1
RUN SEED_ROWS=$SEED_ROWS SEED_SEARCH_ROWS=$SEED_SEARCH_ROWS SEED_TRANSFERS=$SEED_TRANSFERS python /app/seed/seed_fixtures.py

COPY overlay/app/fixtures_replay.py /app/src/app/fixtures_replay.py
COPY overlay/app/services/base.py /app/src/app/services/base.py

WORKDIR /app/src
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
