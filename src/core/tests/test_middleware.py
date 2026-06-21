from django.core.exceptions import DisallowedHost
from django.test import RequestFactory, TestCase, override_settings

from core.middleware import HEALTH_CHECK_PATHS, HealthCheckHostMiddleware


class TestHealthCheckHostMiddlewareUnit(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = HealthCheckHostMiddleware(get_response=lambda r: None)

    def test_health_path_bypasses_host_validation(self):
        request = self.factory.get('/health', HTTP_HOST='evil.example.com')
        result = self.middleware.process_request(request)
        self.assertIsNone(result)

    def test_health_path_sets_is_health_check_flag(self):
        request = self.factory.get('/health', HTTP_HOST='evil.example.com')
        self.middleware.process_request(request)
        self.assertTrue(getattr(request, 'is_health_check', False))

    def test_readiness_path_bypasses_host_validation(self):
        request = self.factory.get('/readiness', HTTP_HOST='evil.example.com')
        result = self.middleware.process_request(request)
        self.assertIsNone(result)

    def test_readiness_path_sets_is_health_check_flag(self):
        request = self.factory.get('/readiness', HTTP_HOST='evil.example.com')
        self.middleware.process_request(request)
        self.assertTrue(getattr(request, 'is_health_check', False))

    def test_liveness_path_bypasses_host_validation(self):
        request = self.factory.get('/liveness', HTTP_HOST='evil.example.com')
        result = self.middleware.process_request(request)
        self.assertIsNone(result)

    def test_liveness_path_sets_is_health_check_flag(self):
        request = self.factory.get('/liveness', HTTP_HOST='evil.example.com')
        self.middleware.process_request(request)
        self.assertTrue(getattr(request, 'is_health_check', False))

    @override_settings(ALLOWED_HOSTS=['localhost', '127.0.0.1'])
    def test_non_health_path_with_invalid_host_raises_disallowed_host(self):
        request = self.factory.get('/some-other-path', HTTP_HOST='evil.example.com')
        with self.assertRaises(DisallowedHost):
            self.middleware.process_request(request)

    @override_settings(ALLOWED_HOSTS=['localhost', '127.0.0.1'])
    def test_non_health_path_with_valid_host_returns_none(self):
        request = self.factory.get('/some-other-path', HTTP_HOST='localhost')
        result = self.middleware.process_request(request)
        self.assertIsNone(result)

    def test_health_check_paths_constant_contains_expected_paths(self):
        self.assertIn('/health', HEALTH_CHECK_PATHS)
        self.assertIn('/readiness', HEALTH_CHECK_PATHS)
        self.assertIn('/liveness', HEALTH_CHECK_PATHS)


@override_settings(ALLOWED_HOSTS=['localhost', '127.0.0.1'])
class TestHealthCheckHostMiddlewareIntegration(TestCase):
    def test_health_with_valid_host_returns_200(self):
        response = self.client.get('/health', HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 200)

    def test_health_with_invalid_host_still_returns_200(self):
        # HealthCheckHostMiddleware bypasses ALLOWED_HOSTS for /health
        response = self.client.get('/health', HTTP_HOST='evil.example.com')
        self.assertEqual(response.status_code, 200)

    def test_readiness_with_invalid_host_still_returns_200(self):
        response = self.client.get('/readiness', HTTP_HOST='evil.example.com')
        self.assertEqual(response.status_code, 200)

    def test_liveness_with_invalid_host_still_returns_200(self):
        response = self.client.get('/liveness', HTTP_HOST='evil.example.com')
        self.assertEqual(response.status_code, 200)

    def test_non_health_path_with_invalid_host_returns_400(self):
        # DisallowedHost from super().process_request() is converted to 400
        response = self.client.get('/admin/', HTTP_HOST='evil.example.com')
        self.assertEqual(response.status_code, 400)
