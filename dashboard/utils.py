from .models import SocialMediaPlatform

def get_social_media_platform(platform_name):
    try:
        return SocialMediaPlatform.objects.get(name=platform_name)
    except SocialMediaPlatform.DoesNotExist:
        raise ValueError(f"Platform {platform_name} does not exist")
