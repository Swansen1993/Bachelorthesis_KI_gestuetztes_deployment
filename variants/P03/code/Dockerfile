FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

WORKDIR /app/src

ENV APP_ENVIRONMENT=production
ENV SENDER_EMAIL=benchmark@example.com
ENV TO_EMAIL=benchmark@example.com
ENV TO_NAME=Benchmark
ENV SMTP_HOST=localhost
ENV SMTP_PORT=25
ENV SMTP_TLS=false
ENV SMTP_SSL=false
ENV SMTP_USER=
ENV SMTP_PASSWORD=
ENV FORCE_HTTPS=false
ENV RECAPTCHA_SECRET_KEY=

EXPOSE 8080
CMD ["uvicorn", "mailer:app", "--host", "0.0.0.0", "--port", "8080"]
