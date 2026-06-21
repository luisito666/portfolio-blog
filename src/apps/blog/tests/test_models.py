"""Tests for BlogPost model."""
from django.test import TestCase
from django.utils import timezone

from apps.blog.models import BlogPost


class TestBlogPostModel(TestCase):

    def test_str_returns_title(self):
        post = BlogPost(title='My Post', slug='my-post', content='test')
        self.assertEqual(str(post), 'My Post')

    def test_slug_auto_generated_from_title(self):
        post = BlogPost.objects.create(title='Hello World', content='test')
        self.assertEqual(post.slug, 'hello-world')

    def test_slug_spaces_become_dashes(self):
        post = BlogPost.objects.create(title='One Two Three', content='test')
        self.assertEqual(post.slug, 'one-two-three')

    def test_slug_commas_removed(self):
        post = BlogPost.objects.create(title='Hello, World', content='test')
        self.assertEqual(post.slug, 'hello-world')

    def test_slug_not_overwritten_if_provided(self):
        post = BlogPost.objects.create(title='Hello World', slug='custom-slug', content='test')
        self.assertEqual(post.slug, 'custom-slug')

    def test_published_at_set_when_published(self):
        post = BlogPost.objects.create(title='Published Post', content='test', published=True)
        self.assertIsNotNone(post.published_at)

    def test_published_at_not_changed_on_subsequent_save(self):
        post = BlogPost.objects.create(title='Published Post', content='test', published=True)
        original_published_at = post.published_at
        post.title = 'Updated Title'
        post.save()
        post.refresh_from_db()
        self.assertEqual(post.published_at, original_published_at)

    def test_published_at_not_set_when_not_published(self):
        post = BlogPost.objects.create(title='Draft Post', content='test', published=False)
        self.assertIsNone(post.published_at)

    def test_default_published_is_false(self):
        post = BlogPost.objects.create(title='Test Post', content='test')
        self.assertFalse(post.published)

    def test_excerpt_is_optional(self):
        post = BlogPost.objects.create(title='Test Post', content='test')
        self.assertEqual(post.excerpt, '')

    def test_featured_image_is_optional(self):
        post = BlogPost.objects.create(title='Test Post', content='test')
        self.assertFalse(post.featured_image)

    def test_ordering_published_before_drafts(self):
        draft = BlogPost.objects.create(title='Draft', content='test', published=False)
        published = BlogPost.objects.create(title='Published', content='test', published=True)
        posts = list(BlogPost.objects.all())
        # published_at is set for published post; None for draft
        # ordering [-published_at, -created_at]: NULL (draft) sorts last in DESC
        self.assertEqual(posts[0], published)
        self.assertEqual(posts[1], draft)
