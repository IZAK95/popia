import logging
import signal
import threading
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import close_old_connections
from django.utils import timezone

from compliance import backups, reminders

log = logging.getLogger(__name__)

TICK = 60 * 60  # wake up every hour
BACKUP_EVERY = timedelta(hours=23)


class Command(BaseCommand):
    help = "Run the daily jobs: a database backup and the reminder email. Wakes every hour and stops on SIGTERM."

    def add_arguments(self, parser):
        parser.add_argument("--keep-days", type=int, default=30)
        parser.add_argument("--once", action="store_true", help="Run the jobs that are due once, then exit.")

    def handle(self, *args, keep_days, once, **options):
        # In the container this process is PID 1, which ignores SIGTERM unless it has a handler.
        # Without one, `docker stop` waits 10 s and then kills it, possibly halfway through a backup.
        stop = threading.Event()
        if not once:
            for sig in (signal.SIGTERM, signal.SIGINT):
                signal.signal(sig, lambda *_: stop.set())

        while not stop.is_set():
            self.tick(keep_days)
            if once:
                return
            stop.wait(TICK)
        self.stdout.write("Scheduler stopped.")

    def tick(self, keep_days):
        # Each job is independent: a failing backup must not stop the reminder that reports it.
        close_old_connections()
        try:
            newest = backups.newest_backup()
            age = timezone.now().timestamp() - newest.stat().st_mtime if newest else None
            if age is None or age >= BACKUP_EVERY.total_seconds():
                target = backups.create_backup(keep_days)
                self.stdout.write(f"Backup written: {target}")
        except Exception:
            log.exception("Backup failed; trying again in an hour")

        try:
            if timezone.localtime().hour >= settings.REMINDER_HOUR:
                self.stdout.write(f"Reminders: {reminders.send_digest()}")
        except Exception:
            log.exception("Sending the reminder email failed; trying again in an hour")
        close_old_connections()
