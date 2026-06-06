web: python manage.py migrate --noinput && python manage.py setup_groups && gunicorn shop_project.wsgi --bind 0.0.0.0:$PORT
