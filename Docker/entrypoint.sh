#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
until pg_isready -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is up and running."

# Check if the database has been initialized
ALEMBIC_TABLE_EXISTS=$(psql -h $POSTGRES_SERVER -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'alembic_version';")

if [ "$ALEMBIC_TABLE_EXISTS" != "1" ]; then
    echo "Fresh database detected. Running initial migrations and data imports..."
    
    # Run Alembic migrations
    echo "Running Alembic revision and upgrade..."
    alembic revision --autogenerate -m "create users,jihate,woulate,amalate_jamaate,comments,reactions tables"
    alembic upgrade head

    # Run data imports
    echo "Running data import scripts..."
    python -m backend.app.cli.jihate_import
    python -m backend.app.cli.amalate_jamaate_import
    python -m backend.app.cli.woulate_import

    echo "Migrations and initial data imports complete."
else
    echo "Database is already initialized (alembic_version table found). Skipping initial setup."
fi

# Execute the main command passed to the container
echo "Starting application..."
exec "$@"