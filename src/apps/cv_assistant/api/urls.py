"""URL routing for the cv_assistant API."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CVVersionViewSet,
    JobApplicationViewSet,
    RecruiterResponseViewSet,
)

router = DefaultRouter()
router.register(r"jobs", JobApplicationViewSet, basename="job")
router.register(r"cv-versions", CVVersionViewSet, basename="cv-version")
router.register(r"recruiter-responses", RecruiterResponseViewSet, basename="recruiter-response")

app_name = "cv_assistant_api"

urlpatterns = [
    # JWT auth endpoints scoped under /api/v1/cv-assistant/
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Registered viewsets
    path("", include(router.urls)),
]