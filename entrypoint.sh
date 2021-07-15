#!/usr/bin/env bash
#!/bin/sh

apt-get update && apt-get install -y netcat
echo "Waiting for postgres..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done

echo "PostgreSQL started"

#python manage.py collectstatic --no-input
python manage.py migrate
gunicorn -b 0.0.0.0:8000 cxbootcamp_django_example.wsgi --timeout 300 --worker-class=gevent --worker-connections=1000 --workers=5

exec "$@"
