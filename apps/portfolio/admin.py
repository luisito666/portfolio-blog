from django.contrib import admin
from .models import About, Skill, Project

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'profile_image')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency_level', 'created_at']
    list_filter = ['category', 'proficiency_level']
    search_fields = ['name', 'category']
    list_editable = ['proficiency_level']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'featured', 'created_at', 'updated_at']
    list_filter = ['featured', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'technologies']
    list_editable = ['featured']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'description', 'image', 'technologies')
        }),
        ('Links', {
            'fields': ('github_url', 'live_url'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('featured',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
