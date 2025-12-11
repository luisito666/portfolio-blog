from .models import SocialSettings

def social_media(request):
    """
    Context processor to make social media settings available in all templates.
    """
    try:
        social_settings = SocialSettings.objects.first()
    except Exception:
        social_settings = None
        
    return {
        'social_settings': social_settings
    }