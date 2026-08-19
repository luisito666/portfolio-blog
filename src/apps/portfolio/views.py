from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.core.signing import TimestampSigner
from weasyprint import HTML
from .models import About, Skill, Project, Experience, Summary, Certification, Education, Lead, SocialSettings
from apps.cv_assistant.services.cv_builder import build_cv_context
from apps.cv_assistant.services.pdf_generator import generate_cv_pdf
from django.conf import settings
from core.markdown import render_markdown
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
            context['about_html'] = render_markdown(about.content)
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
            project.description_html = render_markdown(project.description)
        context['projects'] = projects
        
        return context

class ProjectDetailView(TemplateView):
    """Individual project detail view"""
    template_name = 'portfolio/project_detail.html'
    
    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=pk)
        # Convert markdown description to HTML
        context['project_description_html'] = render_markdown(project.description)
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
            context['summary_html'] = render_markdown(summary.content)
        context['summary'] = summary
        
        # Get all experiences ordered by start date (most recent first)
        experiences = Experience.objects.all()
        for experience in experiences:
            # Convert markdown description to HTML
            experience.description_html = render_markdown(experience.description)
        context['experiences'] = experiences
        
        # Get all certifications ordered by issue date (most recent first)
        certifications = Certification.objects.all()
        for certification in certifications:
            if certification.description:
                # Convert markdown description to HTML
                certification.description_html = render_markdown(certification.description)
        context['certifications'] = certifications
        
        # Get all education entries ordered by start date (most recent first)
        education_list = Education.objects.all()
        for education in education_list:
            if education.description:
                # Convert markdown description to HTML
                education.description_html = render_markdown(education.description)
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
            try:
                recaptcha_response = requests.post(
                    'https://www.google.com/recaptcha/api/siteverify',
                    data={
                        'secret': settings.RECAPTCHA_PRIVATE_KEY,
                        'response': captcha
                    },
                    timeout=10
                )
                result = recaptcha_response.json()
            except requests.exceptions.RequestException:
                return JsonResponse({'error': 'Could not verify captcha. Please try again.'}, status=503)
            
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
        
        # Build the CV context using the reusable service (mirrors the
        # previous inline portfolio-model extraction). ``user`` is preserved
        # for parity with the previous inline implementation.
        context = build_cv_context()
        context['user'] = request.user

        # Generate PDF using the reusable WeasyPrint service.
        try:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="cv.pdf"'
            pdf_bytes = generate_cv_pdf(context)
            response.write(pdf_bytes)
        except Exception:
            return HttpResponse(
                'We had some errors generating your PDF. Please try again later.',
                status=500,
            )

        return response
