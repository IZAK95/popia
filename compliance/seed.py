from django.db import transaction
from django.utils import timezone

from . import knowledge
from .models import (
    ChecklistItem,
    CompanyProfile,
    ComplianceTask,
    Draftable,
    Operator,
    ProcessingActivity,
    RetentionRule,
    Risk,
    SeedMarker,
)


def _once(key):
    """Run a seeding step only the first time, so user deletions stick."""
    _, created = SeedMarker.objects.get_or_create(key=key)
    return created


@transaction.atomic
def seed_all():
    CompanyProfile.get()

    # The checklist is refreshed on every start so improved guidance reaches existing installs,
    # while the user's status and evidence are preserved.
    for order, (code, area, essential, title, why, how, legal_ref, action_url, action_label) in enumerate(knowledge.CHECKLIST):
        ChecklistItem.objects.update_or_create(
            code=code,
            defaults=dict(
                area=area, essential=essential, title=title, why=why, how=how, legal_ref=legal_ref,
                action_url=action_url, action_label=action_label, order=order,
            ),
        )

    if _once("retention-v1"):
        for order, (record_type, examples, period, starts_from, source, kind) in enumerate(knowledge.RETENTION_RULES):
            RetentionRule.objects.create(
                record_type=record_type, examples=examples, period=period, starts_from=starts_from,
                legal_source=source, kind=kind, order=order,
            )

    if _once("operators-v1"):
        for name, service, info, location, outside, basis, notes in knowledge.OPERATORS:
            Operator.objects.create(
                name=name, service=service, personal_info=info, data_location=location, outside_sa=outside,
                transfer_basis=basis, notes=notes, review_status=Draftable.DRAFT,
            )

    if _once("activities-v1"):
        for spec in knowledge.ACTIVITIES:
            spec = dict(spec)
            operator_names = spec.pop("operators")
            activity = ProcessingActivity.objects.create(review_status=Draftable.DRAFT, **spec)
            activity.operators.set(Operator.objects.filter(name__in=operator_names))

    if _once("risks-v1"):
        for title, description, likelihood, impact, mitigation in knowledge.RISKS:
            Risk.objects.create(
                title=title, description=description, likelihood=likelihood, impact=impact,
                mitigation=mitigation, review_status=Draftable.DRAFT,
            )

    if _once("tasks-v1"):
        for title, details, due, recurrence, link in knowledge.seed_tasks(timezone.localdate()):
            ComplianceTask.objects.create(title=title, details=details, due_date=due, recurrence=recurrence, link=link)
