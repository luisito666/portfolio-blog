from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('experience/', views.ExperienceListView.as_view(), name='experience_list'),
    path('download-cv/', views.DownloadCVView.as_view(), name='download_cv'),
    path('generate-pdf/', views.GeneratePDFView.as_view(), name='generate_pdf'),
]