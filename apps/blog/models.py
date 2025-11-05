from django.db import models
from django.utils import timezone

class BlogPost(models.Model):
    """Model for storing blog posts with markdown support"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the title")
    content = models.TextField(help_text="Blog post content in markdown format")
    excerpt = models.TextField(blank=True, help_text="Short summary of the post (optional)")
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    published = models.BooleanField(default=False, help_text="Mark as published")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True, help_text="Date when post was published")
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug and self.title:
            self.slug = self.title.lower().replace(' ', '-').replace(',', '')
        
        # Set published_at when post is first published
        if self.published and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
