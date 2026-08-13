from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from members.models import Contributor


class Command(BaseCommand):
    help = "Create or update contributor login accounts"

    accounts = [
        ("achanolympia", "Achan Olympia Happy", "achanolympia@456"),
        ("alarasamson", "Alarm Samson", "alarasamson@456"),
        ("annakoth", "Ann Akoth", "annakoth@456"),
    ]

    def handle(self, *args, **options):
        User = get_user_model()

        for username, name, password in self.accounts:

            contributor = Contributor.objects.filter(
                full_name=name
            ).first()

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                },
            )

            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.set_password(password)

            if contributor and contributor.email:
                user.email = contributor.email

            user.save()

            if contributor:
                contributor.user = user
                contributor.save(update_fields=["user"])
                result = f"{'Created' if created else 'Updated'} {username} -> {name}"
            else:
                result = (
                    f"{'Created' if created else 'Updated'} {username}; "
                    f"Contributor '{name}' not found, so account was not linked."
                )

            self.stdout.write(self.style.SUCCESS(result))
