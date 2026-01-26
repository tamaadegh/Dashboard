#!/bin/sh

set -e

# Apply Tamaade logo
python /backend/scripts/apply_tamaade_logo.py

# Create and apply database migrations
echo "Creating database migrations..."
python manage.py makemigrations --noinput

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear


# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn nxtbn.wsgi:application --bind :8000 --timeout 120 --workers 3
