import os

bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = 4
worker_class = "sync"
threads = 2
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Django
env = {
    'DJANGO_SETTINGS_MODULE': 'gym_management.settings'
}
