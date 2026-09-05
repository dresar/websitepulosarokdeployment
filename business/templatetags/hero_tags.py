from django import template
from core.models import HeroImage

register = template.Library()

@register.simple_tag
def get_hero_image(page='business'):
    """
    Get hero image for any page
    """
    try:
        hero_image = HeroImage.objects.filter(page=page, is_active=True).first()
        if hero_image:
            return hero_image
    except:
        pass
    return None

@register.simple_tag
def get_hero_image_url(page='business'):
    """
    Get hero image URL for any page
    """
    try:
        hero_image = HeroImage.objects.filter(page=page, is_active=True).first()
        if hero_image:
            return hero_image.image.url
    except:
        pass
    return None
