"""Tests for the IsAdminUser permission class (Task 7).

Uses a minimal standalone ViewSet wired into this module's own urlpatterns so
the permission can be exercised without depending on the JobApplication CRUD
endpoints from Task 8 being registered yet.
"""

from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework import serializers, viewsets
from rest_framework.routers import DefaultRouter
from rest_framework.test import APIClient, APITestCase
from django.test import override_settings

from apps.cv_assistant.api.permissions import IsAdminUser
from apps.cv_assistant.models import JobApplication

User = get_user_model()


class _DummySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ["id", "company", "position"]


class _DummyViewSet(viewsets.ModelViewSet):
    """Minimal ViewSet guarded by IsAdminUser."""

    queryset = JobApplication.objects.all()
    serializer_class = _DummySerializer
    permission_classes = [IsAdminUser]


_router = DefaultRouter()
_router.register(r"dummy-jobs", _DummyViewSet, basename="dummy-job")

urlpatterns = [
    path("", include(_router.urls)),
]


URLCONF = __name__  # this module's dotted path, used as ROOT_URLCONF


class IsAdminUserPermissionTest(APITestCase):
    """Anonymous -> 401, authenticated non-staff -> 403, staff -> 200."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._override = override_settings(ROOT_URLCONF=URLCONF)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            username="staff", password="pw12345!", is_staff=True
        )
        cls.non_staff = User.objects.create_user(
            username="plain", password="pw12345!"
        )

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_denied(self):
        resp = self.client.get("/dummy-jobs/")
        self.assertEqual(resp.status_code, 401)

    def test_non_staff_forbidden(self):
        self.client.force_authenticate(user=self.non_staff)
        resp = self.client.get("/dummy-jobs/")
        self.assertEqual(resp.status_code, 403)

    def test_staff_allowed(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.get("/dummy-jobs/")
        self.assertEqual(resp.status_code, 200)