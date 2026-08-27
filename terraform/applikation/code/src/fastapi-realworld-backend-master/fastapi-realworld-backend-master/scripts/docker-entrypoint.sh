#!/bin/sh

set -e

python -m alembic -c alembic.ini upgrade head

exec "$@"
