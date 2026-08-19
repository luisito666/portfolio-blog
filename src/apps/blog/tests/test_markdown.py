"""Tests for the shared render_markdown helper."""
from django.test import SimpleTestCase

from core.markdown import render_markdown


class TestRenderMarkdown(SimpleTestCase):

    def test_basic_bold_renders(self):
        html = render_markdown('**bold text**')
        self.assertIn('<strong>bold text</strong>', html)

    def test_labeled_python_block_gets_highlighting_and_linenos(self):
        text = '```python\nclass Foo:\n    pass\n```'
        html = render_markdown(text)
        self.assertIn('codehilite', html)
        self.assertIn('<span', html)
        self.assertIn('linenodiv', html)
        self.assertIn('codehilitetable', html)

    def test_unlabeled_block_has_no_linenos(self):
        text = '```\nplain diagram\n```'
        html = render_markdown(text)
        self.assertNotIn('linenodiv', html)
        self.assertNotIn('codehilitetable', html)
        self.assertIn('<code>plain diagram', html)

    def test_unlabeled_multiline_diagram_content_preserved(self):
        text = '```\n+----------+\n|  Client  |\n+----------+\n      |\n  Internet\n      |\n+----------+\n|  Server  |\n+----------+\n```'
        html = render_markdown(text)
        self.assertIn('Internet', html)
        self.assertNotIn('linenodiv', html)

    def test_crlf_labeled_block_still_gets_linenos(self):
        text = '```python\r\nclass Foo:\r\n    pass\r\n```'
        html = render_markdown(text)
        self.assertIn('linenodiv', html)
        self.assertIn('Foo', html)

    def test_none_input_returns_empty_string(self):
        self.assertEqual(render_markdown(None), '')

    def test_tables_extension_works(self):
        text = '| A | B |\n| --- | --- |\n| 1 | 2 |'
        html = render_markdown(text)
        self.assertIn('<table>', html)

    def test_mixed_doc_python_numbered_diagram_plain(self):
        text = (
            '```python\n'
            'class Foo:\n'
            '    pass\n'
            '```\n\n'
            '```\n'
            'plain diagram\n'
            '```\n'
        )
        html = render_markdown(text)
        self.assertEqual(html.count('linenodiv'), 1)
