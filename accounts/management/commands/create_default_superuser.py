from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = "Create the default superuser with first/last name"

    def handle(self, *args, **kwargs):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        first_name = os.getenv("DJANGO_SUPERUSER_FIRSTNAME")
        last_name = os.getenv("DJANGO_SUPERUSER_LASTNAME")

        if not username or not password:
            self.stdout.write(self.style.ERROR("Missing required env variables for superuser"))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING("Superuser already exists"))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='admin',
            first_name=first_name,
            last_name=last_name
        )

        self.stdout.write(self.style.SUCCESS("Superuser created successfully"))
