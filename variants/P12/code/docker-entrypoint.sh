#!/bin/sh
if [ -n "${POSTGRES_HOST}" ] && [ -z "${DATABASE_URL}" ]; then
  DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT:-5432}/${POSTGRES_DB}"
  export DATABASE_URL
fi
if [ -z "${JWT_SECRET}" ]; then
  if [ -n "${JWT_SECRET_KEY}" ]; then
    JWT_SECRET="${JWT_SECRET_KEY}"
  elif [ -n "${SECRET_KEY}" ]; then
    JWT_SECRET="${SECRET_KEY}"
  fi
  export JWT_SECRET
fi
JWT_ALGORITHM="${JWT_ALGORITHM:-HS256}"
export JWT_ALGORITHM
DOMAIN="${DOMAIN:-localhost}"
export DOMAIN
MAIL_USERNAME="${MAIL_USERNAME:-bench@test.com}"
export MAIL_USERNAME
MAIL_PASSWORD="${MAIL_PASSWORD:-bench}"
export MAIL_PASSWORD
MAIL_FROM="${MAIL_FROM:-bench@test.com}"
export MAIL_FROM
MAIL_FROM_NAME="${MAIL_FROM_NAME:-Benchmark}"
export MAIL_FROM_NAME
MAIL_SERVER="${MAIL_SERVER:-localhost}"
export MAIL_SERVER
MAIL_PORT="${MAIL_PORT:-587}"
export MAIL_PORT
exec "$@"
