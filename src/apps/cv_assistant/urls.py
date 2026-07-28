"""URL routing for the cv_assistant admin UI (non-API)."""
from django.urls import path

from .views import AdminChatView

app_name = "cv_assistant"

urlpatterns = [
    path("assistant/", AdminChatView.as_view(), name="chat"),
]