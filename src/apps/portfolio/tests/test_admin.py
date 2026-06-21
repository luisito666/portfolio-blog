from datetime import date

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

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

User = get_user_model()


class AdminTestBase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='password'
        )

    def _request(self):
        request = self.factory.get('/')
        request.user = self.superuser
        return request

    def _admin_for(self, model):
        return admin.site._registry[model]


class TestAboutAdmin(AdminTestBase):
    def test_about_is_registered(self):
        self.assertIn(About, admin.site._registry)

    def test_list_display_fields(self):
        a = self._admin_for(About)
        for field in ('title', 'created_at', 'updated_at'):
            self.assertIn(field, a.list_display)

    def test_search_fields(self):
        a = self._admin_for(About)
        self.assertIn('title', a.search_fields)
        self.assertIn('content', a.search_fields)

    def test_readonly_fields(self):
        a = self._admin_for(About)
        self.assertIn('created_at', a.readonly_fields)
        self.assertIn('updated_at', a.readonly_fields)

    def test_has_add_permission_false_when_instance_exists(self):
        About.objects.create(title='About', content='Content')
        a = self._admin_for(About)
        self.assertFalse(a.has_add_permission(self._request()))

    def test_has_add_permission_true_when_no_instance(self):
        a = self._admin_for(About)
        self.assertTrue(a.has_add_permission(self._request()))


class TestSkillAdmin(AdminTestBase):
    def test_skill_is_registered(self):
        self.assertIn(Skill, admin.site._registry)

    def test_list_display_fields(self):
        a = self._admin_for(Skill)
        for field in ('name', 'category', 'years_of_experience', 'created_at'):
            self.assertIn(field, a.list_display)

    def test_search_fields(self):
        a = self._admin_for(Skill)
        self.assertIn('name', a.search_fields)
        self.assertIn('category', a.search_fields)

    def test_list_editable_includes_years_of_experience(self):
        a = self._admin_for(Skill)
        self.assertIn('years_of_experience', a.list_editable)


class TestProjectAdmin(AdminTestBase):
    def test_project_is_registered(self):
        self.assertIn(Project, admin.site._registry)

    def test_list_display_fields(self):
        a = self._admin_for(Project)
        for field in ('title', 'featured', 'created_at'):
            self.assertIn(field, a.list_display)

    def test_search_fields(self):
        a = self._admin_for(Project)
        for field in ('title', 'description', 'technologies'):
            self.assertIn(field, a.search_fields)

    def test_readonly_fields(self):
        a = self._admin_for(Project)
        self.assertIn('created_at', a.readonly_fields)
        self.assertIn('updated_at', a.readonly_fields)


class TestSocialSettingsAdmin(AdminTestBase):
    def test_social_settings_is_registered(self):
        self.assertIn(SocialSettings, admin.site._registry)

    def test_has_add_permission_false_when_instance_exists(self):
        SocialSettings.objects.create()
        a = self._admin_for(SocialSettings)
        self.assertFalse(a.has_add_permission(self._request()))

    def test_has_add_permission_true_when_no_instance(self):
        a = self._admin_for(SocialSettings)
        self.assertTrue(a.has_add_permission(self._request()))


class TestExperienceAdmin(AdminTestBase):
    def test_experience_is_registered(self):
        self.assertIn(Experience, admin.site._registry)

    def test_list_display_fields(self):
        a = self._admin_for(Experience)
        for field in ('position', 'company', 'start_date', 'end_date', 'current'):
            self.assertIn(field, a.list_display)

    def test_search_fields(self):
        a = self._admin_for(Experience)
        for field in ('company', 'position', 'description', 'location'):
            self.assertIn(field, a.search_fields)

    def test_list_editable_includes_current(self):
        a = self._admin_for(Experience)
        self.assertIn('current', a.list_editable)


class TestSummaryAdmin(AdminTestBase):
    def test_summary_is_registered(self):
        self.assertIn(Summary, admin.site._registry)

    def test_has_add_permission_false_when_instance_exists(self):
        Summary.objects.create(title='My Summary', content='Content')
        a = self._admin_for(Summary)
        self.assertFalse(a.has_add_permission(self._request()))

    def test_has_add_permission_true_when_no_instance(self):
        a = self._admin_for(Summary)
        self.assertTrue(a.has_add_permission(self._request()))


class TestCertificationAdmin(AdminTestBase):
    def test_certification_is_registered(self):
        self.assertIn(Certification, admin.site._registry)

    def test_list_display_fields(self):
        a = self._admin_for(Certification)
        for field in ('name', 'issuing_organization', 'issue_date', 'expiry_date'):
            self.assertIn(field, a.list_display)

    def test_is_expired_in_list_display(self):
        a = self._admin_for(Certification)
        self.assertIn('is_expired', a.list_display)

    def test_is_expired_is_custom_method_on_admin(self):
        from apps.portfolio.admin import CertificationAdmin
        self.assertTrue(callable(getattr(CertificationAdmin, 'is_expired', None)))

    def test_search_fields(self):
        a = self._admin_for(Certification)
        for field in ('name', 'issuing_organization', 'credential_id'):
            self.assertIn(field, a.search_fields)


class TestEducationAdmin(AdminTestBase):
    def test_education_is_registered(self):
        self.assertIn(Education, admin.site._registry)

    def test_list_display_fields(self):
        a = self._admin_for(Education)
        for field in ('degree', 'field_of_study', 'institution'):
            self.assertIn(field, a.list_display)

    def test_search_fields(self):
        a = self._admin_for(Education)
        for field in ('institution', 'degree', 'field_of_study'):
            self.assertIn(field, a.search_fields)


class TestLeadAdmin(AdminTestBase):
    def test_lead_is_registered(self):
        self.assertIn(Lead, admin.site._registry)

    def test_list_display_fields(self):
        a = self._admin_for(Lead)
        for field in ('name', 'email', 'downloaded_at'):
            self.assertIn(field, a.list_display)

    def test_readonly_fields_includes_downloaded_at(self):
        a = self._admin_for(Lead)
        self.assertIn('downloaded_at', a.readonly_fields)
