"""Views for the cv_assistant admin chat UI."""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from django.conf import settings


class AdminChatView(UserPassesTestMixin, TemplateView):
    """Admin-only chat UI for the AI CV Assistant."""

    template_name = "cv_assistant/chat.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ai_model"] = settings.AI_MODEL
        return context