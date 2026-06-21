from django.test import RequestFactory, TestCase

from apps.portfolio.context_processors import social_media
from apps.portfolio.models import SocialSettings


class TestSocialMediaContextProcessor(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _request(self):
        return self.factory.get('/')

    def test_returns_dict_with_social_settings_key(self):
        result = social_media(self._request())
        self.assertIsInstance(result, dict)
        self.assertIn('social_settings', result)

    def test_returns_social_settings_instance_when_exists(self):
        social = SocialSettings.objects.create(
            linkedin_url='https://linkedin.com/in/test',
            github_url='https://github.com/test',
        )
        result = social_media(self._request())
        self.assertEqual(result['social_settings'], social)

    def test_returns_none_when_no_social_settings(self):
        result = social_media(self._request())
        self.assertIsNone(result['social_settings'])

    def test_does_not_raise_when_db_empty(self):
        try:
            result = social_media(self._request())
        except Exception as exc:
            self.fail(f'social_media raised an exception with empty DB: {exc}')
        self.assertIn('social_settings', result)

    def test_returns_first_instance_when_multiple_exist(self):
        first = SocialSettings.objects.create(linkedin_url='https://linkedin.com/in/first')
        SocialSettings.objects.create(linkedin_url='https://linkedin.com/in/second')
        result = social_media(self._request())
        self.assertEqual(result['social_settings'], first)
