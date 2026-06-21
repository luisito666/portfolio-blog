"""Tests for blog HTML views."""
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import BlogPost


class TestPostListView(TestCase):

    def test_get_returns_200(self):
        resp = self.client.get(reverse('blog:post_list'))
        self.assertEqual(resp.status_code, 200)

    def test_uses_correct_template(self):
        resp = self.client.get(reverse('blog:post_list'))
        self.assertTemplateUsed(resp, 'blog/post_list.html')

    def test_context_has_posts_key(self):
        resp = self.client.get(reverse('blog:post_list'))
        self.assertIn('posts', resp.context)

    def test_only_published_posts_in_list(self):
        BlogPost.objects.create(title='Published', content='test', published=True)
        BlogPost.objects.create(title='Draft', content='test', published=False)
        resp = self.client.get(reverse('blog:post_list'))
        titles = [p.title for p in resp.context['posts']]
        self.assertIn('Published', titles)
        self.assertNotIn('Draft', titles)

    def test_drafts_not_in_list(self):
        BlogPost.objects.create(title='Draft', content='test', published=False)
        resp = self.client.get(reverse('blog:post_list'))
        self.assertEqual(len(resp.context['posts']), 0)

    def test_title_in_context_is_blog(self):
        resp = self.client.get(reverse('blog:post_list'))
        self.assertEqual(resp.context['title'], 'Blog')

    def test_pagination_page_2_has_two_posts(self):
        for i in range(12):
            BlogPost.objects.create(title=f'Post {i}', content='test', published=True)
        resp = self.client.get(reverse('blog:post_list') + '?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['posts']), 2)

    def test_empty_list_returns_200(self):
        resp = self.client.get(reverse('blog:post_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['posts']), 0)

    def test_url_name_post_list_reverses(self):
        url = reverse('blog:post_list')
        self.assertEqual(url, '/blog/')


class TestPostDetailView(TestCase):

    def setUp(self):
        self.published = BlogPost.objects.create(
            title='Published Post',
            content='**bold** content',
            published=True,
        )
        self.draft = BlogPost.objects.create(
            title='Draft Post',
            content='draft content',
            published=False,
        )

    def test_get_published_post_returns_200(self):
        url = reverse('blog:post_detail', kwargs={'slug': self.published.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_uses_correct_template(self):
        url = reverse('blog:post_detail', kwargs={'slug': self.published.slug})
        resp = self.client.get(url)
        self.assertTemplateUsed(resp, 'blog/post_detail.html')

    def test_context_has_post_instance(self):
        url = reverse('blog:post_detail', kwargs={'slug': self.published.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.context['post'], self.published)

    def test_context_has_post_html(self):
        url = reverse('blog:post_detail', kwargs={'slug': self.published.slug})
        resp = self.client.get(url)
        self.assertIn('post_html', resp.context)

    def test_markdown_bold_renders_as_strong(self):
        url = reverse('blog:post_detail', kwargs={'slug': self.published.slug})
        resp = self.client.get(url)
        self.assertIn('<strong>bold</strong>', resp.context['post_html'])

    def test_draft_returns_404(self):
        url = reverse('blog:post_detail', kwargs={'slug': self.draft.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_nonexistent_slug_returns_404(self):
        resp = self.client.get(reverse('blog:post_detail', kwargs={'slug': 'does-not-exist'}))
        self.assertEqual(resp.status_code, 404)

    def test_url_name_post_detail_reverses(self):
        url = reverse('blog:post_detail', kwargs={'slug': self.published.slug})
        self.assertIn('/blog/post/', url)
