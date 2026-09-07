FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src/users

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
COPY main_container.py /app/src/users/app/main.py

WORKDIR /app/src/users
EXPOSE 8080
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
