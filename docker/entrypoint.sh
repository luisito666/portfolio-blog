#!/bin/bash
set -e

# Function to wait for PostgreSQL to be ready
wait_for_db() {
    echo "Waiting for PostgreSQL to be ready..."

    # Use Python to check connection - works reliably as non-root user
    # This method uses Django's database connection, so it's guaranteed to work
    python << ENDSCRIPT
import sys
import time
import os
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.core.exceptions import ImproperlyConfigured

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        # Try to establish a connection
        connection.ensure_connection()
        # If successful, try a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                print("PostgreSQL is ready!", flush=True)
                sys.exit(0)
    except Exception as e:
        retry_count += 1
        print(f"Waiting for PostgreSQL... (attempt {retry_count}/{max_retries})", flush=True)
        time.sleep(2)

print("Failed to connect to PostgreSQL after maximum retries", flush=True)
sys.exit(1)
ENDSCRIPT

    if [ $? -eq 0 ]; then
        echo "PostgreSQL connection verified!"
    else
        echo "Failed to connect to PostgreSQL"
        exit 1
    fi
}

# Function to run migrations
run_migrations() {
    echo "Running database migrations..."
    python manage.py migrate --noinput
}

# Function to collect static files
collect_static() {
    echo "Collecting static files..."
    # Clear existing static files to avoid permission issues
    rm -rf /app/staticfiles/*
    python manage.py collectstatic --noinput --clear
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