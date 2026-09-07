FROM python:3.6.15-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY settings_container.py /app/src/settings_container.py
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

ENV PYTHONPATH=/app/src
ENV DJANGO_SETTINGS_MODULE=settings_container

WORKDIR /app/src
EXPOSE 8080
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["gunicorn", "conduit.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2"]
