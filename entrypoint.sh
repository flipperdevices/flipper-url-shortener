#!/bin/sh

set -eu

uvicorn --workers "$WORKERS" --host "$HOST" --port "$PORT" app.main:app --reload
