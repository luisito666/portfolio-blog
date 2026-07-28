"""Permission classes for the cv_assistant API."""
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Only allows staff (admin) users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )