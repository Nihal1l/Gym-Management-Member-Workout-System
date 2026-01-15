"""
Django command to initialize project.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_management.settings')
django.setup()

from django.core.management import execute_from_command_line
import sys

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
