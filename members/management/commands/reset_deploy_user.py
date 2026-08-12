import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or reset the deployment user."

    def handle(self, *args, **options):
        username = os.environ.get("DEPLOY_ADMIN_USERNAME")
        password = os.environ.get("DEPLOY_ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DEPLOY_ADMIN_USERNAME or DEPLOY_ADMIN_PASSWORD not set; skipping."
                )
            )
            return

        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        action = "created" if created else "password reset"
        self.stdout.write(
            self.style.SUCCESS(
                f"Deployment user '{username}' {action} successfully."
            )
        )
