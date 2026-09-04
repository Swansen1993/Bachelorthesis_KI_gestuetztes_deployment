#!/bin/sh
if [ -z "${DATABASE_URL}" ] && [ -n "${POSTGRES_HOST}" ]; then
  DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
  export DATABASE_URL
fi
exec "$@"
