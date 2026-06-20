"""Tests for the blog DRF API."""
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.blog.models import BlogPost


class BlogAPIAuthTests(APITestCase):
    """JWT authentication and permission tests."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='tester', password='StrongP@ss123', email='t@example.com'
        )
        self.login_url = reverse('blog_api:token_obtain_pair')

    def test_login_returns_access_and_refresh(self):
        resp = self.client.post(self.login_url, {
            'username': 'tester', 'password': 'StrongP@ss123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_login_with_bad_password_rejected(self):
        resp = self.client.post(self.login_url, {
            'username': 'tester', 'password': 'wrong'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_create_post(self):
        url = reverse('blog_api:post-list')
        resp = self.client.post(url, {'title': 'x', 'content': 'y'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class BlogAPIPostTests(APITestCase):
    """CRUD tests for blog posts via API."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='tester', password='StrongP@ss123', email='t@example.com'
        )
        login = self.client.post(reverse('blog_api:token_obtain_pair'), {
            'username': 'tester', 'password': 'StrongP@ss123'
        }, format='json')
        self.access = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        self.posts_url = reverse('blog_api:post-list')

    def test_create_post_authenticated(self):
        payload = {
            'title': 'Hello API',
            'content': '# heading\n\n body',
            'excerpt': 'short',
            'published': True,
        }
        resp = self.client.post(self.posts_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(BlogPost.objects.count(), 1)
        post = BlogPost.objects.first()
        self.assertEqual(post.title, 'Hello API')
        self.assertTrue(post.slug)

    def test_list_published_visible_anonymous(self):
        BlogPost.objects.create(title='pub', content='c', published=True)
        BlogPost.objects.create(title='draft', content='c', published=False)
        self.client.credentials()
        resp = self.client.get(self.posts_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in resp.data['results']]
        self.assertIn('pub', titles)
        self.assertNotIn('draft', titles)

    def test_update_post_authenticated(self):
        post = BlogPost.objects.create(title='orig', content='c', published=False)
        url = reverse('blog_api:post-detail', kwargs={'slug': post.slug})
        resp = self.client.patch(url, {'title': 'updated'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        post.refresh_from_db()
        self.assertEqual(post.title, 'updated')

    def test_delete_post_authenticated(self):
        post = BlogPost.objects.create(title='doomed', content='c', published=False)
        url = reverse('blog_api:post-detail', kwargs={'slug': post.slug})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(slug=post.slug).exists())

    def test_published_endpoint(self):
        BlogPost.objects.create(title='p1', content='c', published=True)
        BlogPost.objects.create(title='d1', content='c', published=False)
        url = reverse('blog_api:post-published')
        self.client.credentials()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in resp.data['results']]
        self.assertIn('p1', titles)
        self.assertNotIn('d1', titles)
