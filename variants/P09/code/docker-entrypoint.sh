#!/bin/sh
if [ -z "${PROJECT_NAME}" ]; then
  PROJECT_NAME="users"
  export PROJECT_NAME
fi
if [ -z "${FIRST_USER_EMAIL}" ]; then
  FIRST_USER_EMAIL="bench_admin@test.com"
  export FIRST_USER_EMAIL
fi
if [ -z "${FIRST_USER_PASSWORD}" ]; then
  FIRST_USER_PASSWORD="bench-admin-pass-123"
  export FIRST_USER_PASSWORD
fi
if [ -z "${SECRET_KEY}" ] && [ -n "${JWT_SECRET_KEY}" ]; then
  SECRET_KEY="${JWT_SECRET_KEY}"
  export SECRET_KEY
fi
if [ -z "${SECRET_KEY}" ]; then
  SECRET_KEY="bench-secret-key-0123456789abcdef0123456789abcdef"
  export SECRET_KEY
fi
if [ -z "${ACCESS_TOKEN_EXPIRE_MINUTES}" ]; then
  ACCESS_TOKEN_EXPIRE_MINUTES="60"
  export ACCESS_TOKEN_EXPIRE_MINUTES
fi
if [ -z "${REDIS_HOST}" ]; then
  REDIS_HOST="localhost"
  export REDIS_HOST
fi
if [ -z "${REDIS_PORT}" ]; then
  REDIS_PORT="6379"
  export REDIS_PORT
fi
exec "$@"
