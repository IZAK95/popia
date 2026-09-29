FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/data \
    BACKUP_DIR=/backups

WORKDIR /app

# UID 1000 matches the first user on most Linux desktops, so ./data and ./backups stay writable.
RUN groupadd --gid 1000 app && useradd --uid 1000 --gid app --home /app --no-create-home app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN SECRET_KEY=build-only python manage.py collectstatic --noinput -v0 \
    && mkdir -p /data /backups && chown -R app:app /data /backups \
    && chmod +x docker/entrypoint.sh

USER app
EXPOSE 8000
VOLUME ["/data", "/backups"]
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')" || exit 1

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--no-control-socket"]
