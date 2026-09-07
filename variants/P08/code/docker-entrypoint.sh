#!/bin/sh
if [ -z "${DATABASE_URL}" ] && [ -n "${POSTGRES_HOST}" ]; then
  DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT:-5432}/${POSTGRES_DB}"
  export DATABASE_URL
fi
if [ -z "${ADMIN_CREATION_KEY}" ]; then
  ADMIN_CREATION_KEY="7060546501"
  export ADMIN_CREATION_KEY
fi
exec "$@"
