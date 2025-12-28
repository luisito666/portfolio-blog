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
    years_of_experience = models.IntegerField(default=1, help_text="Years of experience with this skill")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    class Meta:
        ordering = ['category', '-years_of_experience']
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

class SocialSettings(models.Model):
    """Model for storing social media links"""
    linkedin_url = models.URLField(blank=True, null=True, help_text="LinkedIn Profile URL")
    twitter_url = models.URLField(blank=True, null=True, help_text="Twitter Profile URL")
    facebook_url = models.URLField(blank=True, null=True, help_text="Facebook Profile URL")
    github_url = models.URLField(blank=True, null=True, help_text="GitHub Profile URL")
    
    def __str__(self):
        return "Social Media Settings"
    
    class Meta:
        verbose_name = "Social Settings"
        verbose_name_plural = "Social Settings"

class Experience(models.Model):
    """Model for storing work experience"""
    company = models.CharField(max_length=200, help_text="Company name")
    position = models.CharField(max_length=200, help_text="Job title/position")
    description = models.TextField(help_text="Job description and achievements in markdown format")
    location = models.CharField(max_length=200, blank=True, null=True, help_text="Job location (city, country)")
    start_date = models.DateField(help_text="Start date of employment")
    end_date = models.DateField(blank=True, null=True, help_text="End date (leave empty if current)")
    current = models.BooleanField(default=False, help_text="Currently working here")
    company_url = models.URLField(blank=True, null=True, help_text="Company website URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.position} at {self.company}"
    
    @property
    def duration(self):
        """Calculate duration of employment"""
        from datetime import date
        end = self.end_date if self.end_date else date.today()
        years = (end.year - self.start_date.year)
        months = (end.month - self.start_date.month)
        
        if months < 0:
            years -= 1
            months += 12
            
        if years > 0 and months > 0:
            return f"{years} year{'s' if years > 1 else ''}, {months} month{'s' if months > 1 else ''}"
        elif years > 0:
            return f"{years} year{'s' if years > 1 else ''}"
        else:
            return f"{months} month{'s' if months > 1 else ''}"
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Work Experience"
        verbose_name_plural = "Work Experiences"

class Summary(models.Model):
    """Model for storing professional summary/bio"""
    title = models.CharField(max_length=200, default="Professional Summary", help_text="Section title")
    content = models.TextField(help_text="Professional summary in markdown format")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Professional Summary"
        verbose_name_plural = "Professional Summary"

class Certification(models.Model):
    """Model for storing certifications and courses"""
    name = models.CharField(max_length=200, help_text="Certification or course name")
    issuing_organization = models.CharField(max_length=200, help_text="Organization that issued the certification")
    issue_date = models.DateField(help_text="Date when certification was issued")
    expiry_date = models.DateField(blank=True, null=True, help_text="Expiration date (leave empty if doesn't expire)")
    credential_id = models.CharField(max_length=200, blank=True, null=True, help_text="Credential ID or certificate number")
    credential_url = models.URLField(blank=True, null=True, help_text="URL to verify credential")
    description = models.TextField(blank=True, null=True, help_text="Brief description in markdown format")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"
    
    @property
    def is_expired(self):
        """Check if certification is expired"""
        from datetime import date
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False
    
    class Meta:
        ordering = ['-issue_date']
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"

class Education(models.Model):
    """Model for storing education history"""
    institution = models.CharField(max_length=200, help_text="Educational institution name")
    degree = models.CharField(max_length=200, help_text="Degree or diploma obtained")
    field_of_study = models.CharField(max_length=200, help_text="Major or field of study")
    start_date = models.DateField(help_text="Start date")
    end_date = models.DateField(blank=True, null=True, help_text="End date (leave empty if current)")
    current = models.BooleanField(default=False, help_text="Currently studying here")
    grade = models.CharField(max_length=100, blank=True, null=True, help_text="GPA or grade (e.g., '3.8/4.0', 'First Class')")
    description = models.TextField(blank=True, null=True, help_text="Additional details in markdown format")
    institution_url = models.URLField(blank=True, null=True, help_text="Institution website URL")
    location = models.CharField(max_length=200, blank=True, null=True, help_text="Institution location (city, country)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} - {self.institution}"
    
    @property
    def duration(self):
        """Calculate duration of education"""
        from datetime import date
        end = self.end_date if self.end_date else date.today()
        years = (end.year - self.start_date.year)
        
        if years > 0:
            return f"{years} year{'s' if years > 1 else ''}"
        else:
            months = (end.year - self.start_date.year) * 12 + (end.month - self.start_date.month)
            return f"{months} month{'s' if months > 1 else ''}"
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Education"
        verbose_name_plural = "Education"

class Lead(models.Model):
    """Model for storing leads who download the CV"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    class Meta:
        ordering = ['-downloaded_at']
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
