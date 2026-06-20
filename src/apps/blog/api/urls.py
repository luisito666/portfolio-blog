"""URL routing for the blog API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import BlogPostViewSet

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet, basename='post')

app_name = 'blog_api'

urlpatterns = [
    # JWT auth
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Blog post CRUD
    path('', include(router.urls)),
]
