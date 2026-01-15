release: python manage.py migrate --noinput && python manage.py create_test_data || true
web: python -m gunicorn gym_management.wsgi:application --bind 0.0.0.0:8000 --workers 4
