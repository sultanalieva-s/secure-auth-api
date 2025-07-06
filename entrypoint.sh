#!/bin/bash
set -e

echo "⏳ Waiting for MySQL..."
while ! nc -z "$MYSQL_HOST" "$MYSQL_PORT"; do
  sleep 0.5
done

echo "✅ MySQL started"
echo "🚀 Starting Gunicorn server..."

uv run fastapi run app/main.py --host 0.0.0.0 --port 8080
