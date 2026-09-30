"""
Daily reminder email: what needs attention, so a deadline isn't missed just because nobody opened the app.

The email goes through an outside mail provider, so it names records by reference number only – never the
requester's name or an incident's description. The details stay in the app.
"""

from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from . import backups
from .models import AuditEntry, CompanyProfile, ComplianceTask, DataSubjectRequest, Incident

AUDIT_MODEL = "Reminder email"
DUE_SOON_DAYS = 7
PAIA_WARN_DAYS = 14


def enabled():
    return bool(settings.EMAIL_HOST)


def recipients():
    if settings.REMINDER_EMAIL:
        return list(settings.REMINDER_EMAIL)
    io_email = CompanyProfile.get().io_email
    return [io_email] if io_email else []


def _date(value):
    return f"{value.day} {value:%b %Y}"


def digest_items(today=None):
    """The lines of the reminder email, most urgent first. Empty when nothing needs attention."""
    from .views import paia_window  # avoid a circular import

    today = today or timezone.localdate()
    urgent, soon = [], []

    for incident in Incident.objects.exclude(status="closed"):
        if incident.needs_notification:
            urgent.append(f"{incident.reference}: breach not yet reported to the Regulator and affected people.")
        elif incident.notifiable == "unsure":
            soon.append(f"{incident.reference}: decide whether this breach must be reported.")

    for req in DataSubjectRequest.objects.filter(status__in=DataSubjectRequest.OPEN_STATUSES, due_date__isnull=False):
        kind = req.get_request_type_display().split(" (")[0].lower()
        if req.due_date < today:
            urgent.append(f"{req.reference} ({kind}) is overdue: it was due {_date(req.due_date)}.")
        elif req.due_date <= today + timedelta(days=DUE_SOON_DAYS):
            days = (req.due_date - today).days
            when = "today" if days == 0 else f"in {days} day{'s' if days != 1 else ''}"
            soon.append(f"{req.reference} ({kind}) is due {when} ({_date(req.due_date)}).")

    for task in ComplianceTask.objects.filter(done_on__isnull=True, due_date__lt=today):
        soon.append(f"Overdue task: {task.title} (was due {_date(task.due_date)}).")

    health = backups.health()
    if health["level"] != "ok":
        urgent.append(health["text"])

    window = paia_window(today)
    if window["open"] and window["days_left"] <= PAIA_WARN_DAYS:
        soon.append(f"The PAIA annual report is due by 30 June ({window['days_left']} days left).")

    return urgent + soon


def sent_today(today=None):
    today = today or timezone.localdate()
    return AuditEntry.objects.filter(model=AUDIT_MODEL, action="sent", at__date=today).exists()


def _link():
    return f"\n\nOpen the app: {settings.APP_URL}{reverse('compliance:dashboard')}" if settings.APP_URL else ""


def send_digest(today=None):
    """
    Send today's reminder email if it's due. Returns a short description of what happened.

    Sends at most once a day, only when something needs attention.
    """
    today = today or timezone.localdate()
    if not enabled():
        return "Reminders are off (EMAIL_HOST is not set)."
    to = recipients()
    if not to:
        return "No recipient: set REMINDER_EMAIL or the Information Officer's email in the company profile."
    if sent_today(today):
        return "Already sent today."
    items = digest_items(today)
    if not items:
        return "Nothing needs attention."

    count = len(items)
    subject = f"POPIA: {count} item{'s' if count != 1 else ''} need{'' if count != 1 else 's'} your attention"
    body = (
        f"{CompanyProfile.get().display_name} – POPIA reminders for {_date(today)}\n\n"
        + "\n".join(f"- {item}" for item in items)
        + _link()
        + "\n\nYou get this email once a day while something is overdue or due soon."
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, to)
    AuditEntry.objects.create(
        user="system", action="sent", model=AUDIT_MODEL, summary=f"{count} item(s) to {', '.join(to)}"[:300]
    )
    return f"Sent {count} item(s) to {', '.join(to)}."


def send_test(user):
    to = recipients()
    if not enabled() or not to:
        raise ValueError("Email reminders aren't set up.")
    send_mail(
        "POPIA: test email",
        "This is a test from your POPIA Compliance app. Reminder emails will reach this address." + _link(),
        settings.DEFAULT_FROM_EMAIL,
        to,
    )
    AuditEntry.objects.create(user=user, action="sent", model="Test email", summary=f"To {', '.join(to)}"[:300])
    return to
