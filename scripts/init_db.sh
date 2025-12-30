#!/bin/bash
# Initialize database with Alembic migrations

echo "Running database migrations..."
alembic upgrade head

echo "Database initialized successfully!"

