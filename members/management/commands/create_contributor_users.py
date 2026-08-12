from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from members.models import Contributor


class Command(BaseCommand):
    help = "Create and link contributor login accounts"

    accounts = [
        ("achanolympia", "Achan Olympia Happy", "achanolympia@456"),
        ("alarasamson", "Alarm Samson", "alarasamson@456"),
        ("annakoth", "Ann Akoth", "annakoth@456"),
    ]

    def handle(self, *args, **options):
        User = get_user_model()

        for username, name, password in self.accounts:
            contributor = Contributor.objects.get(full_name=name)

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": contributor.email,
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                },
            )

            user.email = contributor.email
            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.set_password(password)
            user.save()

            contributor.user = user
            contributor.save(update_fields=["user"])

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Updated'} {username} -> {name}"
                )
            )
