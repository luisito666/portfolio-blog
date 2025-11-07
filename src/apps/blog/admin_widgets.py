from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.templatetags.static import static

class MarkdownTextArea(forms.Textarea):
    """Custom textarea widget with markdown formatting toolbar"""
    
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        attrs.update({
            'class': 'markdown-editor-textarea',
            'data-markdown-editor': 'true'
        })
        kwargs['attrs'] = attrs
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        """Custom render method to add markdown help text"""
        attrs = attrs or {}
        attrs.update(self.attrs)
        
        # Get the default textarea HTML
        html = super().render(name, value, attrs, renderer)
        
        # Add markdown help information
        help_text = """
        <div class="field-help">
            <strong>Markdown Help:</strong><br>
            <code>**bold**</code> • <code>*italic*</code> • <code># heading</code> • 
            <code>[link](url)</code> • <code>![image](url)</code> • 
            <code>`code`</code> • <code>> quote</code><br>
            <small>Use toolbar buttons or keyboard shortcuts (Ctrl+B for bold, etc.)</small>
        </div>
        """
        
        return mark_safe(html + help_text)

class MarkdownModelAdmin(admin.ModelAdmin):
    """Base admin class that includes markdown support"""
    
    def get_form(self, request, obj=None, **kwargs):
        """Custom form to add markdown widgets"""
        form = super().get_form(request, obj, **kwargs)
        
        # Add markdown widget to text fields
        if hasattr(form.base_fields, 'content'):
            form.base_fields['content'].widget = MarkdownTextArea(
                attrs={
                    'rows': 20,
                    'cols': 80,
                    'placeholder': 'Write your post content here using Markdown...'
                }
            )
        
        if hasattr(form.base_fields, 'excerpt'):
            form.base_fields['excerpt'].widget = MarkdownTextArea(
                attrs={
                    'rows': 5,
                    'cols': 80,
                    'placeholder': 'Optional excerpt/summary...'
                }
            )
        
        return form