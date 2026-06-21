import time
from datetime import date as real_date
from unittest.mock import patch

from django.test import TestCase

from apps.portfolio.models import (
    About,
    Certification,
    Education,
    Experience,
    Lead,
    Project,
    Skill,
    SocialSettings,
    Summary,
)


class AboutModelTest(TestCase):
    def test_str(self):
        about = About.objects.create(title="About Luis", content="Some content")
        self.assertEqual(str(about), "About Luis")

    def test_auto_timestamps_set(self):
        about = About.objects.create(title="About Me", content="Content")
        self.assertIsNotNone(about.created_at)
        self.assertIsNotNone(about.updated_at)

    def test_updated_at_changes_on_save(self):
        about = About.objects.create(title="About Me", content="Content")
        original = about.updated_at
        time.sleep(0.05)
        about.title = "New Title"
        about.save()
        about.refresh_from_db()
        self.assertGreater(about.updated_at, original)

    def test_profile_image_optional(self):
        about = About.objects.create(title="About Me", content="Content")
        self.assertFalse(about.profile_image)


class SkillModelTest(TestCase):
    def test_str(self):
        skill = Skill.objects.create(name="Python", category="Programming Languages")
        self.assertEqual(str(skill), "Python (Programming Languages)")

    def test_years_of_experience_default(self):
        skill = Skill.objects.create(name="Python", category="Languages")
        self.assertEqual(skill.years_of_experience, 1)

    def test_ordering_by_category_asc_then_experience_desc(self):
        Skill.objects.create(name="Django", category="Frameworks", years_of_experience=3)
        Skill.objects.create(name="Python", category="Languages", years_of_experience=5)
        Skill.objects.create(name="React", category="Frameworks", years_of_experience=2)
        skills = list(Skill.objects.all())
        # Frameworks (F) < Languages (L); within Frameworks: most years first
        self.assertEqual(skills[0].name, "Django")
        self.assertEqual(skills[1].name, "React")
        self.assertEqual(skills[2].name, "Python")


class ProjectModelTest(TestCase):
    def test_str(self):
        project = Project.objects.create(
            title="My Portfolio", description="A portfolio site", technologies="Django,Python"
        )
        self.assertEqual(str(project), "My Portfolio")

    def test_featured_default_is_false(self):
        project = Project.objects.create(title="Test", description="Desc", technologies="Python")
        self.assertFalse(project.featured)

    def test_ordering_featured_first(self):
        Project.objects.create(title="Regular", description="d", technologies="T", featured=False)
        Project.objects.create(title="Featured", description="d", technologies="T", featured=True)
        projects = list(Project.objects.all())
        self.assertEqual(projects[0].title, "Featured")
        self.assertEqual(projects[1].title, "Regular")

    def test_optional_fields(self):
        project = Project.objects.create(
            title="Test Project", description="Description", technologies="Python"
        )
        self.assertIsNone(project.github_url)
        self.assertIsNone(project.live_url)
        self.assertFalse(project.image)


class SocialSettingsModelTest(TestCase):
    def test_str(self):
        social = SocialSettings.objects.create()
        self.assertEqual(str(social), "Social Media Settings")

    def test_all_url_fields_optional(self):
        social = SocialSettings.objects.create()
        self.assertIsNone(social.linkedin_url)
        self.assertIsNone(social.twitter_url)
        self.assertIsNone(social.facebook_url)
        self.assertIsNone(social.github_url)

    def test_create_with_all_four_urls(self):
        social = SocialSettings.objects.create(
            linkedin_url="https://linkedin.com/in/test",
            twitter_url="https://twitter.com/test",
            facebook_url="https://facebook.com/test",
            github_url="https://github.com/test",
        )
        self.assertEqual(social.linkedin_url, "https://linkedin.com/in/test")
        self.assertEqual(social.twitter_url, "https://twitter.com/test")
        self.assertEqual(social.facebook_url, "https://facebook.com/test")
        self.assertEqual(social.github_url, "https://github.com/test")


class ExperienceModelTest(TestCase):
    def _make(self, start, end=None, current=False):
        return Experience.objects.create(
            company="Acme Corp",
            position="Developer",
            description="Work description",
            start_date=start,
            end_date=end,
            current=current,
        )

    def test_str(self):
        exp = self._make(real_date(2024, 1, 1))
        self.assertEqual(str(exp), "Developer at Acme Corp")

    def test_ordering_by_start_date_desc(self):
        Experience.objects.create(
            company="Old Corp", position="Dev", description="d",
            start_date=real_date(2020, 1, 1),
        )
        Experience.objects.create(
            company="New Corp", position="Dev", description="d",
            start_date=real_date(2023, 1, 1),
        )
        exps = list(Experience.objects.all())
        self.assertEqual(exps[0].company, "New Corp")
        self.assertEqual(exps[1].company, "Old Corp")

    def test_duration_2_years(self):
        exp = self._make(real_date(2024, 1, 1), end=real_date(2026, 1, 1))
        self.assertEqual(exp.duration, "2 years")

    def test_duration_1_year_5_months(self):
        exp = self._make(real_date(2024, 1, 1), end=real_date(2025, 6, 1))
        self.assertEqual(exp.duration, "1 year, 5 months")

    def test_duration_5_months(self):
        exp = self._make(real_date(2026, 1, 1), end=real_date(2026, 6, 1))
        self.assertEqual(exp.duration, "5 months")

    def test_duration_1_year_no_months_suffix(self):
        exp = self._make(real_date(2025, 1, 1), end=real_date(2026, 1, 1))
        self.assertEqual(exp.duration, "1 year")

    def test_duration_current_uses_today(self):
        # start 2025-01-21 → today 2026-06-21 → 1 year, 5 months
        exp = self._make(real_date(2025, 1, 21), current=True)
        with patch('datetime.date') as mock_date:
            mock_date.today.return_value = real_date(2026, 6, 21)
            result = exp.duration
        self.assertEqual(result, "1 year, 5 months")


class SummaryModelTest(TestCase):
    def test_str(self):
        summary = Summary.objects.create(title="Professional Summary", content="Content")
        self.assertEqual(str(summary), "Professional Summary")

    def test_default_title(self):
        summary = Summary.objects.create(content="Some bio text")
        self.assertEqual(summary.title, "Professional Summary")

    def test_create(self):
        summary = Summary.objects.create(title="My Summary", content="Some professional bio")
        self.assertEqual(Summary.objects.count(), 1)
        self.assertEqual(summary.pk, Summary.objects.first().pk)


class CertificationModelTest(TestCase):
    def _make(self, issue_date, expiry_date=None):
        return Certification.objects.create(
            name="AWS Certified",
            issuing_organization="Amazon",
            issue_date=issue_date,
            expiry_date=expiry_date,
        )

    def test_str(self):
        cert = self._make(real_date(2024, 1, 1))
        self.assertEqual(str(cert), "AWS Certified - Amazon")

    def test_is_expired_when_expiry_in_past(self):
        cert = self._make(real_date(2020, 1, 1), expiry_date=real_date(2025, 1, 1))
        with patch('datetime.date') as mock_date:
            mock_date.today.return_value = real_date(2026, 6, 21)
            self.assertTrue(cert.is_expired)

    def test_is_not_expired_when_expiry_in_future(self):
        cert = self._make(real_date(2024, 1, 1), expiry_date=real_date(2027, 1, 1))
        with patch('datetime.date') as mock_date:
            mock_date.today.return_value = real_date(2026, 6, 21)
            self.assertFalse(cert.is_expired)

    def test_is_not_expired_when_no_expiry_date(self):
        cert = self._make(real_date(2024, 1, 1))
        self.assertFalse(cert.is_expired)

    def test_ordering_by_issue_date_desc(self):
        self._make(real_date(2022, 1, 1))
        self._make(real_date(2024, 6, 1))
        certs = list(Certification.objects.all())
        self.assertGreater(certs[0].issue_date, certs[1].issue_date)

    def test_description_optional(self):
        cert = self._make(real_date(2024, 1, 1))
        self.assertIsNone(cert.description)


class EducationModelTest(TestCase):
    def _make(self, start, end=None, current=False):
        return Education.objects.create(
            institution="MIT",
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            start_date=start,
            end_date=end,
            current=current,
        )

    def test_str(self):
        edu = self._make(real_date(2019, 9, 1), end=real_date(2023, 6, 1))
        self.assertEqual(str(edu), "Bachelor of Science in Computer Science - MIT")

    def test_duration_past_end_date(self):
        edu = self._make(real_date(2019, 9, 1), end=real_date(2023, 9, 1))
        self.assertEqual(edu.duration, "4 years")

    def test_duration_current_uses_today(self):
        # start 2024-09-01 → today 2026-06-21 → 2 years
        edu = self._make(real_date(2024, 9, 1), current=True)
        with patch('datetime.date') as mock_date:
            mock_date.today.return_value = real_date(2026, 6, 21)
            result = edu.duration
        self.assertEqual(result, "2 years")

    def test_duration_less_than_1_year(self):
        edu = self._make(real_date(2026, 1, 1), end=real_date(2026, 6, 1))
        self.assertEqual(edu.duration, "5 months")

    def test_ordering_by_start_date_desc(self):
        self._make(real_date(2015, 9, 1), end=real_date(2019, 6, 1))
        self._make(real_date(2020, 9, 1), end=real_date(2024, 6, 1))
        edus = list(Education.objects.all())
        self.assertGreater(edus[0].start_date, edus[1].start_date)

    def test_optional_fields(self):
        edu = self._make(real_date(2020, 9, 1))
        self.assertIsNone(edu.end_date)
        self.assertIsNone(edu.grade)
        self.assertIsNone(edu.description)
        self.assertFalse(edu.current)


class LeadModelTest(TestCase):
    def test_str(self):
        lead = Lead.objects.create(name="John Doe", email="john@example.com")
        self.assertEqual(str(lead), "John Doe (john@example.com)")

    def test_downloaded_at_auto_set(self):
        lead = Lead.objects.create(name="Jane Smith", email="jane@example.com")
        self.assertIsNotNone(lead.downloaded_at)

    def test_ordering_most_recent_first(self):
        Lead.objects.create(name="First", email="first@example.com")
        time.sleep(0.05)
        Lead.objects.create(name="Second", email="second@example.com")
        leads = list(Lead.objects.all())
        self.assertEqual(leads[0].name, "Second")
        self.assertEqual(leads[1].name, "First")

    def test_valid_creation(self):
        lead = Lead.objects.create(name="Test User", email="test@example.com")
        self.assertEqual(lead.name, "Test User")
        self.assertEqual(lead.email, "test@example.com")
        self.assertEqual(Lead.objects.count(), 1)
