import re
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from core.models import LoginHistory


def get_browser_info(user_agent):
    """Deteksi browser dari user agent"""
    user_agent = user_agent.lower()
    
    if 'chrome' in user_agent and 'edg' not in user_agent:
        return 'Chrome'
    elif 'firefox' in user_agent:
        return 'Firefox'
    elif 'safari' in user_agent and 'chrome' not in user_agent:
        return 'Safari'
    elif 'edg' in user_agent:
        return 'Edge'
    else:
        return 'Other'


def get_os_info(user_agent):
    """Deteksi OS dari user agent"""
    user_agent = user_agent.lower()
    
    if 'windows' in user_agent:
        return 'Windows'
    elif 'mac' in user_agent:
        return 'macOS'
    elif 'linux' in user_agent:
        return 'Linux'
    elif 'android' in user_agent:
        return 'Android'
    elif 'ios' in user_agent:
        return 'iOS'
    else:
        return 'Unknown'


def get_device_info(user_agent):
    """Deteksi jenis perangkat dari user agent"""
    user_agent = user_agent.lower()
    
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        return 'Mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        return 'Tablet'
    else:
        return 'Desktop'


def get_client_ip(request):
    """Ambil IP address dari request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Signal handler untuk mencatat login"""
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        browser = get_browser_info(user_agent)
        os = get_os_info(user_agent)
        device = get_device_info(user_agent)
        
        # Simpan login history
        LoginHistory.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            browser=browser,
            os=os,
            device=device,
            is_successful=True
        )
        
        # Update last login time
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
    except Exception as e:
        # Log error tapi jangan ganggu proses login
        print(f"Error logging login history: {e}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Signal handler untuk mencatat logout"""
    try:
        if user and user.is_authenticated:
            # Update logout time untuk login terakhir
            last_login = LoginHistory.objects.filter(
                user=user, 
                is_successful=True,
                logout_time__isnull=True
            ).order_by('-login_time').first()
            
            if last_login:
                last_login.logout_time = timezone.now()
                last_login.save(update_fields=['logout_time'])
                
    except Exception as e:
        # Log error tapi jangan ganggu proses logout
        print(f"Error logging logout history: {e}")


class LoginTrackingMiddleware(MiddlewareMixin):
    """Middleware untuk tracking login/logout"""
    
    def process_request(self, request):
        """Process request untuk tracking"""
        # Set session untuk tracking
        if not hasattr(request, 'session'):
            return
        
        # Track current session
        request.session['current_ip'] = get_client_ip(request)
        request.session['current_user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return None
