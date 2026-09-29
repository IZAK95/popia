from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from . import models
from .middleware import get_current_username

AUDITED = (
    models.CompanyProfile,
    models.ChecklistItem,
    models.Operator,
    models.ProcessingActivity,
    models.RetentionRule,
    models.DataSubjectRequest,
    models.Incident,
    models.Risk,
    models.TrainingRecord,
    models.ComplianceTask,
)


def _log(instance, action):
    models.AuditEntry.objects.create(
        user=get_current_username(),
        action=action,
        model=instance._meta.verbose_name.capitalize(),
        object_id=str(instance.pk or ""),
        summary=str(instance)[:300],
    )


@receiver(post_save)
def audit_save(sender, instance, created, raw=False, **kwargs):
    if sender in AUDITED and not raw:
        _log(instance, "created" if created else "updated")


@receiver(post_delete)
def audit_delete(sender, instance, **kwargs):
    if sender in AUDITED:
        _log(instance, "deleted")
