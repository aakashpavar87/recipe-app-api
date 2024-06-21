"""
Django Command to wait for database until its available.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Management Commands"""

    def handle(self, *args, **options):
        pass
