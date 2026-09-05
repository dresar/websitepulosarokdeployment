import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def youtube_embed(value):
    """
    Convert YouTube URL to embed iframe
    """
    if not value:
        return value
    
    # YouTube URL patterns
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
    ]
    
    # Check if it's already an iframe
    if '<iframe' in str(value):
        return value
    
    # Try to extract video ID from various YouTube URL formats
    video_id = None
    for pattern in youtube_patterns:
        match = re.search(pattern, str(value))
        if match:
            video_id = match.group(1)
            break
    
    if video_id:
        embed_html = f'''
        <div class="youtube-video">
            <iframe 
                src="https://www.youtube.com/embed/{video_id}" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
        </div>
        '''
        return mark_safe(embed_html)
    
    return value

@register.filter
def youtube_thumbnail(value):
    """
    Get YouTube thumbnail URL
    """
    if not value:
        return value
    
    # YouTube URL patterns
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
    ]
    
    # Try to extract video ID
    video_id = None
    for pattern in youtube_patterns:
        match = re.search(pattern, str(value))
        if match:
            video_id = match.group(1)
            break
    
    if video_id:
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    
    return value
