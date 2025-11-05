from django.shortcuts import render
from django.views.generic import TemplateView
from .models import About, Skill, Project

class HomeView(TemplateView):
    """Main portfolio homepage view"""
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get about section (most recent one)
        context['about'] = About.objects.first()
        
        # Get skills grouped by category
        skills_by_category = {}
        skills = Skill.objects.all()
        for skill in skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)
        context['skills_by_category'] = skills_by_category
        
        # Get projects (featured first)
        context['projects'] = Project.objects.all()
        
        return context

class ProjectDetailView(TemplateView):
    """Individual project detail view"""
    template_name = 'portfolio/project_detail.html'
    
    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=pk)
        return context
