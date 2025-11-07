from django.shortcuts import render
from django.views.generic import TemplateView
from .models import About, Skill, Project
import markdown

class HomeView(TemplateView):
    """Main portfolio homepage view"""
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get about section (most recent one)
        about = About.objects.first()
        if about:
            # Convert markdown content to HTML for about section
            context['about_html'] = markdown.markdown(about.content, extensions=['extra', 'codehilite'])
        context['about'] = about
        
        # Get skills grouped by category
        skills_by_category = {}
        skills = Skill.objects.all()
        for skill in skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)
        context['skills_by_category'] = skills_by_category
        
        # Get projects (featured first) and process markdown
        projects = Project.objects.all()
        for project in projects:
            # Convert markdown description to HTML for project cards
            project.description_html = markdown.markdown(project.description, extensions=['extra', 'codehilite'])
        context['projects'] = projects
        
        return context

class ProjectDetailView(TemplateView):
    """Individual project detail view"""
    template_name = 'portfolio/project_detail.html'
    
    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        project = Project.objects.get(pk=pk)
        # Convert markdown description to HTML
        context['project_description_html'] = markdown.markdown(project.description, extensions=['extra', 'codehilite'])
        context['project'] = project
        return context
