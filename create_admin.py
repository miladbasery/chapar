import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

ADMIN_USER = os.getenv('DJANGO_SUPERUSER_USERNAME')
ADMIN_EMAIL = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
ADMIN_PASS = os.getenv('DJANGO_SUPERUSER_PASSWORD')

if ADMIN_USER and ADMIN_PASS:
    if not User.objects.filter(username=ADMIN_USER).exists():
        User.objects.create_superuser(ADMIN_USER, ADMIN_EMAIL, ADMIN_PASS)
        print(f"Admin user '{ADMIN_USER}' created successfully!")
    else:
        print(f"Admin user '{ADMIN_USER}' already exists.")
else:
    print("Admin credentials not provided in environment variables. Skipping creation.")