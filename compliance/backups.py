"""
Database backups: making them, checking they can be restored, and reporting their health.

The backup container (scheduler) and the web app share the backup folder. The outcome of every attempt is
written to a small status file there, so the dashboard can warn when backups have stopped working.
"""

import gzip
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.utils import timezone

PATTERN = "popia-*.sqlite3.gz"
STATUS_FILE = ".backup-status.json"
STALE_AFTER = timedelta(hours=26)  # the scheduler backs up daily; allow for its hourly tick
TMP_MAX_AGE = 60 * 60

# Record counts shown after a restore test, so it's clear the backup holds real data.
COUNTED_TABLES = [
    ("compliance_checklistitem", "checklist item", "checklist items"),
    ("compliance_processingactivity", "processing activity", "processing activities"),
    ("compliance_datasubjectrequest", "request", "requests"),
    ("compliance_incident", "incident", "incidents"),
    ("compliance_auditentry", "audit log entry", "audit log entries"),
]


class BackupError(Exception):
    pass


def backup_dir():
    return Path(settings.BACKUP_DIR)


def database_path():
    return settings.DATABASES["default"]["NAME"]


def list_backups():
    folder = backup_dir()
    return sorted(folder.glob(PATTERN), reverse=True) if folder.exists() else []


def newest_backup():
    backups = list_backups()
    return backups[0] if backups else None


def check_database(path):
    """Open a database file and run SQLite's integrity check. Returns the record counts."""
    conn = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise BackupError(f"integrity check failed: {result}")
        counts = {}
        for table, singular, plural in COUNTED_TABLES:
            try:
                n = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            except sqlite3.OperationalError:
                n = 0
            counts[singular if n == 1 else plural] = n
        return counts
    except sqlite3.DatabaseError as exc:
        raise BackupError(f"not a readable database ({exc})") from exc
    finally:
        conn.close()


def create_backup(keep_days=30):
    """Copy the live database, check the copy, compress it and prune old backups. Returns the new file."""
    folder = backup_dir()
    folder.mkdir(parents=True, exist_ok=True)
    stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
    target = folder / f"popia-{stamp}.sqlite3.gz"
    try:
        # Everything is written under temporary names and renamed at the end, so an interrupted run
        # never leaves a half-written file that looks like a good backup.
        with tempfile.TemporaryDirectory(dir=folder, prefix=".tmp-") as tmp:
            copy = Path(tmp) / "copy.sqlite3"
            packed = Path(tmp) / "copy.sqlite3.gz"
            source = sqlite3.connect(database_path(), timeout=60)
            dest = sqlite3.connect(copy)
            try:
                with dest:
                    source.backup(dest)
            finally:
                dest.close()
                source.close()
            check_database(copy)
            with open(copy, "rb") as raw, gzip.open(packed, "wb") as out:
                shutil.copyfileobj(raw, out)
            packed.chmod(0o600)
            os.replace(packed, target)
    except Exception as exc:
        write_status(ok=False, message=str(exc) or exc.__class__.__name__)
        raise
    write_status(ok=True, message=f"{target.name} written and checked")
    prune(keep_days)
    return target


def prune(keep_days):
    folder = backup_dir()
    now = timezone.now().timestamp()
    for old in folder.glob(PATTERN):
        if old.stat().st_mtime < now - keep_days * 86400:
            old.unlink()
    # Leftovers from a run that was killed outright (power cut, SIGKILL).
    for stale in folder.glob(".tmp-*"):
        if stale.is_dir() and stale.stat().st_mtime < now - TMP_MAX_AGE:
            shutil.rmtree(stale, ignore_errors=True)


def try_restore(path):
    """Unpack a backup into a temporary file and check it opens. Returns the record counts."""
    # Unpack inside the backup folder, never the system temp folder: with the encrypted vault, that keeps
    # the data off the unencrypted disk.
    with tempfile.TemporaryDirectory(dir=backup_dir(), prefix=".tmp-restore-") as tmp:
        restored = Path(tmp) / "restored.sqlite3"
        try:
            with gzip.open(path, "rb") as packed, open(restored, "wb") as raw:
                shutil.copyfileobj(packed, raw)
        except (OSError, EOFError) as exc:
            raise BackupError(f"the file could not be unpacked ({exc})") from exc
        return check_database(restored)


def write_status(ok, message):
    status = {"at": timezone.now().isoformat(), "ok": ok, "message": message[:300]}
    path = backup_dir() / STATUS_FILE
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(status))
        os.replace(tmp, path)
    except OSError:
        pass  # the backup folder itself is the problem; the dashboard reports missing backups anyway


def read_status():
    try:
        status = json.loads((backup_dir() / STATUS_FILE).read_text())
        status["at"] = datetime.fromisoformat(status["at"])
        return status
    except (OSError, ValueError, KeyError, TypeError):
        return None


def health(now=None):
    """
    Summarise backup health for the dashboard and reminder emails.

    Returns {"level": "ok" | "warn" | "bad", "text": ..., "last_backup": datetime | None}.
    """
    now = now or timezone.now()
    newest = newest_backup()
    last = datetime.fromtimestamp(newest.stat().st_mtime, tz=timezone.get_current_timezone()) if newest else None
    status = read_status()

    if status and not status["ok"] and (last is None or status["at"] > last):
        return {"level": "bad", "text": f"The last backup failed: {status['message']}", "last_backup": last}
    if last is None:
        return {"level": "warn", "text": "No backup has been made yet.", "last_backup": None}
    if now - last > STALE_AFTER:
        days = max(1, (now - last).days)
        return {
            "level": "warn",
            "text": f"The newest backup is {days} day{'s' if days != 1 else ''} old. Daily backups may have stopped.",
            "last_backup": last,
        }
    return {"level": "ok", "text": "Backups are up to date.", "last_backup": last}
