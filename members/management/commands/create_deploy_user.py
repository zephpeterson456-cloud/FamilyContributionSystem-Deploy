import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update the deployment admin user"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DEPLOY_ADMIN_USERNAME")
        password = os.environ.get("DEPLOY_ADMIN_PASSWORD")
        email = os.environ.get("DEPLOY_ADMIN_EMAIL", "")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DEPLOY_ADMIN_USERNAME or DEPLOY_ADMIN_PASSWORD is not set."
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "created" if created else "updated"

        self.stdout.write(
            self.style.SUCCESS(
                f"Deployment user '{username}' {action} successfully."
            )
        )
