FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src

COPY overlay/app/db.py /app/src/examples/sqlalchemy/app/db.py
COPY overlay/app/users.py /app/src/examples/sqlalchemy/app/users.py

WORKDIR /app/src/examples/sqlalchemy
EXPOSE 8080
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8080"]
