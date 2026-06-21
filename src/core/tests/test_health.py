from unittest.mock import patch

from django.test import TestCase


class TestLiveness(TestCase):
    def test_returns_200(self):
        response = self.client.get('/liveness')
        self.assertEqual(response.status_code, 200)

    def test_response_json_is_alive(self):
        response = self.client.get('/liveness')
        self.assertEqual(response.json(), {'status': 'alive'})

    def test_content_type_is_json(self):
        response = self.client.get('/liveness')
        self.assertIn('application/json', response['Content-Type'])

    def test_url_path_resolves(self):
        # No URL name registered; verify the path exists and returns 200
        response = self.client.get('/liveness')
        self.assertEqual(response.status_code, 200)


class TestReadiness(TestCase):
    def test_returns_200_when_db_up(self):
        response = self.client.get('/readiness')
        self.assertEqual(response.status_code, 200)

    def test_response_json_ready(self):
        response = self.client.get('/readiness')
        data = response.json()
        self.assertEqual(data['status'], 'ready')
        self.assertEqual(data['database'], 'ok')

    def test_content_type_is_json(self):
        response = self.client.get('/readiness')
        self.assertIn('application/json', response['Content-Type'])

    def test_returns_503_when_db_unavailable(self):
        with patch('core.health.connection') as mock_conn:
            mock_conn.cursor.side_effect = Exception('DB down')
            response = self.client.get('/readiness')
        self.assertEqual(response.status_code, 503)

    def test_response_json_not_ready_when_db_unavailable(self):
        with patch('core.health.connection') as mock_conn:
            mock_conn.cursor.side_effect = Exception('DB down')
            response = self.client.get('/readiness')
        data = response.json()
        self.assertEqual(data['status'], 'not_ready')
        self.assertEqual(data['database'], 'error')
        self.assertIn('error', data)


class TestHealth(TestCase):
    def test_returns_200_when_db_up(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

    def test_response_json_healthy(self):
        response = self.client.get('/health')
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['checks']['database'], 'ok')

    def test_content_type_is_json(self):
        response = self.client.get('/health')
        self.assertIn('application/json', response['Content-Type'])

    def test_cache_check_present_in_response(self):
        response = self.client.get('/health')
        data = response.json()
        self.assertIn('cache', data['checks'])
        self.assertIn(data['checks']['cache'], ('ok', 'not_configured'))

    def test_returns_503_when_db_unavailable(self):
        with patch('core.health.connection') as mock_conn:
            mock_conn.cursor.side_effect = Exception('DB down')
            response = self.client.get('/health')
        self.assertEqual(response.status_code, 503)

    def test_response_json_unhealthy_when_db_unavailable(self):
        with patch('core.health.connection') as mock_conn:
            mock_conn.cursor.side_effect = Exception('DB down')
            response = self.client.get('/health')
        data = response.json()
        self.assertEqual(data['status'], 'unhealthy')
        self.assertIn('database', data['checks'])
        self.assertTrue(data['checks']['database'].startswith('error:'))
