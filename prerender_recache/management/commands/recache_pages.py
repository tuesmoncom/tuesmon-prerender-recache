from django.core.management.base import BaseCommand, CommandError
from prerender_recache.service import process_scheduled_recaches
from django_pglocks import advisory_lock


class Command(BaseCommand):
    help = 'Recache all pending pages'

    def handle(self, *args, **options):
        with advisory_lock("reache_pages", wait=False) as acquired:
            if acquired:
                process_scheduled_recaches()
            else:
                print("Other recache process running")
