"""APITestCase scaffolding for the cv_assistant API (Task 7+).

Shared helpers and per-task test classes. Tests run against the SQLite shim
(`core.settings_test_sqlite`) so PostgreSQL is not required.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

# Dotted path used to mock the AI client without making real API calls.
AI_CLIENT_PATH = "apps.cv_assistant.services.ai_client.chat_completion"

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