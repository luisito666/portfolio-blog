from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('experience/', views.ExperienceListView.as_view(), name='experience_list'),
]