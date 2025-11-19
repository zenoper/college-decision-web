#!/bin/bash
set -e

echo "Starting entrypoint script..."

# Run migrations
echo "Running migrations..."
python manage.py migrate --no-input

# Collect static files
echo "Running collectstatic..."
python manage.py collectstatic --no-input --verbosity 2

# Start Gunicorn
echo "Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn collegedecisionweb.wsgi:application --bind 0.0.0.0:${PORT:-8000} --log-level info --access-logfile - --error-logfile -
