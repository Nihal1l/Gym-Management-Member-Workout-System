#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_management.settings')
django.setup()

from gym_api.models import User

# Update superadmin to have staff privileges
user = User.objects.get(email='superadmin@gym.com')
user.is_staff = True
user.is_superuser = True
user.save()
print(f"✓ Updated {user.email}")
print(f"  is_staff: {user.is_staff}")
print(f"  is_superuser: {user.is_superuser}")
