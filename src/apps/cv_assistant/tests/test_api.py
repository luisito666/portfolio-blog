"""APITestCase scaffolding for the cv_assistant API (Task 7+).

Shared helpers and per-task test classes. Tests run against the SQLite shim
(`core.settings_test_sqlite`) so PostgreSQL is not required.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.cv_assistant.models import JobApplication

User = get_user_model()

# Dotted path used to mock the AI client without making real API calls.
AI_CLIENT_PATH = "apps.cv_assistant.api.views.chat_completion"

JOBS_URL = "/api/v1/cv-assistant/jobs/"
TOKEN_URL = "/api/v1/cv-assistant/auth/login/"


class _AuthMixin:
    """Helper to obtain a JWT token and authenticate the APIClient."""

    @staticmethod
    def _jwt_auth(client, username, password):
        resp = client.post(
            TOKEN_URL, {"username": username, "password": password}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK, resp.content
        token = resp.json()["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return token


class JobApplicationCRUDTest(APITestCase, _AuthMixin):
    """Task 8: CRUD endpoints under /api/v1/cv-assistant/jobs/."""

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            username="staff", password="pw12345!", is_staff=True
        )
        cls.non_staff = User.objects.create_user(
            username="plain", password="pw12345!"
        )

    def setUp(self):
        # staff client for authenticated CRUD tests
        self.client.credentials(HTTP_AUTHORIZATION=None)
        self._jwt_auth(self.client, "staff", "pw12345!")

    def _payload(self, company="OpenAI", position="Backend Engineer"):
        return {
            "company": company,
            "position": position,
            "job_description": "We need a Django dev with REST experience.",
            "status": "draft",
        }

    # --- permission checks ---

    def test_anonymous_denied(self):
        self.client.credentials(HTTP_AUTHORIZATION=None)
        resp = self.client.get(JOBS_URL)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_staff_forbidden(self):
        client = self.__class__.client_class()
        self._jwt_auth(client, "plain", "pw12345!")
        resp = client.get(JOBS_URL)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_list_ok(self):
        resp = self.client.get(JOBS_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # --- CRUD ---

    def test_create_job(self):
        resp = self.client.post(JOBS_URL, self._payload(), format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json()["company"], "OpenAI")
        self.assertIn("id", resp.json())

    def test_list_jobs(self):
        self.client.post(JOBS_URL, self._payload(), format="json")
        self.client.post(
            JOBS_URL, self._payload("Anthropic", "ML Engineer"), format="json"
        )
        resp = self.client.get(JOBS_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.json().get("results", resp.json())
        self.assertEqual(len(results), 2)

    def test_retrieve_job(self):
        create = self.client.post(JOBS_URL, self._payload(), format="json").json()
        resp = self.client.get(f"{JOBS_URL}{create['id']}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()["position"], "Backend Engineer")

    def test_update_job(self):
        create = self.client.post(JOBS_URL, self._payload(), format="json").json()
        resp = self.client.patch(
            f"{JOBS_URL}{create['id']}/", {"position": "Senior Backend"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()["position"], "Senior Backend")

    def test_delete_job(self):
        create = self.client.post(JOBS_URL, self._payload(), format="json").json()
        resp = self.client.delete(f"{JOBS_URL}{create['id']}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(f"{JOBS_URL}{create['id']}/").status_code, 404)

from datetime import date
from apps.portfolio.models import (
    Certification, Education, Experience, Skill, SocialSettings, Summary,
)


def _seed_portfolio():
    """Seed the minimal portfolio models build_cv_context() needs."""
    if not Summary.objects.exists():
        Summary.objects.create(title="Summary", content="Experienced dev")
    if not Experience.objects.exists():
        Experience.objects.create(
            company="Acme", position="Backend Dev",
            description="Did backend work", start_date=date(2022, 1, 1),
        )
    if not Skill.objects.exists():
        Skill.objects.create(name="Python", category="Languages", years_of_experience=3)
    if not SocialSettings.objects.exists():
        SocialSettings.objects.create(linkedin_url="https://linkedin.com/in/test")
    if not Certification.objects.exists():
        Certification.objects.create(
            name="AWS Cert", issuing_organization="Amazon",
            issue_date=date(2023, 1, 1), description="Cloud cert",
        )
    if not Education.objects.exists():
        Education.objects.create(
            institution="MIT", degree="BSc", field_of_study="CS",
            start_date=date(2018, 9, 1), end_date=date(2022, 6, 1),
            description="Studied CS",
        )


class ChatEndpointsTest(APITestCase, _AuthMixin):
    """Task 9: /api/v1/cv-assistant/jobs/<pk>/messages/ GET and POST."""

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            username="staff", password="pw12345!", is_staff=True
        )

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=None)
        self._jwt_auth(self.client, "staff", "pw12345!")
        _seed_portfolio()
        self.job = JobApplication.objects.create(
            company="OpenAI", position="Backend Engineer",
            job_description="We need a Django dev with REST experience.",
        )

    @patch(AI_CLIENT_PATH, return_value="Hello from the AI!")
    def test_get_lists_messages(self, _mock):
        # create a couple of messages directly
        self.job.messages.create(role="user", content="hi")
        self.job.messages.create(role="assistant", content="hello")
        resp = self.client.get(f"{JOBS_URL}{self.job.pk}/messages/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()), 2)

    @patch(AI_CLIENT_PATH, return_value="AI reply text")
    def test_post_first_message_calls_ai_and_returns_both(self, mock_ai):
        resp = self.client.post(
            f"{JOBS_URL}{self.job.pk}/messages/",
            {"content": "Adapt my CV please"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["role"], "user")
        self.assertEqual(data[0]["content"], "Adapt my CV please")
        self.assertEqual(data[1]["role"], "assistant")
        self.assertEqual(data[1]["content"], "AI reply text")
        # AI client was invoked once
        mock_ai.assert_called_once()
        # both messages persisted
        self.assertEqual(self.job.messages.count(), 2)

    @patch(AI_CLIENT_PATH, return_value="Second reply")
    def test_post_missing_content_returns_400(self, _mock):
        resp = self.client.post(
            f"{JOBS_URL}{self.job.pk}/messages/", {}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Task 10: Generate CV version endpoint
# ---------------------------------------------------------------------------

# Dotted paths for mocking services used by the generate-cv endpoint.
PDF_GEN_PATH = "apps.cv_assistant.api.views.pdf_generator.generate_cv_pdf"

# A valid AI JSON response referencing the experience created by _seed_portfolio
# (id=1, since it's the first Experience row in the test DB).
VALID_AI_RESPONSE = (
    '{"summary": "Adapted summary for the role.", '
    '"experiences": [{"id": 1, "description_adapted": "Adapted description."}]}'
)


class GenerateCVTest(APITestCase, _AuthMixin):
    """Task 10: /api/v1/cv-assistant/jobs/<pk>/generate-cv/ endpoint."""

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            username="staff", password="pw12345!", is_staff=True
        )

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=None)
        self._jwt_auth(self.client, "staff", "pw12345!")
        _seed_portfolio()
        self.job = JobApplication.objects.create(
            company="OpenAI",
            position="Backend Engineer",
            job_description="We need a Django dev with REST experience.",
        )

    @patch(PDF_GEN_PATH, return_value=b"%PDF-1.4 fake pdf content")
    @patch(AI_CLIENT_PATH, return_value=VALID_AI_RESPONSE)
    def test_generate_cv_creates_version_1(self, _mock_ai, _mock_pdf):
        resp = self.client.post(
            f"{JOBS_URL}{self.job.pk}/generate-cv/",
            {"user_instructions": "Emphasize REST."},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertEqual(data["version_number"], 1)
        self.assertEqual(data["adapted_summary"], "Adapted summary for the role.")
        self.assertEqual(data["ai_model"], "gpt-4o-mini")
        # PDF file field should be populated
        self.assertTrue(data["pdf_file"])
        # CVVersion created and PDF non-empty on disk
        from apps.cv_assistant.models import CVVersion
        cv = CVVersion.objects.get(job_application=self.job, version_number=1)
        self.assertTrue(cv.pdf_file.name)
        cv.pdf_file.open("rb")
        content = cv.pdf_file.read()
        cv.pdf_file.close()
        self.assertTrue(len(content) > 0)
        # Job status updated
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, "cv_generated")

    @patch(PDF_GEN_PATH, return_value=b"%PDF-1.4 fake pdf content")
    @patch(AI_CLIENT_PATH, return_value=VALID_AI_RESPONSE)
    def test_generate_cv_second_call_creates_version_2(self, _mock_ai, _mock_pdf):
        # First call -> version 1
        self.client.post(
            f"{JOBS_URL}{self.job.pk}/generate-cv/", format="json"
        )
        # Second call -> version 2
        resp = self.client.post(
            f"{JOBS_URL}{self.job.pk}/generate-cv/", format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json()["version_number"], 2)
        from apps.cv_assistant.models import CVVersion
        self.assertEqual(
            CVVersion.objects.filter(job_application=self.job).count(), 2
        )
