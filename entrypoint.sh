set -e

echo "Waiting for MySQL..."

while ! nc -z "${MYSQL_HOST}" "${MYSQL_PORT}"; do
  sleep 0.1
done

echo "MySQL started"

echo "Migrating the database at startup"
alembic upgrade head

echo "Starting Gunicorn server"
gunicorn main:app -w ${GUNICORN_WORKERS:-4} -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 --access-logfile - --error-logfile - --log-level info
