from django.urls import path

from . import views

app_name = "compliance"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("checklist/", views.checklist, name="checklist"),
    path("checklist/<int:pk>/", views.checklist_item, name="checklist_item"),
    path("profile/", views.profile, name="profile"),
    path("tasks/<int:pk>/done/", views.task_complete, name="task_complete"),
    path("learn/", views.learn, name="learn"),
    path("learn/<slug:topic>/", views.learn, name="learn_topic"),
    path("documents/", views.document_list, name="documents"),
    path("documents/<slug:slug>/", views.document_view, name="document"),
    path("documents/<slug:slug>/download/", views.document_download, name="document_download"),
    path("paia-report/", views.paia_report, name="paia_report"),
    path("audit-log/", views.AuditLog.as_view(), name="audit_log"),
    path("export/", views.export, name="export"),
    path("export/json/", views.export_json, name="export_json"),
    path("export/backup/", views.backup_now, name="backup_now"),
    path("export/backup/<str:name>/", views.backup_download, name="backup_download"),
    path("healthz", views.healthz, name="healthz"),
]

for register in views.REGISTERS:
    urlpatterns += register.urlpatterns()
