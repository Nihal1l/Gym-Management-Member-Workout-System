release: pip install --upgrade pip setuptools wheel && python manage.py migrate --noinput && python manage.py create_test_data
web: gunicorn gym_management.wsgi
