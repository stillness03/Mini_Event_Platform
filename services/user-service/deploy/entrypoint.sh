#!/bin/sh

set -e

echo "Waiting for database..."
sleep 5

echo "Running database migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8001 --proxy-headers