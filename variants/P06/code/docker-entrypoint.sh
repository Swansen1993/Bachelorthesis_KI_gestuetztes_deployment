#!/bin/sh
if [ -z "${DJANGO_SECRET_KEY}" ]; then
  if [ -n "${SECRET_KEY}" ]; then
    DJANGO_SECRET_KEY="${SECRET_KEY}"
  elif [ -n "${JWT_SECRET_KEY}" ]; then
    DJANGO_SECRET_KEY="${JWT_SECRET_KEY}"
  fi
  export DJANGO_SECRET_KEY
fi
exec "$@"
