#!/bin/sh
set -e
# Prepare the database on every start: apply migrations, refresh the POPIA
# checklist content and create the first admin user if requested.
python manage.py migrate --noinput
python manage.py seed_popia
python manage.py ensure_admin
exec "$@"
