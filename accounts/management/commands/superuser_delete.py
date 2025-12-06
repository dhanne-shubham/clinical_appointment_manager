from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os   # ← MISSING IMPORT (now added)

User = get_user_model()

class Command(BaseCommand):
    help = "Delete the superuser defined by DJANGO_SUPERUSER_USERNAME"

    def handle(self, *args, **kwargs):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")

        if not username:
            self.stdout.write(self.style.ERROR("DJANGO_SUPERUSER_USERNAME not provided in environment"))
            return

        try:
            user = User.objects.get(username=username, is_superuser=True)
            user.delete()
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' deleted successfully"))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Superuser '{username}' does not exist"))
