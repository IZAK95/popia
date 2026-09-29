from django.core.management.base import BaseCommand

from compliance.seed import seed_all


class Command(BaseCommand):
    help = "Load/refresh the POPIA checklist and first-run example content (safe to run repeatedly)."

    def handle(self, *args, **options):
        seed_all()
        self.stdout.write(self.style.SUCCESS("POPIA framework content is up to date."))
