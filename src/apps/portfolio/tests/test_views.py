import json
import secrets
from datetime import date
from unittest.mock import MagicMock, patch

from django.core.signing import TimestampSigner
from django.test import TestCase
from django.urls import reverse

from apps.portfolio.models import (
    About,
    Certification,
    Education,
    Experience,
    Lead,
    Project,
    Skill,
    Summary,
)


class TestHomeView(TestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse('portfolio:home'))
        self.assertTemplateUsed(response, 'portfolio/home.html')

    def test_context_contains_about_instance(self):
        about = About.objects.create(title='About Me', content='Hello')
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.context['about'], about)

    def test_context_about_html_when_about_has_content(self):
        About.objects.create(title='About', content='**Bold**')
        response = self.client.get(reverse('portfolio:home'))
        self.assertIn('about_html', response.context)
        self.assertIn('<strong>Bold</strong>', response.context['about_html'])

    def test_context_contains_skills_by_category(self):
        Skill.objects.create(name='Python', category='Languages', years_of_experience=3)
        response = self.client.get(reverse('portfolio:home'))
        self.assertIn('skills_by_category', response.context)
        self.assertIsInstance(response.context['skills_by_category'], dict)
        self.assertIn('Languages', response.context['skills_by_category'])

    def test_context_contains_all_projects(self):
        Project.objects.create(title='P1', description='desc', technologies='T1')
        Project.objects.create(title='P2', description='desc', technologies='T2')
        response = self.client.get(reverse('portfolio:home'))
        self.assertIn('projects', response.context)
        self.assertEqual(len(list(response.context['projects'])), 2)

    def test_no_about_html_when_about_missing(self):
        response = self.client.get(reverse('portfolio:home'))
        self.assertIsNone(response.context['about'])
        self.assertNotIn('about_html', response.context)

    def test_projects_have_description_html_attribute(self):
        Project.objects.create(title='P1', description='**Bold**', technologies='T')
        response = self.client.get(reverse('portfolio:home'))
        projects = list(response.context['projects'])
        self.assertTrue(hasattr(projects[0], 'description_html'))
        self.assertIn('<strong>Bold</strong>', projects[0].description_html)


class TestProjectDetailView(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='My Project',
            description='**Bold** description',
            technologies='Python, Django',
        )

    def test_get_existing_project_returns_200(self):
        url = reverse('portfolio:project_detail', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        url = reverse('portfolio:project_detail', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'portfolio/project_detail.html')

    def test_context_contains_project_description_html(self):
        url = reverse('portfolio:project_detail', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertIn('project_description_html', response.context)
        self.assertIn('<strong>Bold</strong>', response.context['project_description_html'])

    def test_context_contains_project_instance(self):
        url = reverse('portfolio:project_detail', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.context['project'], self.project)

    def test_nonexistent_pk_returns_404(self):
        url = reverse('portfolio:project_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_url_name_reverses_correctly(self):
        url = reverse('portfolio:project_detail', kwargs={'pk': self.project.pk})
        self.assertEqual(url, f'/project/{self.project.pk}/')


class TestExperienceListView(TestCase):
    def _make_experience(self):
        return Experience.objects.create(
            company='Acme',
            position='Developer',
            description='**Work** description',
            start_date=date(2022, 1, 1),
        )

    def _make_certification(self, description=None):
        return Certification.objects.create(
            name='AWS',
            issuing_organization='Amazon',
            issue_date=date(2023, 1, 1),
            description=description,
        )

    def _make_education(self, description=None):
        return Education.objects.create(
            institution='MIT',
            degree='BSc',
            field_of_study='CS',
            start_date=date(2018, 9, 1),
            end_date=date(2022, 6, 1),
            description=description,
        )

    def test_get_returns_200(self):
        response = self.client.get(reverse('portfolio:experience_list'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse('portfolio:experience_list'))
        self.assertTemplateUsed(response, 'portfolio/experience_list.html')

    def test_context_contains_summary_and_html_when_summary_exists(self):
        summary = Summary.objects.create(title='My Summary', content='**Great** bio')
        response = self.client.get(reverse('portfolio:experience_list'))
        self.assertEqual(response.context['summary'], summary)
        self.assertIn('summary_html', response.context)
        self.assertIn('<strong>Great</strong>', response.context['summary_html'])

    def test_no_summary_html_when_summary_missing(self):
        response = self.client.get(reverse('portfolio:experience_list'))
        self.assertIsNone(response.context['summary'])
        self.assertNotIn('summary_html', response.context)

    def test_context_contains_experiences_with_description_html(self):
        self._make_experience()
        response = self.client.get(reverse('portfolio:experience_list'))
        experiences = list(response.context['experiences'])
        self.assertEqual(len(experiences), 1)
        self.assertTrue(hasattr(experiences[0], 'description_html'))
        self.assertIn('<strong>Work</strong>', experiences[0].description_html)

    def test_context_contains_certifications_with_description_html(self):
        self._make_certification(description='**Cert** info')
        response = self.client.get(reverse('portfolio:experience_list'))
        certs = list(response.context['certifications'])
        self.assertEqual(len(certs), 1)
        self.assertTrue(hasattr(certs[0], 'description_html'))
        self.assertIn('<strong>Cert</strong>', certs[0].description_html)

    def test_context_certifications_no_description_html_when_no_description(self):
        cert = self._make_certification(description=None)
        response = self.client.get(reverse('portfolio:experience_list'))
        certs = list(response.context['certifications'])
        self.assertFalse(hasattr(certs[0], 'description_html'))

    def test_context_contains_education_list_with_description_html(self):
        self._make_education(description='**Study** notes')
        response = self.client.get(reverse('portfolio:experience_list'))
        edu_list = list(response.context['education_list'])
        self.assertEqual(len(edu_list), 1)
        self.assertTrue(hasattr(edu_list[0], 'description_html'))
        self.assertIn('<strong>Study</strong>', edu_list[0].description_html)

    def test_context_contains_recaptcha_public_key(self):
        response = self.client.get(reverse('portfolio:experience_list'))
        self.assertIn('recaptcha_public_key', response.context)


class TestDownloadCVView(TestCase):
    URL = '/download-cv/'

    def _post(self, data):
        return self.client.post(
            self.URL,
            data=json.dumps(data),
            content_type='application/json',
        )

    def test_missing_name_returns_400(self):
        response = self._post({'email': 'test@example.com', 'captcha': 'x'})
        self.assertEqual(response.status_code, 400)

    def test_missing_email_returns_400(self):
        response = self._post({'name': 'Test User', 'captcha': 'x'})
        self.assertEqual(response.status_code, 400)

    def test_valid_request_with_successful_captcha_returns_200(self):
        with patch('apps.portfolio.views.requests.post') as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {'success': True}
            mock_post.return_value = mock_resp

            response = self._post({'name': 'Test User', 'email': 'test@example.com', 'captcha': 'valid'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('message', data)
        self.assertIn('token', data)
        self.assertIsInstance(data['token'], str)

    def test_valid_request_creates_lead(self):
        with patch('apps.portfolio.views.requests.post') as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {'success': True}
            mock_post.return_value = mock_resp

            self._post({'name': 'Test User', 'email': 'test@example.com', 'captcha': 'valid'})

        self.assertEqual(Lead.objects.count(), 1)
        lead = Lead.objects.first()
        self.assertEqual(lead.name, 'Test User')
        self.assertEqual(lead.email, 'test@example.com')

    def test_failed_captcha_returns_400(self):
        with patch('apps.portfolio.views.requests.post') as mock_post:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {'success': False}
            mock_post.return_value = mock_resp

            response = self._post({'name': 'Test User', 'email': 'test@example.com', 'captcha': 'bad'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid reCAPTCHA', response.json()['error'])

    def test_captcha_exception_returns_500(self):
        with patch('apps.portfolio.views.requests.post') as mock_post:
            mock_post.side_effect = Exception('Network error')

            response = self._post({'name': 'Test User', 'email': 'test@example.com', 'captcha': 'x'})

        self.assertEqual(response.status_code, 500)


class TestGeneratePDFView(TestCase):
    URL = '/generate-pdf/'

    def test_no_token_returns_403(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 403)
        self.assertIn('Access denied', response.content.decode())

    def test_invalid_token_returns_403(self):
        response = self.client.get(self.URL + '?token=garbage:invalid:token')
        self.assertEqual(response.status_code, 403)
        self.assertIn('Invalid or expired', response.content.decode())

    def test_expired_token_returns_403(self):
        with patch('apps.portfolio.views.TimestampSigner') as MockSigner:
            mock_signer = MagicMock()
            mock_signer.unsign.side_effect = Exception('Signature expired')
            MockSigner.return_value = mock_signer

            response = self.client.get(self.URL + '?token=sometoken')

        self.assertEqual(response.status_code, 403)

    def test_valid_token_returns_pdf_response(self):
        signer = TimestampSigner()
        token = signer.sign(secrets.token_hex(16))

        with patch('apps.portfolio.views.pisa') as mock_pisa, \
             patch('apps.portfolio.views.get_template') as mock_get_template:
            mock_template = MagicMock()
            mock_template.render.return_value = '<html><body>CV</body></html>'
            mock_get_template.return_value = mock_template

            mock_status = MagicMock()
            mock_status.err = False
            mock_pisa.CreatePDF.return_value = mock_status

            response = self.client.get(self.URL + f'?token={token}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_pisa_error_returns_error_response(self):
        signer = TimestampSigner()
        token = signer.sign(secrets.token_hex(16))

        with patch('apps.portfolio.views.pisa') as mock_pisa, \
             patch('apps.portfolio.views.get_template') as mock_get_template:
            mock_template = MagicMock()
            mock_template.render.return_value = '<html><body>CV</body></html>'
            mock_get_template.return_value = mock_template

            mock_status = MagicMock()
            mock_status.err = True
            mock_pisa.CreatePDF.return_value = mock_status

            response = self.client.get(self.URL + f'?token={token}')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'We had some errors', response.content)
