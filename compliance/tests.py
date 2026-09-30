import gzip
import os
import sqlite3
import tempfile
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice

from . import documents
from .models import (
    AuditEntry,
    ChecklistItem,
    ComplianceTask,
    DataSubjectRequest,
    Incident,
    Operator,
    ProcessingActivity,
    Risk,
    add_months,
)
from .seed import seed_all
from .views import LEARN_TOPICS, REGISTERS

TEST_SETTINGS = dict(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
    AXES_ENABLED=False,
)


def token_for(device):
    return f"{totp(device.bin_key, step=device.step, t0=device.t0, digits=device.digits):06d}"


@override_settings(**TEST_SETTINGS)
class AuthFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("owner", password="a-long-test-password")

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("compliance:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])

    def test_healthz_is_public(self):
        self.assertEqual(self.client.get("/healthz").status_code, 200)

    def test_password_only_session_must_enrol_2fa(self):
        self.client.login(username="owner", password="a-long-test-password")
        response = self.client.get(reverse("compliance:dashboard"))
        self.assertRedirects(response, reverse("accounts:two_factor_setup"))

        # Enrolment page creates an unconfirmed device; a valid token confirms it.
        self.client.get(reverse("accounts:two_factor_setup"))
        device = TOTPDevice.objects.get(user=self.user)
        response = self.client.post(reverse("accounts:two_factor_setup"), {"token": token_for(device)})
        self.assertRedirects(response, reverse("compliance:dashboard"), fetch_redirect_response=False)
        device.refresh_from_db()
        self.assertTrue(device.confirmed)
        self.assertEqual(self.client.get(reverse("compliance:dashboard")).status_code, 200)

    def test_enrolled_user_must_verify(self):
        TOTPDevice.objects.create(user=self.user, name="phone", confirmed=True)
        self.client.login(username="owner", password="a-long-test-password")
        response = self.client.get(reverse("compliance:checklist"))
        verify = reverse("accounts:two_factor_verify") + "?next=%2Fchecklist%2F"
        self.assertRedirects(response, verify)
        response = self.client.post(verify, {"token": "000000"})
        self.assertContains(response, "Invalid or expired code")

    def test_verify_returns_to_requested_page(self):
        device = TOTPDevice.objects.create(user=self.user, name="phone", confirmed=True)
        self.client.login(username="owner", password="a-long-test-password")
        verify = self.client.get(reverse("compliance:checklist"))["Location"]
        response = self.client.post(verify, {"token": token_for(device)})
        self.assertRedirects(response, reverse("compliance:checklist"))

    def test_verify_ignores_offsite_next(self):
        device = TOTPDevice.objects.create(user=self.user, name="phone", confirmed=True)
        self.client.login(username="owner", password="a-long-test-password")
        url = reverse("accounts:two_factor_verify") + "?next=https://evil.example/"
        response = self.client.post(url, {"token": token_for(device)})
        self.assertRedirects(response, reverse("compliance:dashboard"))

    def test_security_headers(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertIn("default-src 'self'", response["Content-Security-Policy"])
        self.assertEqual(response["X-Frame-Options"], "DENY")


@override_settings(**TEST_SETTINGS)
class AppTests(TestCase):
    def setUp(self):
        seed_all()
        user = get_user_model().objects.create_user("owner", password="a-long-test-password")
        device = TOTPDevice.objects.create(user=user, name="phone", confirmed=True)
        self.client.login(username="owner", password="a-long-test-password")
        self.client.post(reverse("accounts:two_factor_verify"), {"token": token_for(device)})

    def test_seed_is_idempotent_and_preserves_status(self):
        item = ChecklistItem.objects.get(code="GOV-01")
        item.status = ChecklistItem.DONE
        item.save()
        Operator.objects.all().delete()
        seed_all()
        self.assertEqual(ChecklistItem.objects.get(code="GOV-01").status, ChecklistItem.DONE)
        self.assertEqual(Operator.objects.count(), 0, "deleted examples must not come back")
        self.assertEqual(ChecklistItem.objects.filter(code="GOV-01").count(), 1)

    def test_every_page_renders(self):
        urls = [
            reverse(name)
            for name in (
                "compliance:dashboard", "compliance:checklist", "compliance:profile", "compliance:learn",
                "compliance:documents", "compliance:paia_report", "compliance:audit_log", "compliance:export",
                "accounts:password_change",
            )
        ]
        urls += [reverse("compliance:learn_topic", args=[slug]) for slug, _, _ in LEARN_TOPICS]
        for doc in documents.DOCUMENTS:
            urls += [reverse("compliance:document", args=[doc["slug"]]), reverse("compliance:document_download", args=[doc["slug"]])]
        urls += [reverse("compliance:checklist_item", args=[i.pk]) for i in ChecklistItem.objects.all()[:3]]
        for register in REGISTERS:
            urls += [reverse(register.url("list")), reverse(register.url("create"))]
            obj = register.model.objects.first()
            if obj:
                urls += [reverse(register.url(a), args=[obj.pk]) for a in ("detail", "update", "delete")]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_documents_show_placeholders_then_profile_values(self):
        response = self.client.get(reverse("compliance:document", args=["paia-manual"]))
        self.assertContains(response, '<mark class="ph">[Registered name]</mark>', html=True)
        profile_data = {
            "legal_name": "Acme Widgets (Pty) Ltd", "registration_number": "2015/123456/07",
            "business_description": "We make widgets.", "physical_address": "1 Main Rd, Pretoria",
            "email": "info@acme.co.za", "head_name": "Jane Doe", "io_name": "Jane Doe", "io_email": "privacy@acme.co.za",
        }
        self.client.post(reverse("compliance:profile"), profile_data)
        response = self.client.get(reverse("compliance:document", args=["paia-manual"]))
        self.assertContains(response, "Acme Widgets (Pty) Ltd")
        self.assertNotContains(response, "[Registered name]")
        download = self.client.get(reverse("compliance:document_download", args=["paia-manual"]))
        self.assertEqual(download["Content-Type"], "application/msword")

    def test_request_due_date_and_paia_figures(self):
        received = date(2026, 5, 10)
        self.client.post(
            reverse("compliance:request_create"),
            {"request_type": "access", "requester_name": "A Person", "received_on": received.isoformat(),
             "details": "Copy of my records", "status": "completed", "outcome": "granted_full"},
        )
        req = DataSubjectRequest.objects.get()
        self.assertEqual(req.due_date, received + timedelta(days=30))
        self.assertTrue(req.reference.startswith("DSR-"))
        response = self.client.get(reverse("compliance:paia_report") + "?year=2027")
        figures = dict(response.context["figures"])
        self.assertEqual(figures["Requests for access received"], 1)
        self.assertEqual(figures["Granted in full"], 1)

    def test_overdue_request_alert(self):
        DataSubjectRequest.objects.create(
            request_type="access", requester_name="Late", details="x", received_on=timezone.localdate() - timedelta(days=40)
        )
        response = self.client.get(reverse("compliance:dashboard"))
        self.assertContains(response, "is overdue")

    def test_notifiable_incident_alert(self):
        Incident.objects.create(title="Stolen laptop", cause="device", description="x", notifiable="yes")
        response = self.client.get(reverse("compliance:dashboard"))
        self.assertContains(response, "notify the Regulator")

    def test_recurring_task_reschedules(self):
        task = ComplianceTask.objects.create(title="Yearly", due_date=date(2026, 6, 30), recurrence="yearly")
        self.client.post(reverse("compliance:task_complete", args=[task.pk]))
        self.assertTrue(ComplianceTask.objects.filter(title="Yearly", due_date=date(2027, 6, 30), done_on__isnull=True).exists())

    def test_add_months_clamps_day(self):
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(add_months(date(2027, 11, 30), 3), date(2028, 2, 29))

    def test_checklist_update_records_completion(self):
        item = ChecklistItem.objects.get(code="GOV-02")
        self.client.post(reverse("compliance:checklist_item", args=[item.pk]), {"status": "done", "evidence": "Registered"})
        item.refresh_from_db()
        self.assertEqual(item.completed_on, timezone.localdate())
        self.assertTrue(AuditEntry.objects.filter(action="updated", summary__contains="GOV-02").exists())

    def test_issue_detection(self):
        op = Operator.objects.create(name="Overseas", service="x", outside_sa=True)
        self.assertIn("Cross-border basis not documented (s72)", op.issues)
        activity = ProcessingActivity.objects.create(name="x", data_subjects="y", personal_info="z", purpose="p", lawful_basis="contract")
        self.assertIn("No retention period (s14)", activity.issues)
        self.assertEqual(Risk(likelihood=5, impact=3).level, "high")

    def test_json_export_and_backup(self):
        response = self.client.get(reverse("compliance:export_json"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"compliance.checklistitem", response.content)

    def test_backup_download_rejects_path_traversal(self):
        response = self.client.get(reverse("compliance:backup_download", args=["..%2Fpopia.sqlite3"]))
        self.assertEqual(response.status_code, 404)

    def test_multiple_choice_field_renders_as_group(self):
        Operator.objects.create(name="Payroll bureau", service="Payroll")
        response = self.client.get(reverse("compliance:activity_create"))
        html = response.content.decode()
        self.assertIn('<fieldset class="choice-group">', html)
        # No label wrapped around the whole list of checkboxes (nested labels are invalid HTML).
        self.assertNotIn('<label><div id="id_operators">', html)

    def test_backup_leaves_only_complete_files(self):
        # The test database is in memory and locked by this test's transaction, so back up a real file.
        with tempfile.TemporaryDirectory() as data, tempfile.TemporaryDirectory() as out:
            db, out = Path(data) / "popia.sqlite3", Path(out)
            conn = sqlite3.connect(db)
            conn.execute("CREATE TABLE t (x)")
            conn.close()
            stale = out / ".tmp-interrupted"  # left behind by a killed run
            stale.mkdir()
            os.utime(stale, (0, 0))
            with mock.patch.dict(settings.DATABASES["default"], NAME=str(db)), self.settings(BACKUP_DIR=out):
                call_command("backup_db", stdout=StringIO())
            files = list(out.iterdir())
            self.assertEqual(len(files), 1, files)
            self.assertTrue(files[0].name.startswith("popia-"))
            with gzip.open(files[0]) as packed:
                self.assertEqual(packed.read(16), b"SQLite format 3\x00")
