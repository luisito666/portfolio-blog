from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.core.signing import TimestampSigner
from weasyprint import HTML
from .models import About, Skill, Project, Experience, Summary, Certification, Education, Lead, SocialSettings
from django.conf import settings
import markdown
import json
import requests
import secrets

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
        project = get_object_or_404(Project, pk=pk)
        # Convert markdown description to HTML
        context['project_description_html'] = markdown.markdown(project.description, extensions=['extra', 'codehilite'])
        context['project'] = project
        return context

class ExperienceListView(TemplateView):
    """Work experience list view"""
    template_name = 'portfolio/experience_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get professional summary
        summary = Summary.objects.first()
        if summary:
            # Convert markdown content to HTML
            context['summary_html'] = markdown.markdown(summary.content, extensions=['extra', 'codehilite'])
        context['summary'] = summary
        
        # Get all experiences ordered by start date (most recent first)
        experiences = Experience.objects.all()
        for experience in experiences:
            # Convert markdown description to HTML
            experience.description_html = markdown.markdown(experience.description, extensions=['extra', 'codehilite'])
        context['experiences'] = experiences
        
        # Get all certifications ordered by issue date (most recent first)
        certifications = Certification.objects.all()
        for certification in certifications:
            if certification.description:
                # Convert markdown description to HTML
                certification.description_html = markdown.markdown(certification.description, extensions=['extra', 'codehilite'])
        context['certifications'] = certifications
        
        # Get all education entries ordered by start date (most recent first)
        education_list = Education.objects.all()
        for education in education_list:
            if education.description:
                # Convert markdown description to HTML
                education.description_html = markdown.markdown(education.description, extensions=['extra', 'codehilite'])
        context['education_list'] = education_list
        
        context['recaptcha_public_key'] = settings.RECAPTCHA_PUBLIC_KEY
        
        return context

class DownloadCVView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            
            captcha = data.get('captcha')
            
            if not name or not email:
                return JsonResponse({'error': 'Name and email are required'}, status=400)
            
            # Verify reCAPTCHA
            recaptcha_response = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': settings.RECAPTCHA_PRIVATE_KEY,
                    'response': captcha
                }
            )
            result = recaptcha_response.json()
            
            if not result.get('success'):
                return JsonResponse({'error': 'Invalid reCAPTCHA. Please try again.'}, status=400)
            
            Lead.objects.create(name=name, email=email)
            
            # Generate a signed token for PDF download (valid for 10 minutes)
            signer = TimestampSigner()
            token = signer.sign(secrets.token_hex(16))
            
            return JsonResponse({'success': True, 'message': 'Lead captured successfully', 'token': token})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class GeneratePDFView(View):
    def get(self, request, *args, **kwargs):
        # Get token from query parameters
        token = request.GET.get('token')
        
        if not token:
            return HttpResponse('Access denied. Please complete the captcha first.', status=403)
        
        # Validate the token (must be signed within the last 10 minutes)
        signer = TimestampSigner()
        try:
            # Unsing will raise BadSignature if token is invalid
            # max_age=600 seconds = 10 minutes
            original = signer.unsign(token, max_age=600)
        except Exception:
            return HttpResponse('Invalid or expired token. Please complete the captcha again.', status=403)
        
        summary = Summary.objects.first()
        if summary:
            summary.content_html = markdown.markdown(summary.content)

        experiences = Experience.objects.all()
        for exp in experiences:
            exp.description_html = markdown.markdown(exp.description)

        certifications = Certification.objects.all()
        for cert in certifications:
            if cert.description:
                cert.description_html = markdown.markdown(cert.description)

        education_list = Education.objects.all()
        for edu in education_list:
            if edu.description:
                edu.description_html = markdown.markdown(edu.description)

        skills = Skill.objects.all()
        
        # Group skills by category
        skills_by_category = {}
        for skill in skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)
            
        # Split categories into 3 columns
        categories = list(skills_by_category.items())
        skill_columns = [[], [], []]
        for i, (cat, cat_skills) in enumerate(categories):
            skill_columns[i % 3].append({'category': cat, 'skills': cat_skills})

        social_settings = SocialSettings.objects.first()
        
        context = {
            'summary': summary,
            'experiences': experiences,
            'certifications': certifications,
            'education_list': education_list,
            'skill_columns': skill_columns,
            'social_settings': social_settings,
            'user': request.user,
            'pdf_owner_name': settings.PDF_OWNER_NAME
        }
        
        template_path = 'portfolio/cv_pdf.html'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="cv.pdf"'

        template = get_template(template_path)
        html = template.render(context)

        # Generate PDF using WeasyPrint (faster and more reliable than xhtml2pdf)
        HTML(string=html).write_pdf(response)

        return response
