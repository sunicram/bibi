#!/bin/bash
set -e

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head

# Seed default user
echo "Seeding default user..."
python app/seed_user.py

# Start FastAPI server
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
