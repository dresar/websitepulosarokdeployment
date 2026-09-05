from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.core.cache import cache
from .models import WebsiteSettings
import time


class MaintenanceModeMiddleware:
    """
    Middleware untuk menangani mode maintenance
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip maintenance check for admin users and specific paths
        if self.should_skip_maintenance(request):
            return self.get_response(request)
        
        # Check if maintenance mode is enabled
        try:
            website_settings = WebsiteSettings.get_settings()
            if website_settings.enable_maintenance_mode:
                return self.render_maintenance_page(request, website_settings)
        except Exception as e:
            # If settings not available, continue normally
            pass
        
        return self.get_response(request)
    
    def should_skip_maintenance(self, request):
        """
        Check if request should skip maintenance mode
        """
        # Skip for admin users (check if user is available and authenticated)
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return True
        
        # Skip for admin panel paths
        admin_paths = [
            '/admin/',
            '/admin-panel/',
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        
        for path in admin_paths:
            if request.path.startswith(path):
                return True
        
        # Skip for API endpoints
        if request.path.startswith('/api/'):
            return True
        
        return False
    
    def render_maintenance_page(self, request, website_settings):
        """
        Render maintenance page
        """
        context = {
            'site_name': website_settings.site_name,
            'site_tagline': website_settings.site_tagline,
            'maintenance_message': website_settings.maintenance_message,
            'contact_email': website_settings.contact_email,
            'contact_phone': website_settings.contact_phone,
            'facebook_url': website_settings.facebook_url,
            'instagram_url': website_settings.instagram_url,
            'twitter_url': website_settings.twitter_url,
            'youtube_url': website_settings.youtube_url,
        }
        
        # Try to render custom maintenance template
        try:
            html = render_to_string('maintenance.html', context)
        except:
            # Fallback to simple maintenance page
            html = self.get_simple_maintenance_page(context)
        
        response = HttpResponse(html, status=503)
        # Add cache-busting headers
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    def get_simple_maintenance_page(self, context):
        """
        Simple maintenance page HTML
        """
        return f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Maintenance - {context['site_name']}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                }}
                .maintenance-container {{
                    text-align: center;
                    max-width: 600px;
                    padding: 40px 20px;
                }}
                .maintenance-icon {{
                    font-size: 4rem;
                    margin-bottom: 20px;
                }}
                h1 {{
                    font-size: 2.5rem;
                    margin-bottom: 20px;
                    font-weight: 300;
                }}
                .message {{
                    font-size: 1.2rem;
                    margin-bottom: 30px;
                    opacity: 0.9;
                    line-height: 1.6;
                }}
                .contact-info {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 20px;
                    border-radius: 10px;
                    margin-top: 30px;
                }}
                .contact-info h3 {{
                    margin-top: 0;
                    margin-bottom: 15px;
                }}
                .contact-item {{
                    margin: 10px 0;
                }}
                .contact-item a {{
                    color: white;
                    text-decoration: none;
                }}
                .contact-item a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="maintenance-container">
                <div class="maintenance-icon">🔧</div>
                <h1>Website Sedang Dalam Perbaikan</h1>
                <div class="message">
                    {context['maintenance_message'] or 'Website sedang dalam perbaikan. Terima kasih atas pengertian Anda.'}
                </div>
                
                <div class="contact-info">
                    <h3>Hubungi Kami</h3>
                    {f'<div class="contact-item">📧 <a href="mailto:{context["contact_email"]}">{context["contact_email"]}</a></div>' if context['contact_email'] else ''}
                    {f'<div class="contact-item">📞 {context["contact_phone"]}</div>' if context['contact_phone'] else ''}
                </div>
            </div>
        </body>
        </html>
        """


class AutoCacheClearMiddleware:
    """
    Middleware untuk auto clear cache setiap request dalam development mode
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_cache_clear = 0
        self.cache_clear_interval = 5  # Clear cache every 5 seconds
        
    def __call__(self, request):
        # Clear cache every 5 seconds
        current_time = time.time()
        if current_time - self.last_cache_clear > self.cache_clear_interval:
            try:
                cache.clear()
                self.last_cache_clear = current_time
                print(f"[{time.strftime('%H:%M:%S')}] Auto cache cleared")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Error auto clearing cache: {e}")
        
        response = self.get_response(request)
        
        # Add headers to disable browser cache
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['Last-Modified'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        return response
