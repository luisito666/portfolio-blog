#!/bin/bash
set -e

# Function to wait for PostgreSQL to be ready
wait_for_db() {
    echo "Waiting for PostgreSQL to be ready..."
    
    # Set default values if not provided
    DB_HOST=${DB_HOST:-db}
    DB_PORT=${DB_PORT:-5432}
    
    if [ -n "$DATABASE_URL" ]; then
        echo "Using DATABASE_URL: $DATABASE_URL"
        # Parse DATABASE_URL to extract host and port
        DB_HOST=$(echo $DATABASE_URL | sed -e 's|.*://.*@\([^:]*\).*|\1|')
        DB_PORT=$(echo $DATABASE_URL | sed -e 's|.*:\([0-9]*\)/.*|\1|')
        
        # If parsing failed, use defaults
        if [ -z "$DB_HOST" ] || [ "$DB_HOST" = "$DATABASE_URL" ]; then
            DB_HOST="db"
        fi
        if [ -z "$DB_PORT" ] || [ "$DB_PORT" = "$DATABASE_URL" ]; then
            DB_PORT="5432"
        fi
    else
        echo "Using individual DB_* variables"
        echo "DB_HOST=$DB_HOST, DB_PORT=$DB_PORT"
    fi
    
    echo "Checking PostgreSQL at $DB_HOST:$DB_PORT..."
    
    # Wait for database to be ready
    until pg_isready -h $DB_HOST -p $DB_PORT; do
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