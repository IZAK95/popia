from django.urls import reverse

NAVIGATION = [
    ("Overview", [
        ("compliance:dashboard", "Dashboard", "home"),
        ("compliance:checklist", "Compliance checklist", "check"),
        ("compliance:task_list", "Tasks & deadlines", "calendar"),
    ]),
    ("Learn", [
        ("compliance:learn", "POPIA in plain language", "book"),
    ]),
    ("Registers", [
        ("compliance:activity_list", "Processing register", "list"),
        ("compliance:operator_list", "Operators (suppliers)", "truck"),
        ("compliance:retention_list", "Retention schedule", "archive"),
        ("compliance:risk_list", "Risk register", "alert"),
    ]),
    ("Day-to-day", [
        ("compliance:request_list", "Requests from people", "inbox"),
        ("compliance:incident_list", "Incidents & breaches", "shield"),
        ("compliance:regulator_list", "Regulator correspondence", "mail"),
        ("compliance:training_list", "Training log", "users"),
        ("compliance:paia_report", "PAIA annual report", "report"),
    ]),
    ("Documents", [
        ("compliance:documents", "Policies & notices", "file"),
    ]),
    ("Settings", [
        ("compliance:profile", "Company profile", "building"),
        ("compliance:audit_log", "Audit log", "clock"),
        ("compliance:export", "Export & backup", "download"),
    ]),
]


def navigation(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}
    groups = []
    for label, items in NAVIGATION:
        entries = []
        for name, title, icon in items:
            url = reverse(name)
            active = request.path == url or (url != "/" and request.path.startswith(url))
            entries.append({"url": url, "title": title, "icon": icon, "active": active})
        groups.append({"label": label, "items": entries})
    from .models import CompanyProfile

    return {"nav_groups": groups, "company": CompanyProfile.get()}
