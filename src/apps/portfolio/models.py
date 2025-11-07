from django.db import models

class About(models.Model):
    """Model for storing personal information in the about section"""
    title = models.CharField(max_length=100, default="About Me")
    content = models.TextField(help_text="Write your personal description in markdown format")
    profile_image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "About Section"
        verbose_name_plural = "About Sections"

class Skill(models.Model):
    """Model for storing skills"""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, help_text="e.g., Programming Languages, Frameworks, Tools")
    proficiency_level = models.IntegerField(default=50, help_text="Proficiency level from 0 to 100")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    class Meta:
        ordering = ['category', '-proficiency_level']
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

class Project(models.Model):
    """Model for storing portfolio projects"""
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Project description in markdown format")
    image = models.ImageField(upload_to='portfolio/projects/', blank=True, null=True)
    github_url = models.URLField(blank=True, null=True, help_text="GitHub repository URL")
    live_url = models.URLField(blank=True, null=True, help_text="Live project URL")
    technologies = models.CharField(max_length=500, help_text="Technologies used, separated by commas")
    featured = models.BooleanField(default=False, help_text="Mark as featured project")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-featured', '-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"
