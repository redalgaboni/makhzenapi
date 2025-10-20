#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_SERVER" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "⏳ Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Check if database is already initialized (using lock file)
if [ ! -f /code/.db_initialized ]; then
    echo "Initializing database..."

    # Create Alembic version table
    alembic upgrade head

    # Import reference data
    python -m backend.app.cli.jihate_import
    python -m backend.app.cli.amalate_jamaate_import
    python -m backend.app.cli.woulate_import

    # Create lock file to prevent re-initialization
    touch /code/.db_initialized
    echo "Database initialized successfully!"
else
    echo "Database already initialized. Skipping setup."
    alembic upgrade head
fi