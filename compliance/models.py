from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils import timezone


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Draftable(models.Model):
    """Seeded example entries start as drafts so it's obvious what still needs checking."""

    DRAFT, CONFIRMED = "draft", "confirmed"
    REVIEW_CHOICES = [(DRAFT, "Draft – needs your review"), (CONFIRMED, "Confirmed accurate")]
    review_status = models.CharField(
        "Review status",
        max_length=12,
        choices=REVIEW_CHOICES,
        default=CONFIRMED,
        help_text="Examples added by the app start as drafts. Change to 'Confirmed' once you've checked every field.",
    )

    class Meta:
        abstract = True

    @property
    def is_draft(self):
        return self.review_status == self.DRAFT


def next_reference(model, prefix):
    year = timezone.localdate().year
    count = model.objects.filter(reference__startswith=f"{prefix}-{year}-").count() + 1
    return f"{prefix}-{year}-{count:03d}"


# ---------------------------------------------------------------------------
# Company profile
# ---------------------------------------------------------------------------


class CompanyProfile(TimeStamped):
    legal_name = models.CharField("Registered (legal) name", max_length=200, blank=True)
    trading_name = models.CharField("Trading name", max_length=200, blank=True)
    registration_number = models.CharField(
        "CIPC registration number", max_length=50, blank=True, help_text="E.g. 2015/123456/07. Needed to register your Information Officer."
    )
    industry = models.CharField(max_length=120, blank=True)
    business_description = models.TextField(
        "What does the business do?",
        blank=True,
        help_text="One or two sentences. Used in your PAIA manual and privacy notices.",
    )
    physical_address = models.TextField(blank=True)
    postal_address = models.TextField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField("General email", blank=True)
    website = models.URLField(blank=True)
    employee_count = models.PositiveIntegerField("Number of employees", null=True, blank=True)

    head_name = models.CharField(
        "Head of the business",
        max_length=120,
        blank=True,
        help_text="The CEO, managing director, sole owner or equivalent. By law this person is the Information Officer unless they authorise someone else.",
    )
    head_title = models.CharField("Head's job title", max_length=120, blank=True)

    io_name = models.CharField("Information Officer – name", max_length=120, blank=True)
    io_title = models.CharField("Information Officer – job title", max_length=120, blank=True)
    io_email = models.EmailField(
        "Information Officer – email",
        blank=True,
        help_text="Tip: use a role address such as privacy@yourdomain.co.za so it survives staff changes.",
    )
    io_phone = models.CharField("Information Officer – phone", max_length=40, blank=True)
    io_registered = models.BooleanField(
        "Information Officer registered with the Information Regulator", default=False
    )
    io_registration_date = models.DateField("Date registered", null=True, blank=True)
    io_registration_reference = models.CharField(
        "Registration reference", max_length=80, blank=True, help_text="The reference/number shown on the eServices portal after registration."
    )
    deputy_io_name = models.CharField("Deputy Information Officer – name", max_length=120, blank=True)
    deputy_io_email = models.EmailField("Deputy Information Officer – email", blank=True)

    class Meta:
        verbose_name = "company profile"

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.trading_name or self.legal_name or "Your business"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    REQUIRED_FIELDS = ("legal_name", "registration_number", "business_description", "physical_address", "email", "head_name", "io_name", "io_email")

    @property
    def completeness(self):
        filled = sum(1 for name in self.REQUIRED_FIELDS if getattr(self, name))
        return round(100 * filled / len(self.REQUIRED_FIELDS))

    def get_absolute_url(self):
        return reverse("compliance:profile")


# ---------------------------------------------------------------------------
# Compliance checklist (the framework)
# ---------------------------------------------------------------------------


class ChecklistItem(TimeStamped):
    AREAS = [
        ("governance", "Accountability & Information Officer"),
        ("lawful", "Lawful, limited & purposeful processing"),
        ("openness", "Openness & information quality"),
        ("security", "Security safeguards & breaches"),
        ("rights", "Data subject rights"),
        ("special", "Special information, children & cross-border"),
        ("marketing", "Direct marketing & automated decisions"),
        ("paia", "PAIA (access to information)"),
    ]
    TODO, PROGRESS, DONE, NA = "todo", "progress", "done", "na"
    STATUSES = [(TODO, "Not started"), (PROGRESS, "In progress"), (DONE, "Done"), (NA, "Not applicable")]

    code = models.CharField(max_length=20, unique=True)
    area = models.CharField(max_length=20, choices=AREAS)
    title = models.CharField(max_length=200)
    why = models.TextField(help_text="Plain-language explanation of the requirement.")
    how = models.TextField(help_text="Practical steps.")
    legal_ref = models.CharField(max_length=200, blank=True)
    essential = models.BooleanField(default=True)
    action_url = models.CharField(max_length=80, blank=True, help_text="URL name of the page in this app that helps.")
    action_label = models.CharField(max_length=80, blank=True)
    order = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=10, choices=STATUSES, default=TODO)
    evidence = models.TextField(
        "Notes & evidence",
        blank=True,
        help_text="What did you do, when, and where is the proof? (e.g. 'Signed IO letter 3 Oct 2026, filed in HR drive'). Also explain why if marked Not applicable.",
    )
    completed_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.code} {self.title}"

    def get_absolute_url(self):
        return reverse("compliance:checklist_item", args=[self.pk])

    def save(self, *args, **kwargs):
        if self.status == self.DONE and not self.completed_on:
            self.completed_on = timezone.localdate()
        elif self.status != self.DONE:
            self.completed_on = None
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Registers
# ---------------------------------------------------------------------------


class Operator(TimeStamped, Draftable):
    TRANSFER_BASES = [
        ("local", "Not applicable – information stays in South Africa"),
        ("adequate", "Recipient is bound by law/agreement giving adequate protection – s72(1)(a)"),
        ("consent", "The people concerned consented to the transfer – s72(1)(b)"),
        ("contract", "Necessary for a contract with, or in the interest of, the person – s72(1)(c)/(d)"),
        ("benefit", "For the person's benefit and consent impractical – s72(1)(e)"),
        ("unknown", "Not yet assessed"),
    ]

    name = models.CharField("Supplier / service provider", max_length=200)
    service = models.CharField(
        "What they do for you", max_length=250, help_text="E.g. 'Payroll software', 'Email & file storage', 'IT support'."
    )
    personal_info = models.TextField(
        "Personal information they handle", blank=True, help_text="E.g. 'Employee names, ID numbers, salaries, bank details'."
    )
    data_location = models.CharField(
        "Where is the information stored?",
        max_length=200,
        blank=True,
        help_text="Country/region of the servers. Check the provider's website or contract (search '<provider> data residency').",
    )
    outside_sa = models.BooleanField("Stored or accessed outside South Africa", default=False)
    transfer_basis = models.CharField(
        "Legal basis for cross-border transfer",
        max_length=12,
        choices=TRANSFER_BASES,
        default="unknown",
        help_text="POPIA s72. For EU/UK providers or big cloud providers with data protection terms, 'adequate protection' is usually the right basis.",
    )
    agreement_in_place = models.BooleanField(
        "Written agreement with confidentiality & security terms (s21)",
        default=False,
        help_text="Can be their standard Data Processing Agreement/Addendum (DPA) or our operator agreement template.",
    )
    agreement_date = models.DateField(null=True, blank=True)
    agreement_location = models.CharField("Where is the agreement filed?", max_length=250, blank=True)
    notes = models.TextField(blank=True)
    next_review = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("compliance:operator_detail", args=[self.pk])

    @property
    def issues(self):
        problems = []
        if not self.agreement_in_place:
            problems.append("No written operator agreement (s21)")
        if self.outside_sa and self.transfer_basis in ("unknown", "local"):
            problems.append("Cross-border basis not documented (s72)")
        return problems


class ProcessingActivity(TimeStamped, Draftable):
    LAWFUL_BASES = [
        ("consent", "Consent of the person – s11(1)(a)"),
        ("contract", "Needed for a contract with the person – s11(1)(b)"),
        ("law", "Required by law – s11(1)(c)"),
        ("subject_interest", "Protects the person's legitimate interest – s11(1)(d)"),
        ("legit_interest", "Legitimate interest of the business or a third party – s11(1)(f)"),
    ]

    name = models.CharField("Activity", max_length=200, help_text="E.g. 'Payroll', 'Recruitment', 'Customer orders & invoicing'.")
    data_subjects = models.CharField(
        "Whose information?", max_length=250, help_text="E.g. employees, job applicants, customer contact persons. Note: companies are also 'data subjects' under POPIA."
    )
    personal_info = models.TextField("What information?", help_text="List the categories: name, ID number, bank details, etc.")
    purpose = models.TextField("Why do you need it?", help_text="Be specific (POPIA s13). This goes into your privacy notices.")
    lawful_basis = models.CharField(
        "Lawful ground (s11)", max_length=20, choices=LAWFUL_BASES, help_text="Most business processing is 'contract', 'required by law' or 'legitimate interest'. Use consent only when nothing else fits."
    )
    lawful_basis_notes = models.CharField("Lawful ground – notes", max_length=250, blank=True, help_text="E.g. which law (Income Tax Act, BCEA...).")
    source = models.CharField("Where do you get it?", max_length=250, blank=True, help_text="Directly from the person (preferred, s12) or elsewhere?")
    special_info = models.BooleanField(
        "Includes special personal information",
        default=False,
        help_text="Health, biometrics (fingerprints/face), race, religion, trade union, political views, sex life, or criminal behaviour (s26).",
    )
    special_info_details = models.CharField("Special information – details & authorisation", max_length=250, blank=True)
    children_info = models.BooleanField("Includes information about children (under 18)", default=False, help_text="E.g. employees' dependants on medical aid.")
    recipients = models.TextField("Who else receives it?", blank=True, help_text="E.g. SARS, UIF, medical aid, auditors, banks.")
    operators = models.ManyToManyField(Operator, blank=True, related_name="activities", verbose_name="Service providers used")
    cross_border = models.BooleanField("Sent or stored outside South Africa", default=False)
    retention = models.CharField("How long do you keep it?", max_length=250, blank=True, help_text="See the Retention schedule for legal minimums.")
    security_measures = models.TextField("How is it protected?", blank=True, help_text="E.g. password-protected payroll system with 2FA, locked cabinet for paper files.")
    notice_given = models.BooleanField("People are told about this (privacy notice, s18)", default=False)
    owner = models.CharField("Responsible person", max_length=120, blank=True)
    last_reviewed = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "processing activities"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("compliance:activity_detail", args=[self.pk])

    @property
    def issues(self):
        problems = []
        if not self.notice_given:
            problems.append("People not yet notified (s18)")
        if not self.retention:
            problems.append("No retention period (s14)")
        if self.special_info and not self.special_info_details:
            problems.append("Special information without documented authorisation (s27)")
        if not self.security_measures:
            problems.append("Security measures not documented (s19)")
        return problems


class RetentionRule(TimeStamped):
    STATUTORY, POLICY = "statutory", "policy"
    KINDS = [(STATUTORY, "Legal minimum"), (POLICY, "Business policy")]

    record_type = models.CharField("Type of record", max_length=200)
    examples = models.CharField(max_length=300, blank=True)
    period = models.CharField("Keep for", max_length=120)
    starts_from = models.CharField("Counted from", max_length=200, blank=True)
    legal_source = models.CharField("Source / reason", max_length=250, blank=True)
    kind = models.CharField(max_length=10, choices=KINDS, default=POLICY)
    disposal = models.CharField(
        "How to destroy", max_length=200, blank=True, default="Shred paper; permanently delete electronic copies incl. backups at next rotation"
    )
    order = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["order", "record_type"]

    def __str__(self):
        return self.record_type

    def get_absolute_url(self):
        return reverse("compliance:retention_list")


class DataSubjectRequest(TimeStamped):
    TYPES = [
        ("access", "Access to personal information / records (POPIA s23, PAIA s50)"),
        ("correction", "Correction of information (s24 – Form 2)"),
        ("deletion", "Deletion / destruction of information (s24 – Form 2)"),
        ("objection", "Objection to processing (s11(3) – Form 1)"),
        ("restriction", "Restriction of processing (s14(6))"),
        ("consent", "Withdrawal of consent (s11(2)(b))"),
        ("marketing", "Stop direct marketing (s69)"),
        ("complaint", "Privacy complaint"),
        ("other", "Other"),
    ]
    STATUSES = [
        ("new", "Received"),
        ("in_progress", "In progress"),
        ("extended", "Extended (+30 days, requester notified)"),
        ("completed", "Completed"),
        ("refused", "Refused"),
        ("withdrawn", "Withdrawn"),
    ]
    OUTCOMES = [
        ("", "—"),
        ("granted_full", "Granted in full"),
        ("granted_partial", "Granted in part"),
        ("refused", "Refused"),
        ("no_records", "No records exist"),
    ]
    OPEN_STATUSES = ("new", "in_progress", "extended")

    reference = models.CharField(max_length=20, unique=True, editable=False)
    request_type = models.CharField("Type of request", max_length=20, choices=TYPES)
    requester_name = models.CharField("Requester", max_length=200)
    requester_contact = models.CharField("Contact details", max_length=250, blank=True)
    received_on = models.DateField(default=timezone.localdate)
    channel = models.CharField("Received via", max_length=80, blank=True, help_text="Email, phone, WhatsApp, letter, in person... (all are valid since the 2025 regulation amendments).")
    identity_verified = models.BooleanField(
        "Identity verified", default=False, help_text="Confirm who they are before releasing or changing information (s23(1))."
    )
    details = models.TextField("What are they asking for?")
    due_date = models.DateField(blank=True, null=True, help_text="Leave blank to calculate automatically (30 days).")
    status = models.CharField(max_length=20, choices=STATUSES, default="new")
    outcome = models.CharField(max_length=20, choices=OUTCOMES, blank=True)
    refusal_grounds = models.CharField("Grounds for refusal (if any)", max_length=250, blank=True, help_text="Only the grounds in PAIA Part 3 Chapter 4 (e.g. s63–s69) may be used.")
    completed_on = models.DateField(null=True, blank=True)
    response_notes = models.TextField("What was done / response sent", blank=True)

    class Meta:
        ordering = ["-received_on", "-id"]

    def __str__(self):
        return f"{self.reference} – {self.get_request_type_display().split(' (')[0]}"

    def get_absolute_url(self):
        return reverse("compliance:request_detail", args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = next_reference(DataSubjectRequest, "DSR")
        if not self.due_date:
            self.due_date = self.received_on + timedelta(days=30)
        if self.status in ("completed", "refused") and not self.completed_on:
            self.completed_on = timezone.localdate()
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES

    @property
    def is_overdue(self):
        return self.is_open and self.due_date and self.due_date < timezone.localdate()

    @property
    def days_left(self):
        return (self.due_date - timezone.localdate()).days if self.due_date else None


class Incident(TimeStamped):
    CAUSES = [
        ("device", "Lost or stolen laptop / phone / USB"),
        ("phishing", "Phishing or hacked email/account"),
        ("ransomware", "Ransomware or malware"),
        ("misdirected", "Information sent to the wrong person"),
        ("insider", "Unauthorised access by staff"),
        ("operator", "Breach at a service provider"),
        ("paper", "Lost or exposed paper records"),
        ("other", "Other"),
    ]
    NOTIFIABLE = [
        ("yes", "Yes – reasonable grounds to believe it was accessed or acquired"),
        ("no", "No – e.g. device was encrypted, or data was recovered unread"),
        ("unsure", "Not sure yet – still investigating"),
    ]
    STATUSES = [
        ("open", "Open – investigating"),
        ("contained", "Contained"),
        ("notified", "Notifications sent"),
        ("closed", "Closed"),
    ]

    reference = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField("Short title", max_length=200)
    discovered_on = models.DateTimeField("When was it discovered?", default=timezone.now)
    occurred_on = models.DateField("When did it happen (if known)?", null=True, blank=True)
    reported_by = models.CharField(max_length=120, blank=True)
    cause = models.CharField(max_length=20, choices=CAUSES)
    description = models.TextField("What happened?")
    personal_info_affected = models.TextField("Which personal information was involved?", blank=True)
    people_affected = models.PositiveIntegerField("Approx. number of people affected", null=True, blank=True)
    containment = models.TextField(
        "What have you done to contain it?", blank=True, help_text="E.g. reset passwords, remote-wiped device, asked recipient to delete email, contacted IT support."
    )
    notifiable = models.CharField(
        "Was personal information (probably) accessed or acquired by someone unauthorised?",
        max_length=10,
        choices=NOTIFIABLE,
        default="unsure",
        help_text="POPIA has no 'low risk' exemption: if the answer is yes, you must notify the Regulator AND the affected people (s22).",
    )
    regulator_notified_on = models.DateField("Regulator notified on", null=True, blank=True)
    regulator_reference = models.CharField("Regulator reference (from the eServices portal)", max_length=80, blank=True)
    subjects_notified_on = models.DateField("Affected people notified on", null=True, blank=True)
    subjects_notification_method = models.CharField(
        "How were they notified?", max_length=200, blank=True, help_text="Email, letter to last known address, website notice, news media, or as the Regulator directs (s22(4))."
    )
    status = models.CharField(max_length=12, choices=STATUSES, default="open")
    lessons_learned = models.TextField("Root cause & lessons learned", blank=True)
    closed_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-discovered_on"]

    def __str__(self):
        return f"{self.reference} – {self.title}"

    def get_absolute_url(self):
        return reverse("compliance:incident_detail", args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = next_reference(Incident, "INC")
        if self.status == "closed" and not self.closed_on:
            self.closed_on = timezone.localdate()
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return self.status != "closed"

    @property
    def needs_notification(self):
        return self.notifiable == "yes" and (not self.regulator_notified_on or not self.subjects_notified_on)


class Risk(TimeStamped, Draftable):
    SCALE = [(1, "1 – Very low"), (2, "2 – Low"), (3, "3 – Medium"), (4, "4 – High"), (5, "5 – Very high")]
    STATUSES = [("open", "Open"), ("mitigating", "Being addressed"), ("accepted", "Accepted"), ("closed", "Closed")]

    title = models.CharField("Risk", max_length=200)
    description = models.TextField("What could go wrong?", blank=True)
    activity = models.ForeignKey(ProcessingActivity, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Related activity")
    likelihood = models.PositiveSmallIntegerField(choices=SCALE, default=3)
    impact = models.PositiveSmallIntegerField(choices=SCALE, default=3, help_text="Harm to the people concerned if it happens.")
    mitigation = models.TextField("Controls / actions", blank=True)
    owner = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=12, choices=STATUSES, default="open")
    review_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-likelihood", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("compliance:risk_detail", args=[self.pk])

    @property
    def score(self):
        return self.likelihood * self.impact

    @property
    def level(self):
        if self.score >= 15:
            return "high"
        if self.score >= 8:
            return "medium"
        return "low"


class TrainingRecord(TimeStamped):
    date = models.DateField(default=timezone.localdate)
    topic = models.CharField(max_length=200, default="POPIA awareness")
    attendees = models.TextField(help_text="Names of everyone who attended (one per line).")
    delivered_by = models.CharField(max_length=120, blank=True)
    materials = models.CharField("Materials / link", max_length=300, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.topic} ({self.date:%d %b %Y})"

    def get_absolute_url(self):
        return reverse("compliance:training_detail", args=[self.pk])

    @property
    def attendee_count(self):
        return len([line for line in self.attendees.splitlines() if line.strip()])


class ComplianceTask(TimeStamped):
    RECURRENCE = [("none", "Once-off"), ("monthly", "Monthly"), ("quarterly", "Quarterly"), ("yearly", "Yearly")]
    MONTHS = {"monthly": 1, "quarterly": 3, "yearly": 12}

    title = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    due_date = models.DateField()
    recurrence = models.CharField(max_length=10, choices=RECURRENCE, default="none")
    done_on = models.DateField(null=True, blank=True)
    link = models.CharField("Related page in this app", max_length=80, blank=True)

    class Meta:
        ordering = ["done_on", "due_date"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("compliance:task_list")

    @property
    def is_overdue(self):
        return not self.done_on and self.due_date < timezone.localdate()

    def complete(self):
        """Mark done and, for recurring tasks, schedule the next occurrence."""
        self.done_on = timezone.localdate()
        self.save()
        months = self.MONTHS.get(self.recurrence)
        if months:
            return ComplianceTask.objects.create(
                title=self.title,
                details=self.details,
                due_date=add_months(self.due_date, months),
                recurrence=self.recurrence,
                link=self.link,
            )
        return None


def add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, [31, 29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return value.replace(year=year, month=month, day=day)


class RegulatorMatter(TimeStamped):
    """Correspondence from the Information Regulator: complaints, assessments, notices and fines (Chapter 10)."""

    KINDS = [
        ("complaint", "Complaint about us referred by the Regulator (s74–s77)"),
        ("assessment", "Assessment of our processing (s89)"),
        ("information_notice", "Information notice (s90)"),
        ("enforcement_notice", "Enforcement notice (s95)"),
        ("infringement_notice", "Infringement notice – administrative fine (s109)"),
        ("prior_authorisation", "Prior authorisation notification (s57–s58)"),
        ("other", "Other correspondence"),
    ]
    # Notices that can be appealed to the High Court within 30 days of receipt (s97(1)).
    APPEALABLE = ("information_notice", "enforcement_notice")
    STATUSES = [
        ("open", "Open – action needed"),
        ("responded", "Responded / complied"),
        ("appealed", "Appealed to the High Court"),
        ("closed", "Closed"),
    ]
    OPEN_STATUSES = ("open", "appealed")

    reference = models.CharField(max_length=20, unique=True, editable=False)
    kind = models.CharField("Type", max_length=24, choices=KINDS)
    received_on = models.DateField("Received on", default=timezone.localdate)
    regulator_reference = models.CharField("Regulator's reference", max_length=80, blank=True)
    summary = models.TextField("What is it about?", help_text="What the Regulator asks for or alleges, in your own words.")
    response_due = models.DateField(
        "Response or compliance deadline",
        null=True,
        blank=True,
        help_text="The date in the notice. For an infringement notice, leave blank: it's 30 days after you received it (s109).",
    )
    status = models.CharField(max_length=12, choices=STATUSES, default="open")
    responded_on = models.DateField("Responded / complied on", null=True, blank=True)
    actions_taken = models.TextField("What we did", blank=True, help_text="Steps taken, information supplied, fine paid, appeal lodged.")
    documents_location = models.CharField(
        "Where the notice and our response are filed", max_length=255, blank=True, help_text="E.g. a folder path or document system link."
    )

    class Meta:
        ordering = ["-received_on", "-id"]
        verbose_name = "Regulator matter"

    def __str__(self):
        return f"{self.reference} – {self.get_kind_display().split(' (')[0]}"

    def get_absolute_url(self):
        return reverse("compliance:regulator_detail", args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = next_reference(RegulatorMatter, "REG")
        if not self.response_due and self.kind == "infringement_notice":
            self.response_due = self.received_on + timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES

    @property
    def appeal_deadline(self):
        return self.received_on + timedelta(days=30) if self.kind in self.APPEALABLE else None

    @property
    def days_left(self):
        return (self.response_due - timezone.localdate()).days if self.response_due else None

    @property
    def is_overdue(self):
        return self.status == "open" and self.response_due is not None and self.response_due < timezone.localdate()


class AuditEntry(models.Model):
    """Append-only log of changes – evidence of accountability (POPIA condition 1)."""

    at = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=20)
    model = models.CharField(max_length=80)
    object_id = models.CharField(max_length=40, blank=True)
    summary = models.CharField(max_length=300)

    class Meta:
        ordering = ["-at"]
        verbose_name_plural = "audit entries"

    def __str__(self):
        return f"{self.at:%Y-%m-%d %H:%M} {self.user} {self.action} {self.summary}"


class SeedMarker(models.Model):
    """Records which starter content has been loaded, so deleting examples doesn't bring them back."""

    key = models.CharField(max_length=50, unique=True)
    at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key
