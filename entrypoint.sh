#!/bin/sh

set -eu

alembic --config /app/app/alembic.ini upgrade head

uvicorn --workers "$WORKERS" --host "$HOST" --port "$PORT" app.main:app --reload
