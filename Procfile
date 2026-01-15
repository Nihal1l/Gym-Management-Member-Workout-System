release: pip install --upgrade pip setuptools wheel && python manage.py migrate --noinput && python manage.py create_test_data
web: DJANGO_SETTINGS_MODULE=gym_management.settings gunicorn --bind=0.0.0.0:$PORT --workers=4 gym_management.wsgi:application
