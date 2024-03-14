from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a superuser'

    def handle(self, *args, **options):
        User = get_user_model()
        User.objects.create_superuser(email='superuser@example.com', password='password')
        self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
