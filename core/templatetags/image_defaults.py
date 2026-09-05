from django import template
from django.conf import settings
from django.templatetags.static import static
import os

register = template.Library()

@register.filter
def default_image(image_field, default_type='placeholder'):
    """
    Returns the image URL or a default image if the field is empty
    
    Usage in templates:
    {{ news.featured_image|default_image:'news-featured' }}
    {{ location.main_image|default_image:'tourism-location' }}
    {{ village.header_image|default_image:'village-header' }}
    """
    if image_field and hasattr(image_field, 'url'):
        try:
            # Check if file exists
            if image_field.name and os.path.exists(image_field.path):
                return image_field.url
        except (ValueError, AttributeError):
            pass
    
    # Return default image based on type
    default_images = {
        'placeholder': 'images/defaults/placeholder.svg',
        'avatar': 'images/defaults/avatar-placeholder.svg',
        'document': 'images/defaults/document-placeholder.svg',
        'website-logo': 'images/defaults/website-logo.svg',
        'favicon': 'images/defaults/favicon.svg',
        'background': 'images/defaults/background.svg',
        'tourism-category': 'images/defaults/tourism-category.svg',
        'tourism-location': 'images/defaults/tourism-location.svg',
        'tourism-gallery': 'images/defaults/tourism-gallery.svg',
        'tourism-package': 'images/defaults/tourism-package.svg',
        'news-featured': 'images/defaults/news-featured.svg',
        'news-gallery': 'images/defaults/news-gallery.svg',
        'village-header': 'images/defaults/village-header.svg',
        'village-history': 'images/defaults/village-history.svg',
        'village-photo': 'images/defaults/village-photo.svg',
        'village-official': 'images/defaults/village-official.svg',
        'village-facility': 'images/defaults/village-facility.svg',
        'village-map': 'images/defaults/village-map.svg',
    }
    
    default_path = default_images.get(default_type, default_images['placeholder'])
    return static(default_path)

@register.simple_tag
def get_default_image(image_type):
    """
    Get default image URL by type
    
    Usage in templates:
    {% get_default_image 'news-featured' %}
    """
    default_images = {
        'placeholder': 'images/defaults/placeholder.svg',
        'avatar': 'images/defaults/avatar-placeholder.svg',
        'document': 'images/defaults/document-placeholder.svg',
        'website-logo': 'images/defaults/website-logo.svg',
        'favicon': 'images/defaults/favicon.svg',
        'background': 'images/defaults/background.svg',
        'tourism-category': 'images/defaults/tourism-category.svg',
        'tourism-location': 'images/defaults/tourism-location.svg',
        'tourism-gallery': 'images/defaults/tourism-gallery.svg',
        'tourism-package': 'images/defaults/tourism-package.svg',
        'news-featured': 'images/defaults/news-featured.svg',
        'news-gallery': 'images/defaults/news-gallery.svg',
        'village-header': 'images/defaults/village-header.svg',
        'village-history': 'images/defaults/village-history.svg',
        'village-photo': 'images/defaults/village-photo.svg',
        'village-official': 'images/defaults/village-official.svg',
        'village-facility': 'images/defaults/village-facility.svg',
        'village-map': 'images/defaults/village-map.svg',
    }
    
    default_path = default_images.get(image_type, default_images['placeholder'])
    return static(default_path)

@register.inclusion_tag('core/image_with_fallback.html')
def image_with_fallback(image_field, default_type='placeholder', css_class='', alt_text=''):
    """
    Renders an image with fallback to default
    
    Usage in templates:
    {% image_with_fallback news.featured_image 'news-featured' 'w-full h-48 object-cover' news.title %}
    """
    if image_field and hasattr(image_field, 'url'):
        try:
            if image_field.name and os.path.exists(image_field.path):
                image_url = image_field.url
            else:
                image_url = get_default_image(default_type)
        except (ValueError, AttributeError):
            image_url = get_default_image(default_type)
    else:
        image_url = get_default_image(default_type)
    
    return {
        'image_url': image_url,
        'css_class': css_class,
        'alt_text': alt_text or 'Image',
        'default_type': default_type
    }