"""Tests for the Language model and its integration into the CV pipeline.

Covers:
- Model string representation and ordering
- cv_builder.build_cv_context() exposing languages
- cv_pdf.html rendering the Languages section
- cv_adapter._format_base_cv_data() including languages in AI prompts
"""

from datetime import date

from django.template.loader import get_template
from django.test import TestCase

from apps.portfolio.models import (
    Education,
    Experience,
    Language,
    Skill,
    Summary,
)
from apps.cv_assistant.services import cv_adapter, cv_builder


def _make_summary():
    return Summary.objects.create(title='Summary', content='**Experienced** dev')


def _make_experience():
    return Experience.objects.create(
        company='Acme',
        position='Backend Dev',
        description='Did **backend** work',
        start_date=date(2022, 1, 1),
    )


def _make_language(name='English', level=Language.LEVEL_B2, display_order=1):
    return Language.objects.create(
        name=name,
        level=level,
        display_order=display_order,
    )


class TestLanguageModel(TestCase):
    def test_str_includes_level_display(self):
        lang = _make_language(name='Spanish', level=Language.LEVEL_NATIVE, display_order=0)
        self.assertEqual(str(lang), 'Spanish (Native)')

    def test_ordering_by_display_order_then_name(self):
        english = _make_language(name='English', display_order=1)
        spanish = _make_language(name='Spanish', display_order=0)
        languages = list(Language.objects.all())
        self.assertEqual(languages, [spanish, english])


class TestBuildCvContextLanguages(TestCase):
    def test_context_includes_languages_queryset(self):
        _make_summary()
        _make_experience()
        _make_language(name='Spanish', level=Language.LEVEL_NATIVE, display_order=0)
        _make_language(name='English', level=Language.LEVEL_B2, display_order=1)

        context = cv_builder.build_cv_context()

        languages = list(context['languages'])
        self.assertEqual(len(languages), 2)
        self.assertEqual(languages[0].name, 'Spanish')
        self.assertEqual(languages[1].name, 'English')

    def test_context_languages_empty_when_none_exist(self):
        _make_summary()
        _make_experience()

        context = cv_builder.build_cv_context()

        self.assertEqual(list(context['languages']), [])


class TestCvPdfTemplateLanguages(TestCase):
    def test_template_renders_languages_section(self):
        _make_summary()
        _make_experience()
        _make_language(name='Spanish', level=Language.LEVEL_NATIVE, display_order=0)
        _make_language(name='English', level=Language.LEVEL_B2, display_order=1)

        context = cv_builder.build_cv_context()
        html = get_template('portfolio/cv_pdf.html').render(context)

        self.assertIn('Languages', html)
        self.assertIn('Spanish (Native)', html)
        self.assertIn('English (B2)', html)

    def test_template_omits_section_when_no_languages(self):
        _make_summary()
        _make_experience()

        context = cv_builder.build_cv_context()
        html = get_template('portfolio/cv_pdf.html').render(context)

        self.assertNotIn('<h2>Languages</h2>', html)


class TestCvAdapterLanguages(TestCase):
    def test_format_base_cv_data_includes_languages(self):
        _make_summary()
        _make_experience()
        _make_language(name='Spanish', level=Language.LEVEL_NATIVE, display_order=0)
        _make_language(name='English', level=Language.LEVEL_B2, display_order=1)

        base_cv_data = cv_builder.build_cv_context()
        text = cv_adapter._format_base_cv_data(base_cv_data)

        self.assertIn('Languages:', text)
        self.assertIn('Spanish (Native)', text)
        self.assertIn('English (B2)', text)

    def test_format_base_cv_data_without_languages(self):
        _make_summary()
        _make_experience()

        base_cv_data = cv_builder.build_cv_context()
        text = cv_adapter._format_base_cv_data(base_cv_data)

        self.assertIn('No languages listed.', text)

    def test_build_system_prompt_includes_languages(self):
        _make_summary()
        _make_experience()
        _make_language(name='English', level=Language.LEVEL_B2, display_order=1)

        base_cv_data = cv_builder.build_cv_context()
        prompt = cv_adapter.build_system_prompt(base_cv_data)

        self.assertIn('Languages:', prompt)
        self.assertIn('English (B2)', prompt)
