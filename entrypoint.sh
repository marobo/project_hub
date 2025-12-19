#!/bin/bash
set -e

echo "Running database migrations..."
if ! python manage.py migrate --noinput 2>&1 | tee /tmp/migrate.log; then
    if grep -q "already exists" /tmp/migrate.log; then
        echo "Table already exists, faking migrations..."
        python manage.py migrate --fake
    else
        echo "Migration failed with unexpected error"
        cat /tmp/migrate.log
        exit 1
    fi
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn project_hub.wsgi:application --bind 0.0.0.0:8000
