FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

WORKDIR /app/src

ENV APP_CONFIG_FILE=compose

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
