"""URL routing for the cv_assistant API."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import JobApplicationViewSet

router = DefaultRouter()
router.register(r"jobs", JobApplicationViewSet, basename="job")

app_name = "cv_assistant_api"

urlpatterns = [
    # JWT auth endpoints scoped under /api/v1/cv-assistant/
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Registered viewsets
    path("", include(router.urls)),
]