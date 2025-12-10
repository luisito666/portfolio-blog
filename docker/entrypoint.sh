#!/bin/bash
set -e

# Function to wait for PostgreSQL to be ready
wait_for_db() {
    echo "Waiting for PostgreSQL to be ready..."
    
    # Set default values if not provided
    POSTGRES_HOST=${POSTGRES_HOST:-db}
    POSTGRES_PORT=${POSTGRES_PORT:-5432}
    
    if [ -n "$DATABASE_URL" ]; then
        echo "Using DATABASE_URL: $DATABASE_URL"
        # Parse DATABASE_URL to extract host and port
        POSTGRES_HOST=$(echo $DATABASE_URL | sed -e 's|.*://.*@\([^:]*\).*|\1|')
        POSTGRES_PORT=$(echo $DATABASE_URL | sed -e 's|.*:\([0-9]*\)/.*|\1|')
        
        # If parsing failed, use defaults
        if [ -z "$POSTGRES_HOST" ] || [ "$POSTGRES_HOST" = "$DATABASE_URL" ]; then
            POSTGRES_HOST="db"
        fi
        if [ -z "$POSTGRES_PORT" ] || [ "$POSTGRES_PORT" = "$DATABASE_URL" ]; then
            POSTGRES_PORT="5432"
        fi
    else
        echo "Using individual DB_* variables"
        echo "POSTGRES_HOST=$POSTGRES_HOST, POSTGRES_PORT=$POSTGRES_PORT"
    fi
    
    echo "Checking PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
    
    # Wait for database to be ready
    until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    
    echo "PostgreSQL is up!"
}

# Function to run migrations
run_migrations() {
    echo "Running database migrations..."
    python manage.py migrate --noinput
}

# Function to collect static files
collect_static() {
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
}

# Main execution
echo "Starting Django application..."

# Wait for database
wait_for_db

# Run migrations
run_migrations

# Collect static files
collect_static

echo "Starting application: $@"
exec "$@"