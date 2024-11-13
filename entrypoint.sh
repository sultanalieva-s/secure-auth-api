#!/bin/sh

set -e  # Exit immediately if a command exits with a non-zero status

echo "Waiting for MySQL..."

# Wait until PostgreSQL is reachable
while ! nc -z "${MYSQL_HOST}" "${MYSQL_PORT}"; do
  sleep 0.1
done

echo "MySQL started"

# Run migrations
echo "Migrating the database at startup"
alembic upgrade head

# Start the application
echo "Starting Gunicorn server"
gunicorn main:app -w ${GUNICORN_WORKERS:-4} -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 --access-logfile - --error-logfile - --log-level info
