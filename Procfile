release: python manage.py migrate --noinput && python manage.py create_test_data || true
web: gunicorn -c gunicorn_config.py gym_management.wsgi:application
