"""Tests for BlogPostAdmin."""
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from apps.blog.admin import BlogPostAdmin, BlogPostForm
from apps.blog.models import BlogPost


class TestBlogPostAdmin(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.blog_admin = BlogPostAdmin(BlogPost, self.site)
        self.factory = RequestFactory()
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username='admin', password='admin123', email='admin@example.com'
        )

    def test_blogpost_is_registered(self):
        self.assertIn(BlogPost, admin.site._registry)

    def test_registered_admin_is_blogpostadmin(self):
        self.assertIsInstance(admin.site._registry[BlogPost], BlogPostAdmin)

    def test_list_display_fields(self):
        for field in ('title', 'published', 'published_at', 'created_at'):
            self.assertIn(field, self.blog_admin.list_display)

    def test_list_filter_fields(self):
        for field in ('published', 'created_at', 'published_at'):
            self.assertIn(field, self.blog_admin.list_filter)

    def test_search_fields(self):
        for field in ('title', 'content', 'excerpt'):
            self.assertIn(field, self.blog_admin.search_fields)

    def test_list_editable_includes_published(self):
        self.assertIn('published', self.blog_admin.list_editable)

    def test_readonly_fields(self):
        for field in ('created_at', 'updated_at', 'published_at'):
            self.assertIn(field, self.blog_admin.readonly_fields)

    def test_form_is_blogpostform(self):
        self.assertIs(self.blog_admin.form, BlogPostForm)

    def test_save_model_autogenerates_slug(self):
        request = self.factory.post('/')
        request.user = self.superuser
        post = BlogPost(title='Hello World', content='test')
        form = BlogPostForm(instance=post)
        self.blog_admin.save_model(request, post, form, change=False)
        self.assertEqual(post.slug, 'hello-world')

    def test_save_model_strips_single_quotes_from_slug(self):
        request = self.factory.post('/')
        request.user = self.superuser
        post = BlogPost(title="It's a Test", content='test')
        form = BlogPostForm(instance=post)
        self.blog_admin.save_model(request, post, form, change=False)
        self.assertEqual(post.slug, 'its-a-test')

    def test_save_model_does_not_overwrite_existing_slug(self):
        request = self.factory.post('/')
        request.user = self.superuser
        post = BlogPost(title='Hello World', slug='my-custom-slug', content='test')
        form = BlogPostForm(instance=post)
        self.blog_admin.save_model(request, post, form, change=False)
        self.assertEqual(post.slug, 'my-custom-slug')

    def test_blogpostform_content_widget_has_markdown_class(self):
        form = BlogPostForm()
        widget = form.fields['content'].widget
        self.assertIn('markdown-editor-textarea', widget.attrs.get('class', ''))
