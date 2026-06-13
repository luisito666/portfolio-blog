"""
Middleware for health check endpoints.

This middleware allows health check requests to bypass ALLOWED_HOSTS validation
by replacing CommonMiddleware with a custom version that exempts health paths.
"""
from django.middleware.common import CommonMiddleware
from django.core.exceptions import DisallowedHost


# Paths that should bypass ALLOWED_HOSTS validation
HEALTH_CHECK_PATHS = {'/health', '/readiness', '/liveness'}


class HealthCheckHostMiddleware(CommonMiddleware):
    """
    Custom CommonMiddleware that bypasses ALLOWED_HOSTS validation for health check paths.

    This replaces Django's CommonMiddleware and extends it to skip host validation
    for requests to health check endpoints, allowing Kubernetes probes to work
    regardless of the Host header sent by the kubelet.

    To use: Replace 'django.middleware.common.CommonMiddleware' with
    'core.middleware.HealthCheckHostMiddleware' in MIDDLEWARE settings.
    """

    def process_request(self, request):
        """
        Override process_request to bypass ALLOWED_HOSTS validation for health checks.

        For health check paths, we skip calling the parent's process_request
        which would raise DisallowedHost for invalid Host headers.
        """
        # Skip ALLOWED_HOSTS validation for health check paths
        if request.path in HEALTH_CHECK_PATHS:
            # Set a flag that can be used by other code if needed
            request.is_health_check = True
            return None

        # For all other paths, use normal CommonMiddleware validation
        return super().process_request(request)


# Original middleware that didn't work - kept for reference
class HealthCheckMiddleware:
    """
    DEPRECATED: This approach doesn't work because CommonMiddleware runs before.
    Use HealthCheckHostMiddleware instead.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in HEALTH_CHECK_PATHS:
            request.health_check_bypass = True
        response = self.get_response(request)
        return response
