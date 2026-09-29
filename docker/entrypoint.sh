#!/bin/sh
set -e

# The app runs as an unprivileged user (UID 1000). If Docker created a mounted
# folder as root, stop with a clear fix instead of a database error.
for dir in /data /backups; do
  if [ "${REQUIRE_VAULT:-0}" = "1" ] && ! [ -f "$dir/.popia-vault" ]; then
    echo "ERROR: $dir is not inside the unlocked encrypted vault. Run: scripts/popia-vault.sh unlock" >&2
    exit 1
  fi
  if [ -d "$dir" ] && ! [ -w "$dir" ]; then
    echo "ERROR: the app (UID $(id -u)) cannot write to $dir." >&2
    echo "Fix it on the host, in the app folder:  sudo chown -R $(id -u):$(id -g) data backups" >&2
    exit 1
  fi
done

# Prepare the database on every start: apply migrations, refresh the POPIA
# checklist content and create the first admin user if requested.
python manage.py migrate --noinput
python manage.py seed_popia
python manage.py ensure_admin
exec "$@"
