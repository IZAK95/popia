from datetime import date

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.core import serializers
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import generic
from django.views.decorators.http import require_POST

from . import backups, documents, reminders
from .models import (
    AuditEntry,
    ChecklistItem,
    CompanyProfile,
    ComplianceTask,
    DataSubjectRequest,
    Incident,
    Operator,
    ProcessingActivity,
    RetentionRule,
    Risk,
    TrainingRecord,
)
from .registers import Column, Register, formfield_callback

# ---------------------------------------------------------------------------
# Register definitions
# ---------------------------------------------------------------------------

REVIEW_BADGE = {"draft": "warn", "confirmed": "ok"}

ACTIVITIES = Register(
    slug="activity",
    prefix="processing/",
    model=ProcessingActivity,
    title="Processing register",
    singular="processing activity",
    intro=(
        "A list of everything your business does with personal information – POPIA calls this documenting your "
        "'processing operations' (s17). Start by reviewing the draft examples below: fix anything that doesn't match "
        "your business, then mark each one Confirmed. Add activities that are missing."
    ),
    help_page="conditions",
    fields=[
        "name", "data_subjects", "personal_info", "purpose", "lawful_basis", "lawful_basis_notes", "source",
        "special_info", "special_info_details", "children_info", "recipients", "operators", "cross_border",
        "retention", "security_measures", "notice_given", "owner", "last_reviewed", "review_status",
    ],
    columns=[
        Column("Activity", "name"),
        Column("Whose information", "data_subjects"),
        Column("Lawful ground", "lawful_basis"),
        Column("Special info", "special_info"),
        Column("Open issues", "issues"),
        Column("Status", "review_status", REVIEW_BADGE),
    ],
)

OPERATORS = Register(
    slug="operator",
    prefix="operators/",
    model=Operator,
    title="Operators (service providers)",
    singular="operator",
    intro=(
        "An 'operator' is any outside business that processes personal information on your behalf – cloud email, "
        "payroll software, your accountant, IT support. POPIA requires a written agreement with each one (s21), and "
        "if they store information outside South Africa you must record the legal basis (s72)."
    ),
    help_page="conditions",
    fields=[
        "name", "service", "personal_info", "data_location", "outside_sa", "transfer_basis", "agreement_in_place",
        "agreement_date", "agreement_location", "notes", "next_review", "review_status",
    ],
    columns=[
        Column("Provider", "name"),
        Column("Service", "service"),
        Column("Outside SA", "outside_sa"),
        Column("Agreement", "agreement_in_place"),
        Column("Open issues", "issues"),
        Column("Status", "review_status", REVIEW_BADGE),
    ],
)

RETENTION = Register(
    slug="retention",
    prefix="retention/",
    model=RetentionRule,
    title="Retention schedule",
    singular="retention rule",
    intro=(
        "POPIA says you may not keep personal information longer than you need it (s14) – but other laws say you "
        "must keep some records for a minimum time. This schedule combines both. 'Legal minimum' rows come from "
        "South African legislation; 'Business policy' rows are sensible defaults you may change. Confirm the list "
        "with your accountant once."
    ),
    help_page="conditions",
    fields=["record_type", "examples", "period", "starts_from", "legal_source", "kind", "disposal", "order"],
    columns=[
        Column("Record", "record_type"),
        Column("Keep for", "period"),
        Column("From", "starts_from"),
        Column("Source", "legal_source"),
        Column("Type", "kind", {"statutory": "info", "policy": ""}),
    ],
)

def risk_heatmap(risks):
    open_risks = [r for r in risks if r.status != "closed"]
    heat = []
    for likelihood in range(5, 0, -1):
        cells = []
        for impact in range(1, 6):
            score = likelihood * impact
            level = "high" if score >= 15 else "medium" if score >= 8 else "low"
            count = sum(1 for r in open_risks if r.likelihood == likelihood and r.impact == impact)
            cells.append({"level": level, "count": count})
        heat.append({"likelihood": likelihood, "cells": cells})
    return {"heat": heat}


def task_groups(tasks):
    return {
        "open_tasks": [t for t in tasks if not t.done_on],
        "done_tasks": sorted((t for t in tasks if t.done_on), key=lambda t: t.done_on, reverse=True)[:20],
        "reminders": {
            "enabled": reminders.enabled(),
            "recipients": reminders.recipients(),
            "hour": settings.REMINDER_HOUR,
            "last": AuditEntry.objects.filter(model=reminders.AUDIT_MODEL, action="sent").first(),
        },
    }


RISKS = Register(
    slug="risk",
    prefix="risks/",
    model=Risk,
    title="Risk register",
    singular="risk",
    intro=(
        "Your personal information impact assessment: what could go wrong, how likely it is, how badly people "
        "could be harmed, and what you do about it (Regulation 4(1)(b), POPIA s19). Score = likelihood × impact."
    ),
    help_page="conditions",
    fields=["title", "description", "activity", "likelihood", "impact", "mitigation", "owner", "status", "review_date", "review_status"],
    columns=[
        Column("Risk", "title"),
        Column("Likelihood", "likelihood"),
        Column("Impact", "impact"),
        Column("Score", "score"),
        Column("Level", "level", {"high": "bad", "medium": "warn", "low": "ok"}),
        Column("Status", "status"),
    ],
    list_template="compliance/risk_list.html",
    list_context=risk_heatmap,
)

REQUESTS = Register(
    slug="request",
    prefix="requests/",
    model=DataSubjectRequest,
    title="Requests from people",
    singular="request",
    intro=(
        "Log every request from a person about their information – access, correction, deletion, objection, "
        "marketing opt-outs and complaints – no matter how it arrived (email, WhatsApp, phone). The due date is "
        "calculated automatically (30 days). These records also produce your annual PAIA report."
    ),
    help_page="rights",
    fields=[
        "request_type", "requester_name", "requester_contact", "received_on", "channel", "identity_verified",
        "details", "due_date", "status", "outcome", "refusal_grounds", "completed_on", "response_notes",
    ],
    columns=[
        Column("Ref", "reference"),
        Column("Type", "request_type"),
        Column("From", "requester_name"),
        Column("Received", "received_on"),
        Column("Due", "due_date"),
        Column("Status", "status", {"new": "warn", "in_progress": "info", "extended": "warn", "completed": "ok"}),
    ],
    detail_template="compliance/request_detail.html",
)

INCIDENTS = Register(
    slug="incident",
    prefix="incidents/",
    model=Incident,
    title="Incidents & breaches",
    singular="incident",
    intro=(
        "Log every security incident, even suspected ones and near-misses. The app walks you through what POPIA "
        "s22 requires: contain, assess, notify the Information Regulator (eServices portal) and the affected "
        "people as soon as reasonably possible, and learn from it."
    ),
    help_page="breaches",
    fields=[
        "title", "discovered_on", "occurred_on", "reported_by", "cause", "description", "personal_info_affected",
        "people_affected", "containment", "notifiable", "regulator_notified_on", "regulator_reference",
        "subjects_notified_on", "subjects_notification_method", "status", "lessons_learned", "closed_on",
    ],
    columns=[
        Column("Ref", "reference"),
        Column("Incident", "title"),
        Column("Discovered", "discovered_on"),
        Column("Notifiable", "notifiable", {"yes": "bad", "unsure": "warn", "no": "ok"}),
        Column("Status", "status", {"open": "bad", "contained": "warn", "notified": "info", "closed": "ok"}),
    ],
    detail_template="compliance/incident_detail.html",
)

TRAINING = Register(
    slug="training",
    prefix="training/",
    model=TrainingRecord,
    title="Training log",
    singular="training session",
    intro=(
        "Evidence that staff have been made aware of POPIA (Regulation 4(1)(e)). Hold a short session at least "
        "once a year and for every new hire. The 'POPIA in plain language' pages make a good script."
    ),
    help_page="basics",
    fields=["date", "topic", "attendees", "delivered_by", "materials", "notes"],
    columns=[Column("Date", "date"), Column("Topic", "topic"), Column("Attendees", "attendee_count"), Column("Delivered by", "delivered_by")],
)

TASKS = Register(
    slug="task",
    prefix="tasks/",
    model=ComplianceTask,
    title="Tasks & deadlines",
    singular="task",
    intro="Your compliance calendar. Recurring tasks re-schedule themselves when you mark them done.",
    fields=["title", "details", "due_date", "recurrence", "done_on"],
    columns=[],
    list_template="compliance/task_list.html",
    list_context=task_groups,
)

REGISTERS = [ACTIVITIES, OPERATORS, RETENTION, RISKS, REQUESTS, INCIDENTS, TRAINING, TASKS]


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


def checklist_progress(items):
    applicable = [i for i in items if i.status != ChecklistItem.NA]
    done = [i for i in applicable if i.status == ChecklistItem.DONE]
    return {
        "total": len(applicable),
        "done": len(done),
        "percent": round(100 * len(done) / len(applicable)) if applicable else 100,
    }


def paia_window(today):
    """The PAIA s83(4) report window runs 1 April – 30 June."""
    start, end = date(today.year, 4, 1), date(today.year, 6, 30)
    return {"open": start <= today <= end, "start": start, "end": end, "days_left": (end - today).days}


def dashboard(request):
    today = timezone.localdate()
    profile = CompanyProfile.get()
    items = list(ChecklistItem.objects.all())
    essential = [i for i in items if i.essential]

    alerts = []
    if not profile.io_registered:
        gov02 = next((i for i in items if i.code == "GOV-02"), None)
        target = ("compliance:checklist_item", gov02.pk) if gov02 else ("compliance:profile", None)
        alerts.append(("bad", "Your Information Officer is not yet registered with the Information Regulator.", *target))
    for incident in Incident.objects.exclude(status="closed"):
        if incident.needs_notification:
            alerts.append(("bad", f"{incident.reference}: notify the Regulator and affected people as soon as reasonably possible.", "compliance:incident_detail", incident.pk))
        elif incident.notifiable == "unsure":
            alerts.append(("warn", f"{incident.reference}: decide whether this breach must be reported.", "compliance:incident_detail", incident.pk))
    for req in DataSubjectRequest.objects.filter(status__in=DataSubjectRequest.OPEN_STATUSES):
        if req.is_overdue:
            alerts.append(("bad", f"{req.reference} from {req.requester_name} is overdue (was due {req.due_date:%d %b %Y}).", "compliance:request_detail", req.pk))
        elif req.days_left is not None and req.days_left <= 7:
            alerts.append(("warn", f"{req.reference} from {req.requester_name} is due in {req.days_left} day(s).", "compliance:request_detail", req.pk))
    for task in ComplianceTask.objects.filter(done_on__isnull=True, due_date__lt=today):
        alerts.append(("warn", f"Overdue task: {task.title} (due {task.due_date:%d %b %Y}).", "compliance:task_list", None))
    backup_health = backups.health()
    if backup_health["level"] != "ok":
        alerts.append((backup_health["level"], backup_health["text"], "compliance:export", None))
    window = paia_window(today)
    if window["open"]:
        alerts.append(("info", f"The PAIA annual report window is open – submit by 30 June ({window['days_left']} days left).", "compliance:paia_report", None))

    drafts = sum(m.objects.filter(review_status="draft").count() for m in (ProcessingActivity, Operator, Risk))

    areas = []
    for code, label in ChecklistItem.AREAS:
        area_items = [i for i in items if i.area == code]
        areas.append({"code": code, "label": label, **checklist_progress(area_items)})

    context = {
        "profile": profile,
        "overall": checklist_progress(items),
        "essential": checklist_progress(essential),
        "next_steps": [i for i in items if i.essential and i.status in (ChecklistItem.TODO, ChecklistItem.PROGRESS)][:6],
        "alerts": alerts,
        "areas": areas,
        "drafts": drafts,
        "upcoming": ComplianceTask.objects.filter(done_on__isnull=True).order_by("due_date")[:6],
        "counts": {
            "activities": ProcessingActivity.objects.count(),
            "operators": Operator.objects.count(),
            "open_requests": DataSubjectRequest.objects.filter(status__in=DataSubjectRequest.OPEN_STATUSES).count(),
            "open_incidents": Incident.objects.exclude(status="closed").count(),
            "high_risks": sum(1 for r in Risk.objects.exclude(status="closed") if r.level == "high"),
        },
        "is_new": profile.completeness < 50,
    }
    return render(request, "compliance/dashboard.html", context)


# ---------------------------------------------------------------------------
# Checklist
# ---------------------------------------------------------------------------


def checklist(request):
    status = request.GET.get("status", "")
    items = list(ChecklistItem.objects.all())
    groups = []
    for code, label in ChecklistItem.AREAS:
        area_items = [i for i in items if i.area == code]
        shown = [i for i in area_items if not status or i.status == status]
        if shown:
            groups.append({"label": label, "items": shown, **checklist_progress(area_items)})
    return render(
        request,
        "compliance/checklist.html",
        {"groups": groups, "overall": checklist_progress(items), "status": status, "statuses": ChecklistItem.STATUSES},
    )


class ChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ["status", "evidence"]
        widgets = {"status": forms.RadioSelect, "evidence": forms.Textarea(attrs={"rows": 4})}


def checklist_item(request, pk):
    item = get_object_or_404(ChecklistItem, pk=pk)
    form = ChecklistItemForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{item.code} updated.")
        following = ChecklistItem.objects.filter(order__gt=item.order).exclude(status__in=["done", "na"]).first()
        if "next" in request.POST and following:
            return redirect("compliance:checklist_item", pk=following.pk)
        return redirect("compliance:checklist")
    siblings = list(ChecklistItem.objects.values_list("pk", flat=True))
    index = siblings.index(item.pk)
    return render(
        request,
        "compliance/checklist_item.html",
        {
            "item": item,
            "form": form,
            "prev_pk": siblings[index - 1] if index > 0 else None,
            "next_pk": siblings[index + 1] if index + 1 < len(siblings) else None,
            "position": index + 1,
            "count": len(siblings),
        },
    )


# ---------------------------------------------------------------------------
# Company profile
# ---------------------------------------------------------------------------


ProfileForm = forms.modelform_factory(
    CompanyProfile, exclude=["created_at", "updated_at"], formfield_callback=formfield_callback
)


def profile(request):
    instance = CompanyProfile.get()
    form = ProfileForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Company profile saved. Your documents now use these details.")
        return redirect("compliance:profile")
    sections = [
        ("The business", ["legal_name", "trading_name", "registration_number", "industry", "business_description", "employee_count"]),
        ("Contact details", ["physical_address", "postal_address", "phone", "email", "website"]),
        ("Head of the business", ["head_name", "head_title"]),
        ("Information Officer", ["io_name", "io_title", "io_email", "io_phone", "io_registered", "io_registration_date", "io_registration_reference"]),
        ("Deputy Information Officer (optional)", ["deputy_io_name", "deputy_io_email"]),
    ]
    return render(
        request,
        "compliance/profile.html",
        {"form": form, "sections": [(title, [form[name] for name in names]) for title, names in sections], "profile": instance},
    )


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@require_POST
def task_complete(request, pk):
    task = get_object_or_404(ComplianceTask, pk=pk, done_on__isnull=True)
    upcoming = task.complete()
    if upcoming:
        messages.success(request, f"Done. Next occurrence scheduled for {upcoming.due_date:%d %B %Y}.")
    else:
        messages.success(request, "Task marked as done.")
    return redirect("compliance:task_list")


# ---------------------------------------------------------------------------
# Learn
# ---------------------------------------------------------------------------

LEARN_TOPICS = [
    ("basics", "What is POPIA and does it apply to me?", "5 min"),
    ("terms", "Key terms without the jargon", "4 min"),
    ("conditions", "The 8 conditions for lawful processing", "8 min"),
    ("officer", "The Information Officer", "3 min"),
    ("rights", "People's rights and how to respond", "5 min"),
    ("breaches", "Security compromises (breaches)", "5 min"),
    ("paia", "PAIA – the other law you must follow", "4 min"),
    ("regulator", "The Information Regulator, fines and enforcement", "3 min"),
    ("updates", "What changed in 2025 and 2026", "3 min"),
    ("hosting", "Where this app keeps its data", "3 min"),
]


def learn(request, topic=None):
    if topic is None:
        return render(request, "compliance/learn/index.html", {"topics": LEARN_TOPICS})
    slugs = [t[0] for t in LEARN_TOPICS]
    if topic not in slugs:
        raise Http404
    index = slugs.index(topic)
    return render(
        request,
        f"compliance/learn/{topic}.html",
        {
            "topic": LEARN_TOPICS[index],
            "prev": LEARN_TOPICS[index - 1] if index > 0 else None,
            "next": LEARN_TOPICS[index + 1] if index + 1 < len(LEARN_TOPICS) else None,
            "topics": LEARN_TOPICS,
        },
    )


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


def document_list(request):
    return render(request, "compliance/documents.html", {"docs": documents.DOCUMENTS, "profile": CompanyProfile.get()})


def _document_context(slug):
    doc = documents.get(slug)
    if doc is None:
        raise Http404
    return doc, documents.context()


def document_view(request, slug):
    doc, ctx = _document_context(slug)
    body = render_to_string(f"compliance/documents/{slug}.html", ctx, request=request)
    return render(request, "compliance/document_view.html", {"doc": doc, "body": body, "missing": documents.missing_fields()})


def document_download(request, slug):
    """Download as a .doc file (HTML that Microsoft Word / LibreOffice / Google Docs open and edit)."""
    doc, ctx = _document_context(slug)
    ctx["standalone"] = True
    body = render_to_string(f"compliance/documents/{slug}.html", ctx, request=request)
    html = render_to_string("compliance/document_word.html", {"doc": doc, "body": body})
    response = HttpResponse(html, content_type="application/msword")
    response["Content-Disposition"] = f'attachment; filename="{doc["file"]}.doc"'
    return response


# ---------------------------------------------------------------------------
# PAIA report
# ---------------------------------------------------------------------------


def paia_report(request):
    today = timezone.localdate()
    default_end_year = today.year if today >= date(today.year, 4, 1) else today.year - 1
    try:
        end_year = int(request.GET.get("year", default_end_year))
    except ValueError:
        end_year = default_end_year
    start, end = date(end_year - 1, 4, 1), date(end_year, 3, 31)

    period = DataSubjectRequest.objects.filter(received_on__range=(start, end))
    access = period.filter(request_type="access")

    def late(qs):
        return sum(
            1 for r in qs if (r.completed_on and r.due_date and r.completed_on > r.due_date) or (r.is_open and r.due_date and r.due_date < min(today, end))
        )

    figures = [
        ("Requests for access received", access.count()),
        ("Granted in full", access.filter(outcome="granted_full").count()),
        ("Granted in part", access.filter(outcome="granted_partial").count()),
        ("Refused", access.filter(outcome="refused").count()),
        ("Records did not exist", access.filter(outcome="no_records").count()),
        ("Extensions taken (s57)", access.filter(status="extended").count()),
        ("Not decided within the time limit (deemed refusals)", late(access)),
        ("Still open at period end", sum(1 for r in access if r.is_open)),
    ]
    refusal_grounds = [r.refusal_grounds for r in access if r.refusal_grounds]
    other = [(label.split(" (")[0], period.filter(request_type=code).count()) for code, label in DataSubjectRequest.TYPES if code != "access"]
    return render(
        request,
        "compliance/paia_report.html",
        {
            "start": start,
            "end": end,
            "end_year": end_year,
            "years": list(range(default_end_year, default_end_year - 5, -1)),
            "figures": figures,
            "refusal_grounds": refusal_grounds,
            "other": other,
            "window": paia_window(today),
        },
    )


# ---------------------------------------------------------------------------
# Audit log, export & backups
# ---------------------------------------------------------------------------


class AuditLog(generic.ListView):
    model = AuditEntry
    paginate_by = 50
    template_name = "compliance/audit_log.html"


EXPORT_MODELS = [CompanyProfile, ChecklistItem, Operator, ProcessingActivity, RetentionRule, DataSubjectRequest, Incident, Risk, TrainingRecord, ComplianceTask, AuditEntry]


def export(request):
    files = backups.list_backups()
    return render(
        request,
        "compliance/export.html",
        {"backups": [(b.name, b.stat().st_size) for b in files[:30]], "health": backups.health()},
    )


def export_json(request):
    objects = []
    for model in EXPORT_MODELS:
        objects.extend(model.objects.all())
    data = serializers.serialize("json", objects, indent=2)
    stamp = timezone.localtime().strftime("%Y%m%d-%H%M")
    response = HttpResponse(data, content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="popia-export-{stamp}.json"'
    return response


@require_POST
def backup_now(request):
    try:
        target = backups.create_backup()
    except Exception as exc:
        messages.error(request, f"The backup failed: {exc}. Check that the backup folder exists and has free space.")
    else:
        messages.success(request, f"Backup created and checked: {target.name}.")
    return redirect("compliance:export")


@require_POST
def backup_test(request):
    newest = backups.newest_backup()
    if newest is None:
        messages.error(request, "There's no backup to test yet. Create one first.")
        return redirect("compliance:export")
    try:
        counts = backups.try_restore(newest)
    except backups.BackupError as exc:
        messages.error(request, f"{newest.name} can't be restored: {exc}. Create a new backup and test it.")
    else:
        found = ", ".join(f"{n} {label}" for label, n in counts.items())
        messages.success(request, f"{newest.name} restores correctly. It contains {found}.")
        AuditEntry.objects.create(user=request.user.get_username(), action="tested", model="Backup", summary=f"Restore test passed: {newest.name}")
    return redirect("compliance:export")


@require_POST
def reminder_test(request):
    try:
        to = reminders.send_test(request.user.get_username())
    except ValueError as exc:
        messages.error(request, str(exc))
    except Exception as exc:
        messages.error(request, f"The test email couldn't be sent: {exc}. Check the EMAIL_ settings in .env.")
    else:
        messages.success(request, f"Test email sent to {', '.join(to)}. Check that it arrived, including the spam folder.")
    return redirect("compliance:task_list")


def backup_download(request, name):
    path = settings.BACKUP_DIR / name
    if not name.startswith("popia-") or not name.endswith(".sqlite3.gz") or "/" in name or not path.is_file():
        raise Http404
    return FileResponse(open(path, "rb"), as_attachment=True, filename=name)


@login_not_required
def healthz(request):
    return HttpResponse("ok", content_type="text/plain")
