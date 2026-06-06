#!/bin/sh
set -e
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py setup_groups
exec gunicorn shop_project.wsgi --bind "0.0.0.0:${PORT:-8000}"
