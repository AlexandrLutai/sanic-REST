#!/bin/bash

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
alembic -c config/alembic.ini upgrade head

echo "Starting application..."
exec python -m app.main
