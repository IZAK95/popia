import gzip
import logging
import os
import shutil
import signal
import sqlite3
import tempfile
import threading
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

log = logging.getLogger(__name__)

DAY = 24 * 60 * 60
RETRY_AFTER = 60 * 60  # after a failed backup, try again in an hour instead of waiting a day


class Command(BaseCommand):
    help = "Make a consistent, gzipped copy of the SQLite database and prune old copies."

    def add_arguments(self, parser):
        parser.add_argument("--keep-days", type=int, default=30)
        parser.add_argument("--loop", action="store_true", help="Run forever, once every 24 hours.")

    def handle(self, *args, keep_days, loop, **options):
        if not loop:
            self.backup(keep_days)
            return

        # In the backup container this process is PID 1, which ignores SIGTERM unless it has a handler.
        # Without one, `docker stop` waits 10 s and then kills it, possibly halfway through a backup.
        stop = threading.Event()
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda *_: stop.set())

        while not stop.is_set():
            try:
                self.backup(keep_days)
                wait = DAY
            except Exception:
                # Keep the loop alive: a full disk or a locked vault must not end daily backups for good.
                log.exception("Backup failed; retrying in %s minutes", RETRY_AFTER // 60)
                wait = RETRY_AFTER
            stop.wait(wait)
        self.stdout.write("Backup loop stopped.")

    def backup(self, keep_days):
        backup_dir = Path(settings.BACKUP_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
        target = backup_dir / f"popia-{stamp}.sqlite3.gz"

        # Everything is written under temporary names and renamed at the end, so an interrupted run
        # never leaves a half-written file that looks like a good backup.
        with tempfile.TemporaryDirectory(dir=backup_dir, prefix=".tmp-") as tmp:
            copy = Path(tmp) / "copy.sqlite3"
            packed = Path(tmp) / "copy.sqlite3.gz"
            source = sqlite3.connect(settings.DATABASES["default"]["NAME"], timeout=60)
            dest = sqlite3.connect(copy)
            try:
                with dest:
                    source.backup(dest)
            finally:
                dest.close()
                source.close()
            with open(copy, "rb") as raw, gzip.open(packed, "wb") as out:
                shutil.copyfileobj(raw, out)
            packed.chmod(0o600)
            os.replace(packed, target)

        now = timezone.now().timestamp()
        cutoff = now - keep_days * DAY
        for old in backup_dir.glob("popia-*.sqlite3.gz"):
            if old.stat().st_mtime < cutoff:
                old.unlink()
        # Leftovers from a run that was killed outright (power cut, SIGKILL).
        for stale in backup_dir.glob(".tmp-*"):
            if stale.is_dir() and stale.stat().st_mtime < now - RETRY_AFTER:
                shutil.rmtree(stale, ignore_errors=True)
        self.stdout.write(self.style.SUCCESS(f"Backup written: {target}"))
