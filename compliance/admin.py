from django.contrib import admin

from . import models

for model in (
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
):
    admin.site.register(model)


@admin.register(models.AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ("at", "user", "action", "model", "summary")
    list_filter = ("action", "model")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
