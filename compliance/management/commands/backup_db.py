from django.core.management.base import BaseCommand, CommandError

from compliance import backups


class Command(BaseCommand):
    help = "Make a consistent, checked, gzipped copy of the SQLite database and prune old copies."

    def add_arguments(self, parser):
        parser.add_argument("--keep-days", type=int, default=30)

    def handle(self, *args, keep_days, **options):
        try:
            target = backups.create_backup(keep_days)
        except Exception as exc:
            raise CommandError(f"Backup failed: {exc}") from exc
        self.stdout.write(self.style.SUCCESS(f"Backup written: {target}"))
