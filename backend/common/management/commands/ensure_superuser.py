from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
import os


class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get credentials from environment (fail if not set)
        try:
            username = os.environ['DJANGO_SUPERUSER_USERNAME']
            email = os.environ['DJANGO_SUPERUSER_EMAIL']
            password = os.environ['DJANGO_SUPERUSER_PASSWORD']
        except KeyError as e:
            raise ImproperlyConfigured(
                f'Missing environment variable: {e}. '
                'Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, '
                'and DJANGO_SUPERUSER_PASSWORD in your .env file.'
            )
        
        # Check for placeholder values from .env.example
        placeholder_values = [
            '<unique_admin_username>',
            'your-email@example.com',
            '<generate-strong-password-here>',
            '<generate-password-here>',
        ]
        
        if username in placeholder_values:
            raise ImproperlyConfigured(
                f'DJANGO_SUPERUSER_USERNAME is set to placeholder value "{username}". '
                'Replace with actual username in your .env file.'
            )
        
        if email in placeholder_values:
            raise ImproperlyConfigured(
                f'DJANGO_SUPERUSER_EMAIL is set to placeholder value "{email}". '
                'Replace with actual email in your .env file.'
            )
        
        if password in placeholder_values:
            raise ImproperlyConfigured(
                f'DJANGO_SUPERUSER_PASSWORD is set to placeholder value. '
                'Generate a strong password and set it in your .env file.'
            )
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" created')
            )
        else:
            self.stdout.write(f'Superuser "{username}" already exists')