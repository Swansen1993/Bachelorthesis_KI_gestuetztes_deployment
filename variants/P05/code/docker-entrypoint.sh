#!/bin/sh
if [ -z "${JWT_SECRET}" ] && [ -n "${SECRET_KEY}" ]; then
  JWT_SECRET="${SECRET_KEY}"
  export JWT_SECRET
fi
if [ -z "${JWT_SECRET}" ] && [ -n "${JWT_SECRET_KEY}" ]; then
  JWT_SECRET="${JWT_SECRET_KEY}"
  export JWT_SECRET
fi
if [ -z "${PASSWORD_PEPPER}" ]; then
  PASSWORD_PEPPER="benchmark-pepper-0123456789abcdef0123456789abcdef"
  export PASSWORD_PEPPER
fi
exec "$@"
