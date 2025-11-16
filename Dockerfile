# Use Python 3.11 slim as base image
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
# Note: psycopg2-binary doesn't require PostgreSQL dev packages
# Only installing gcc for potential other package compilations
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Copy project code
COPY . .

# Change ownership of app directory
RUN chown -R app:app /app
USER app

# Expose port (Railway will set $PORT dynamically)
EXPOSE 8000

# Health check (using curl installed above)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

# Run migrations and start application
# Use $PORT environment variable (defaults to 8000 for local development)
CMD sh -c "python manage.py migrate --no-input --run-syncdb && python manage.py collectstatic --no-input && gunicorn collegedecisionweb.wsgi:application --bind 0.0.0.0:${PORT:-8000}"
