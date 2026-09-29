from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "POPIA Compliance – raw data admin"

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("", include("compliance.urls")),
]
