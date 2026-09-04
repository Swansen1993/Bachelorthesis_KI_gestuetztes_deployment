#!/bin/sh
if [ -z "${DB_URI}" ] && [ -n "${POSTGRES_HOST}" ]; then
  DB_URI="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT:-5432}/${POSTGRES_DB}"
  export DB_URI
fi
if [ -z "${SECRET}" ] && [ -n "${SECRET_KEY}" ]; then
  SECRET="${SECRET_KEY}"
  export SECRET
fi
exec "$@"
