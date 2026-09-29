import gzip
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Make a consistent, gzipped copy of the SQLite database and prune old copies."

    def add_arguments(self, parser):
        parser.add_argument("--keep-days", type=int, default=30)
        parser.add_argument("--loop", action="store_true", help="Run forever, once every 24 hours.")

    def handle(self, *args, keep_days, loop, **options):
        while True:
            self.backup(keep_days)
            if not loop:
                return
            time.sleep(24 * 60 * 60)

    def backup(self, keep_days):
        backup_dir = Path(settings.BACKUP_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)
        source = sqlite3.connect(settings.DATABASES["default"]["NAME"])
        stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
        target = backup_dir / f"popia-{stamp}.sqlite3.gz"
        with tempfile.NamedTemporaryFile(dir=backup_dir, suffix=".tmp") as tmp:
            dest = sqlite3.connect(tmp.name)
            with dest:
                source.backup(dest)
            dest.close()
            source.close()
            with open(tmp.name, "rb") as raw, gzip.open(target, "wb") as packed:
                shutil.copyfileobj(raw, packed)
        target.chmod(0o600)

        cutoff = time.time() - keep_days * 86400
        for old in backup_dir.glob("popia-*.sqlite3.gz"):
            if old.stat().st_mtime < cutoff:
                old.unlink()
        self.stdout.write(self.style.SUCCESS(f"Backup written: {target}"))
