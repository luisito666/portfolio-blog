from django.test import TestCase
from django.urls import resolve, reverse


class TestURLPatterns(TestCase):
    def test_home_url_reverses(self):
        self.assertEqual(reverse('portfolio:home'), '/')

    def test_project_detail_url_reverses(self):
        self.assertEqual(reverse('portfolio:project_detail', kwargs={'pk': 1}), '/project/1/')

    def test_experience_list_url_reverses(self):
        self.assertEqual(reverse('portfolio:experience_list'), '/experience/')

    def test_download_cv_url_reverses(self):
        self.assertEqual(reverse('portfolio:download_cv'), '/download-cv/')

    def test_generate_pdf_url_reverses(self):
        self.assertEqual(reverse('portfolio:generate_pdf'), '/generate-pdf/')

    def test_app_namespace_is_portfolio(self):
        resolver = resolve('/')
        self.assertEqual(resolver.app_name, 'portfolio')

    def test_home_resolves_to_home_view(self):
        from apps.portfolio.views import HomeView
        resolver = resolve('/')
        self.assertEqual(resolver.func.view_class, HomeView)

    def test_project_detail_resolves_to_view(self):
        from apps.portfolio.views import ProjectDetailView
        resolver = resolve('/project/1/')
        self.assertEqual(resolver.func.view_class, ProjectDetailView)

    def test_experience_list_resolves_to_view(self):
        from apps.portfolio.views import ExperienceListView
        resolver = resolve('/experience/')
        self.assertEqual(resolver.func.view_class, ExperienceListView)

    def test_download_cv_resolves_to_view(self):
        from apps.portfolio.views import DownloadCVView
        resolver = resolve('/download-cv/')
        self.assertEqual(resolver.func.view_class, DownloadCVView)

    def test_generate_pdf_resolves_to_view(self):
        from apps.portfolio.views import GeneratePDFView
        resolver = resolve('/generate-pdf/')
        self.assertEqual(resolver.func.view_class, GeneratePDFView)

    def test_all_named_url_patterns_are_reversible(self):
        names = ['home', 'experience_list', 'download_cv', 'generate_pdf']
        for name in names:
            with self.subTest(name=name):
                reverse(f'portfolio:{name}')
        reverse('portfolio:project_detail', kwargs={'pk': 1})

    def test_integration_home_returns_200(self):
        url = reverse('portfolio:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
