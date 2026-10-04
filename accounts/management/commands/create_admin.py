from django.core.management.base import BaseCommand
from accounts.models import CustomUser

class Command(BaseCommand):
    help = "Create default admin superuser for Chavara Living"

    def handle(self, *args, **kwargs):
        if not CustomUser.objects.filter(username="admin").exists():
            CustomUser.objects.create_superuser(
                username="admin",
                password="admin123",
                email="admin@chavaraliving.com",
                role="admin",
                first_name="Admin",
                last_name="Chavara"
            )
            self.stdout.write(self.style.SUCCESS("Admin user created: admin / admin123"))
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists."))
