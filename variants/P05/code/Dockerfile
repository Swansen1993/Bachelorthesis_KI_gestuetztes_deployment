FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY seed/ /app/seed/

ENV PYTHONPATH=/app/src/src

COPY docker-entrypoint.sh /app/docker-entrypoint.sh

WORKDIR /app/src
EXPOSE 8080
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main.run:make_app", "--host", "0.0.0.0", "--port", "8080"]
