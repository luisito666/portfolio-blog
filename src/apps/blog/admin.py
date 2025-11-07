from django.contrib import admin
from django import forms
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    """Custom form with markdown support"""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 20,
            'cols': 80,
            'placeholder': 'Write your post content here using Markdown...',
            'class': 'markdown-editor-textarea'
        }),
        help_text="Use the markdown toolbar above or keyboard shortcuts (Ctrl+B for bold, etc.)"
    )
    
    excerpt = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'cols': 80,
            'placeholder': 'Optional excerpt/summary...'
        }),
        help_text="Short summary of the post (optional)",
        required=False
    )
    
    class Meta:
        model = BlogPost
        fields = '__all__'

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostForm
    list_display = ['title', 'published', 'published_at', 'created_at']
    list_filter = ['published', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'excerpt']
    list_editable = ['published']
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    
    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        ('Publishing', {
            'fields': ('published', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Auto-generate slug if empty
        if not obj.slug and obj.title:
            obj.slug = obj.title.lower().replace(' ', '-').replace(',', '').replace("'", '')
        super().save_model(request, obj, form, change)
        
    class Media:
        css = {
            'all': ('admin/css/markdown_editor.css',)
        }
        js = ('admin/js/markdown_editor.js',)
