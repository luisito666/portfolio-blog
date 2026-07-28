"""Tests for the cv_assistant service layer.

Task 4: build_cv_context / generate_cv_pdf
Task 5: ai_client.chat_completion
Task 6: cv_adapter prompt builder / parser
"""

import json
from datetime import date
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.portfolio.models import (
    Certification,
    Education,
    Experience,
    Skill,
    SocialSettings,
    Summary,
)
from apps.cv_assistant.services import ai_client, cv_adapter, cv_builder, pdf_generator


def _make_summary():
    return Summary.objects.create(title='Summary', content='** Experienced ** dev')


def _make_experience():
    return Experience.objects.create(
        company='Acme',
        position='Backend Dev',
        description='Did **backend** work',
        start_date=date(2022, 1, 1),
    )


def _make_skill():
    return Skill.objects.create(name='Python', category='Languages', years_of_experience=3)


def _make_certification():
    return Certification.objects.create(
        name='AWS Cert',
        issuing_organization='Amazon',
        issue_date=date(2023, 1, 1),
        description='**Cloud** cert',
    )


def _make_education():
    return Education.objects.create(
        institution='MIT',
        degree='BSc',
        field_of_study='CS',
        start_date=date(2018, 9, 1),
        end_date=date(2022, 6, 1),
        description='**Studied** CS',
    )


def _make_social_settings():
    return SocialSettings.objects.create(
        linkedin_url='https://linkedin.com/in/test',
    )


class TestBuildCvContext(TestCase):
    def setUp(self):
        _make_summary()
        self.exp = _make_experience()
        _make_certification()
        _make_education()
        _make_skill()
        _make_social_settings()

    def test_returns_dict_with_expected_keys(self):
        ctx = cv_builder.build_cv_context()
        for key in (
            'summary',
            'experiences',
            'certifications',
            'education_list',
            'skill_columns',
            'social_settings',
            'pdf_owner_name',
        ):
            self.assertIn(key, ctx)

    def test_summary_has_content_html(self):
        ctx = cv_builder.build_cv_context()
        self.assertTrue(hasattr(ctx['summary'], 'content_html'))
        self.assertIn('<strong>Experienced</strong>', ctx['summary'].content_html)

    def test_experiences_have_description_html(self):
        ctx = cv_builder.build_cv_context()
        exps = list(ctx['experiences'])
        self.assertEqual(len(exps), 1)
        self.assertTrue(hasattr(exps[0], 'description_html'))
        self.assertIn('<strong>backend</strong>', exps[0].description_html)

    def test_skill_columns_structure(self):
        ctx = cv_builder.build_cv_context()
        self.assertEqual(len(ctx['skill_columns']), 3)
        all_cats = [item for col in ctx['skill_columns'] for item in col]
        self.assertEqual(len(all_cats), 1)
        self.assertEqual(all_cats[0]['category'], 'Languages')

    def test_adapted_data_overrides_summary_and_experiences(self):
        adapted = {
            'summary': '**Tailored** summary',
            'experiences': [
                {
                    'id': self.exp.id,
                    'position': 'Senior Dev',
                    'company': 'Acme',
                    'description_adapted': '**Adapted** description',
                }
            ],
        }
        ctx = cv_builder.build_cv_context(adapted_data=adapted)
        self.assertIn('<strong>Tailored</strong>', ctx['summary'].content_html)
        exps = list(ctx['experiences'])
        self.assertEqual(exps[0].position, 'Senior Dev')
        self.assertIn('<strong>Adapted</strong>', exps[0].description_html)


class TestGenerateCvPdf(TestCase):
    def setUp(self):
        _make_summary()
        _make_experience()
        _make_skill()
        _make_social_settings()

    def test_returns_non_empty_bytes(self):
        ctx = cv_builder.build_cv_context()
        pdf_bytes = pdf_generator.generate_cv_pdf(ctx)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 0)
        # PDF magic bytes
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))


class TestAiClient(TestCase):
    def test_chat_completion_calls_create_and_returns_content(self):
        fake_message = MagicMock()
        fake_message.message.content = 'AI response text'
        fake_choice = MagicMock()
        fake_choice.message = fake_message.message
        # Simpler: choices[0].message.content
        fake_response = MagicMock()
        fake_response.choices = [fake_choice]
        # Make choices[0].message.content resolvable
        fake_response.choices[0].message.content = 'AI response text'

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = fake_response

        with patch('apps.cv_assistant.services.ai_client.get_ai_client', return_value=mock_client):
            result = ai_client.chat_completion(
                messages=[{'role': 'user', 'content': 'hi'}],
                model='custom-model',
                temperature=0.5,
                max_tokens=100,
            )

        self.assertEqual(result, 'AI response text')
        mock_client.chat.completions.create.assert_called_once()
        _, kwargs = mock_client.chat.completions.create.call_args
        self.assertEqual(kwargs['model'], 'custom-model')
        self.assertEqual(kwargs['messages'], [{'role': 'user', 'content': 'hi'}])
        self.assertEqual(kwargs['temperature'], 0.5)
        self.assertEqual(kwargs['max_tokens'], 100)


class TestCvAdapter(TestCase):
    def setUp(self):
        _make_summary()
        self.exp = _make_experience()
        _make_certification()
        _make_education()
        _make_skill()

    def test_build_system_prompt_includes_base_cv_data(self):
        ctx = cv_builder.build_cv_context()
        prompt = cv_adapter.build_system_prompt(ctx)
        self.assertIsInstance(prompt, str)
        # Should reference the summary content
        self.assertIn('Experienced', prompt)
        # Should mention an experience company / position
        self.assertIn('Acme', prompt)
        self.assertIn('Backend Dev', prompt)
        # Should mention a skill
        self.assertIn('Python', prompt)
        # Should include rule about JSON output structure
        self.assertIn('summary', prompt)
        self.assertIn('experiences', prompt)
        self.assertIn('description_adapted', prompt)

    def test_build_adaptation_prompt_includes_job_description(self):
        msg = cv_adapter.build_adaptation_prompt('We need a Django dev', user_instructions='Focus on API')
        self.assertIn('Django dev', msg)
        self.assertIn('Focus on API', msg)

    def test_build_adaptation_prompt_without_user_instructions(self):
        msg = cv_adapter.build_adaptation_prompt('React frontend role')
        self.assertIn('React frontend role', msg)

    def test_parse_ai_response_valid_json(self):
        payload = {
            'summary': 'Adapted summary',
            'experiences': [{'id': self.exp.id, 'description_adapted': 'Adapted desc'}],
        }
        result = cv_adapter.parse_ai_response(json.dumps(payload))
        self.assertEqual(result['summary'], 'Adapted summary')
        self.assertEqual(result['experiences'][0]['id'], self.exp.id)

    def test_parse_ai_response_handles_markdown_wrapped_json(self):
        payload = {
            'summary': 'Wrapped summary',
            'experiences': [{'id': self.exp.id, 'description_adapted': 'Wrapped desc'}],
        }
        wrapped = '```json\n' + json.dumps(payload) + '\n```'
        result = cv_adapter.parse_ai_response(wrapped)
        self.assertEqual(result['summary'], 'Wrapped summary')

    def test_parse_ai_response_rejects_unknown_ids(self):
        payload = {
            'summary': 'Bad',
            'experiences': [{'id': 99999, 'description_adapted': 'Nope'}],
        }
        with self.assertRaises(ValueError):
            cv_adapter.parse_ai_response(json.dumps(payload))