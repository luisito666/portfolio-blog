"""
Health check views for Kubernetes probes.

These views bypass ALLOWED_HOSTS validation via HealthCheckMiddleware
to work correctly with Kubernetes liveness/readiness probes.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache


def liveness(request):
    """
    Liveness probe - returns 200 if the Django server is running.
    This is a basic check that the application code is loaded and responding.
    """
    return JsonResponse({'status': 'alive'}, status=200)


def readiness(request):
    """
    Readiness probe - returns 200 if the application is ready to serve requests.
    Checks database connectivity.
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()

        return JsonResponse({'status': 'ready', 'database': 'ok'}, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'database': 'error',
            'error': str(e)
        }, status=503)


def health(request):
    """
    General health check endpoint for manual use or monitoring.
    Returns detailed health status including database and cache (if configured).
    """
    health_status = {
        'status': 'healthy',
        'checks': {}
    }

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = f'error: {str(e)}'

    # Check cache (if configured)
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['checks']['cache'] = 'ok'
    except Exception:
        # Cache not configured or unavailable - not a critical failure
        health_status['checks']['cache'] = 'not_configured'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
