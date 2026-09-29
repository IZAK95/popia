import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the admin account from ADMIN_USERNAME / ADMIN_PASSWORD / ADMIN_EMAIL if no user exists yet."

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.exists():
            self.stdout.write("A user already exists; nothing to do.")
            return
        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")
        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "No users yet. Set ADMIN_USERNAME and ADMIN_PASSWORD, or run: python manage.py createsuperuser"
                )
            )
            return
        User.objects.create_superuser(username=username, email=os.environ.get("ADMIN_EMAIL", ""), password=password)
        self.stdout.write(self.style.SUCCESS(f"Created admin user '{username}'. Remove ADMIN_PASSWORD from .env now."))
