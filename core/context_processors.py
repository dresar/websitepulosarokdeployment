"""
Context processors for core app
"""

def website_settings(request):
    """
    Add website settings to template context
    """
    try:
        from .models import WebsiteSettings, HeroImage
        settings = WebsiteSettings.get_settings()
        
        # Get current page hero image
        current_page = request.resolver_match.url_name if request.resolver_match else 'home'
        hero_image = None
        try:
            # Map URL names to page choices
            page_mapping = {
                'home': 'home',
                'profile': 'profile', 
                'events': 'events',
                'news': 'news',
                'tourism': 'tourism',
                'umkm': 'umkm',
                'organization': 'organization',
                'correspondence': 'correspondence',
                'gallery': 'gallery',
                'complaints': 'complaints',
                'layanan': 'layanan',
                'posyandu': 'posyandu',
                'bantuna': 'bantuna',
            }
            
            page_key = page_mapping.get(current_page, 'home')
            hero_image = HeroImage.objects.filter(page=page_key, is_active=True, image__isnull=False).exclude(image='').first()
        except Exception as e:
            pass
        
        try:
            hero_image_url = hero_image.image.url if hero_image and hero_image.image else None
            hero_title = hero_image.name if hero_image else None
            hero_subtitle = f"Website Desa Pulosarok - {hero_image.get_page_display()}" if hero_image else None
        except Exception as e:
            hero_image_url = None
            hero_title = None
            hero_subtitle = None
        
        return {
            'website_settings': settings,
            'site_name': settings.site_name,
            'site_tagline': getattr(settings, 'site_tagline', 'Desa Digital Terdepan'),
            'site_description': settings.site_description,
            'site_keywords': getattr(settings, 'site_keywords', settings.meta_keywords),
            'logo': getattr(settings, 'logo', settings.site_logo),
            'favicon': getattr(settings, 'favicon', settings.site_favicon),
            'hero_image': hero_image,
            'hero_image_url': hero_image_url,
            'hero_title': hero_title,
            'hero_subtitle': hero_subtitle,
            'contact_email': settings.contact_email,
            'contact_phone': settings.contact_phone,
            'contact_whatsapp': getattr(settings, 'contact_whatsapp', None),
            'contact_address': settings.contact_address,
            'facebook_url': settings.facebook_url,
            'instagram_url': settings.instagram_url,
            'twitter_url': settings.twitter_url,
            'youtube_url': settings.youtube_url,
            'google_analytics_id': settings.google_analytics_id,
            'google_tag_manager_id': getattr(settings, 'google_tag_manager_id', None),
            'facebook_pixel_id': getattr(settings, 'facebook_pixel_id', None),
            'enable_maintenance_mode': getattr(settings, 'enable_maintenance_mode', settings.maintenance_mode),
            'maintenance_message': settings.maintenance_message,
            'enable_cache': getattr(settings, 'enable_cache', True),
            'cache_duration': getattr(settings, 'cache_duration', 300),
        }
    except Exception as e:
        # Return default values if settings not available
        return {
            'website_settings': None,
            'site_name': 'Website Desa',
            'site_tagline': 'Desa Digital Terdepan',
            'site_description': 'Website resmi desa',
            'site_keywords': 'desa, website desa',
            'logo': None,
            'favicon': None,
            'hero_image': None,
            'contact_email': None,
            'contact_phone': None,
            'contact_whatsapp': None,
            'contact_address': None,
            'facebook_url': None,
            'instagram_url': None,
            'twitter_url': None,
            'youtube_url': None,
            'google_analytics_id': '',
            'google_tag_manager_id': '',
            'facebook_pixel_id': '',
            'enable_maintenance_mode': False,
            'maintenance_message': '',
            'enable_cache': True,
            'cache_duration': 300,
        }
