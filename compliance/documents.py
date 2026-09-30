"""Catalogue of generated compliance documents and the data they are built from."""

from django.utils import timezone

from .models import CompanyProfile, Operator, ProcessingActivity, RetentionRule

DOCUMENTS = [
    {
        "slug": "popia-policy",
        "file": "POPIA-Compliance-Policy",
        "title": "POPIA Compliance Policy",
        "audience": "Internal – all staff",
        "legal_ref": "Regulation 4(1)(a); POPIA s8, s19",
        "description": "Your compliance framework in writing: roles, the 8 conditions as rules for staff, security, requests and breaches.",
        "action": "Review, sign, share with staff and have them acknowledge it.",
    },
    {
        "slug": "privacy-notice",
        "file": "Privacy-Notice",
        "title": "Privacy Notice (customers & suppliers)",
        "audience": "Public – publish on your website",
        "legal_ref": "POPIA s18",
        "description": "Tells customers, suppliers and website visitors what you collect, why, who receives it and their rights.",
        "action": "Publish on your website and link to it from quotes, invoices and email signatures.",
    },
    {
        "slug": "employee-notice",
        "file": "Employee-Privacy-Notice",
        "title": "Employee Privacy Notice & Consent",
        "audience": "Employees and job applicants",
        "legal_ref": "POPIA s18, s26–s27, s32, s34–s35",
        "description": "Explains how employee information (including health and banking information) is used, with optional consents for biometrics and background checks.",
        "action": "Give to every employee; keep a signed acknowledgement in their file.",
    },
    {
        "slug": "paia-manual",
        "file": "PAIA-Manual",
        "title": "PAIA Manual",
        "audience": "Public – website and premises",
        "legal_ref": "PAIA s51; POPIA s17",
        "description": "The legally required manual describing your records and how people can request access to them.",
        "action": "Publish on your website and keep a printed copy at your premises. Review yearly.",
    },
    {
        "slug": "io-appointment",
        "file": "Information-Officer-Appointment",
        "title": "Information Officer appointment",
        "audience": "Internal",
        "legal_ref": "POPIA s55–s56; PAIA s17",
        "description": "Letter by the head of the business authorising the Information Officer (and deputy), with duties.",
        "action": "Sign, file, then register the IO on the eServices portal.",
    },
    {
        "slug": "breach-plan",
        "file": "Security-Compromise-Response-Plan",
        "title": "Security compromise (breach) response plan",
        "audience": "Internal",
        "legal_ref": "POPIA s19, s22",
        "description": "Step-by-step plan for when personal information is lost, stolen, hacked or sent to the wrong person.",
        "action": "Share with staff; print a copy to keep off-line.",
    },
    {
        "slug": "breach-letter",
        "file": "Breach-Notification-Letter",
        "title": "Breach notification letter (template)",
        "audience": "Affected people",
        "legal_ref": "POPIA s22(4)–(5)",
        "description": "Template to tell affected people about a security compromise, containing everything s22(5) requires.",
        "action": "Use only when needed – fill in the bracketed parts.",
    },
    {
        "slug": "operator-agreement",
        "file": "Operator-Agreement",
        "title": "Operator agreement (data processing addendum)",
        "audience": "Service providers",
        "legal_ref": "POPIA s20, s21, s72",
        "description": "Contract terms for suppliers who process personal information for you, if they don't offer their own DPA.",
        "action": "Send to operators without their own data processing terms; file signed copies.",
    },
    {
        "slug": "retention-schedule",
        "file": "Records-Retention-Schedule",
        "title": "Records retention schedule",
        "audience": "Internal",
        "legal_ref": "POPIA s14",
        "description": "How long each type of record is kept and how it is destroyed, generated from your retention register.",
        "action": "Adopt and follow during the quarterly clean-up.",
    },
    {
        "slug": "processing-record",
        "file": "Record-of-Processing",
        "title": "Record of processing activities",
        "audience": "Internal / on request by the Regulator",
        "legal_ref": "POPIA s17",
        "description": "Printable version of your processing register and operators.",
        "action": "Keep with your compliance file; produce if the Regulator asks.",
    },
    {
        "slug": "request-response",
        "file": "Request-Response-Letters",
        "title": "Request acknowledgement & response letters",
        "audience": "People making requests",
        "legal_ref": "POPIA s11(2)–(3), s14(6)–(8), s23–s25; PAIA s56–s57",
        "description": "Templates to acknowledge, extend, grant or refuse requests, estimate fees, confirm no information is held, restrict processing and confirm consent withdrawals.",
        "action": "Copy the relevant letter when responding to a request.",
    },
]


REGULATOR = {
    "name": "Information Regulator (South Africa)",
    "address": "Woodmead North Office Park, 54 Maxwell Drive, Woodmead, Johannesburg, 2191",
    "email": "enquiries@inforegulator.org.za",
    "popia_complaints": "POPIAComplaints@inforegulator.org.za",
    "paia_complaints": "PAIAComplaints@inforegulator.org.za",
    "website": "https://inforegulator.org.za",
    "portal": "https://eservices.inforegulator.org.za",
}


def get(slug):
    return next((d for d in DOCUMENTS if d["slug"] == slug), None)


def context():
    activities = ProcessingActivity.objects.prefetch_related("operators")
    operators = Operator.objects.all()
    return {
        "c": CompanyProfile.get(),
        "activities": activities,
        "operators": operators,
        "overseas": [o for o in operators if o.outside_sa],
        "retention": RetentionRule.objects.all(),
        "special": any(a.special_info for a in activities),
        "today": timezone.localdate(),
        "regulator": REGULATOR,
    }


def missing_fields():
    c = CompanyProfile.get()
    return [c._meta.get_field(name).verbose_name for name in CompanyProfile.REQUIRED_FIELDS if not getattr(c, name)]
