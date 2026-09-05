import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from .models import Letter
# from references.models import Penduduk  # COMMENTED OUT - references app disabled
# Using letters app models instead
try:
    from letters.models import Penduduk
except ImportError:
    Penduduk = None

logger = logging.getLogger(__name__)


class LetterAccessControlMiddleware(MiddlewareMixin):
    """
    Middleware untuk mengontrol akses berdasarkan role user
    dan mencatat aktivitas user pada sistem letters
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        # Skip untuk static files dan admin
        if (request.path.startswith('/static/') or 
            request.path.startswith('/media/') or
            request.path.startswith('/admin/')):
            return None
        
        # Skip untuk anonymous users pada public endpoints
        if isinstance(request.user, AnonymousUser):
            public_paths = [
                '/letters/',
                '/letters/services/',
                '/letters/info/',
                '/letters/request/',
                '/letters/status/',
                '/letters/api/search-residents/',
            ]
            if any(request.path.startswith(path) for path in public_paths):
                return None
        
        # Check rate limiting untuk API endpoints
        if request.path.startswith('/letters/api/'):
            return self._check_rate_limit(request)
        
        # Check role-based access untuk admin endpoints
        if request.path.startswith('/letters/admin/'):
            return self._check_admin_access(request)
        
        return None
    
    def process_response(self, request, response):
        # Log aktivitas user
        if (hasattr(request, 'user') and 
            not isinstance(request.user, AnonymousUser) and
            request.path.startswith('/letters/')):
            self._log_user_activity(request, response)
        
        return response
    
    def _check_rate_limit(self, request):
        """
        Check rate limiting untuk API endpoints
        """
        if isinstance(request.user, AnonymousUser):
            # Rate limit berdasarkan IP untuk anonymous users
            client_ip = self._get_client_ip(request)
            cache_key = f'rate_limit_ip_{client_ip}'
            rate_limit = getattr(settings, 'LETTERS_API_RATE_LIMIT_ANONYMOUS', 100)
        else:
            # Rate limit berdasarkan user untuk authenticated users
            cache_key = f'rate_limit_user_{request.user.id}'
            rate_limit = getattr(settings, 'LETTERS_API_RATE_LIMIT_USER', 500)
        
        # Check current count
        current_count = cache.get(cache_key, 0)
        if current_count >= rate_limit:
            logger.warning(
                f'Rate limit exceeded for {cache_key}: {current_count}/{rate_limit}'
            )
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.',
                'limit': rate_limit,
                'reset_in': cache.ttl(cache_key)
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, current_count + 1, timeout=3600)  # 1 hour window
        return None
    
    def _check_admin_access(self, request):
        """
        Check akses untuk admin endpoints
        """
        if isinstance(request.user, AnonymousUser):
            messages.error(request, 'Anda harus login untuk mengakses halaman admin.')
            return redirect('letters:document_services')
        
        # Check apakah user memiliki permission untuk mengakses admin
        required_groups = ['Village Admin', 'Letter Admin', 'Letter Staff', 'Dusun Admin']
        user_groups = request.user.groups.values_list('name', flat=True)
        
        if not any(group in user_groups for group in required_groups):
            messages.error(
                request, 
                'Anda tidak memiliki permission untuk mengakses halaman admin.'
            )
            return redirect('letters:document_services')
        
        # Check akses berdasarkan dusun untuk Dusun Admin
        if 'Dusun Admin' in user_groups and 'Village Admin' not in user_groups:
            return self._check_dusun_access(request)
        
        return None
    
    def _check_dusun_access(self, request):
        """
        Check akses berdasarkan dusun untuk Dusun Admin
        """
        try:
            # Get user's dusun dari profile atau relasi
            user_dusun = None
            if hasattr(request.user, 'penduduk_profile'):
                user_dusun = request.user.penduduk_profile.dusun
            elif hasattr(request.user, 'profile') and hasattr(request.user.profile, 'dusun'):
                user_dusun = request.user.profile.dusun
            
            if not user_dusun:
                messages.error(
                    request,
                    'Profile dusun Anda belum diatur. Hubungi administrator.'
                )
                return redirect('letters:document_services')
            
            # Untuk detail letter, check apakah letter dari dusun yang sama
            if '/detail/' in request.path:
                letter_id = request.path.split('/')[-2]
                try:
                    letter = Letter.objects.select_related(
                        'applicant__dusun'
                    ).get(id=letter_id)
                    
                    if letter.applicant.dusun != user_dusun:
                        messages.error(
                            request,
                            'Anda hanya dapat mengakses surat dari dusun Anda.'
                        )
                        return redirect('letters:admin_letter_list')
                except (Letter.DoesNotExist, ValueError):
                    messages.error(request, 'Surat tidak ditemukan.')
                    return redirect('letters:admin_letter_list')
            
            # Set dusun filter di session untuk list views
            request.session['admin_dusun_filter'] = user_dusun.id
            
        except Exception as e:
            logger.error(f'Error checking dusun access: {e}')
            messages.error(
                request,
                'Terjadi kesalahan saat memeriksa akses. Hubungi administrator.'
            )
            return redirect('letters:document_services')
        
        return None
    
    def _log_user_activity(self, request, response):
        """
        Log aktivitas user untuk audit trail
        """
        try:
            activity_data = {
                'user_id': request.user.id,
                'username': request.user.username,
                'path': request.path,
                'method': request.method,
                'status_code': response.status_code,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
                'timestamp': time.time()
            }
            
            # Log ke file atau database sesuai konfigurasi
            if getattr(settings, 'LETTERS_LOG_USER_ACTIVITY', True):
                logger.info(
                    f"User Activity: {activity_data['username']} "
                    f"{activity_data['method']} {activity_data['path']} "
                    f"[{activity_data['status_code']}] from {activity_data['ip_address']}"
                )
            
            # Cache recent activities untuk dashboard
            cache_key = f'user_activities_{request.user.id}'
            recent_activities = cache.get(cache_key, [])
            recent_activities.insert(0, activity_data)
            recent_activities = recent_activities[:50]  # Keep last 50 activities
            cache.set(cache_key, recent_activities, timeout=86400)  # 24 hours
            
        except Exception as e:
            logger.error(f'Error logging user activity: {e}')
    
    def _get_client_ip(self, request):
        """
        Get client IP address dari request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LetterPerformanceMiddleware(MiddlewareMixin):
    """
    Middleware untuk monitoring performa aplikasi letters
    """
    
    def process_request(self, request):
        if request.path.startswith('/letters/'):
            request._letters_start_time = time.time()
    
    def process_response(self, request, response):
        if (hasattr(request, '_letters_start_time') and 
            request.path.startswith('/letters/')):
            
            duration = time.time() - request._letters_start_time
            
            # Log slow requests
            slow_threshold = getattr(settings, 'LETTERS_SLOW_REQUEST_THRESHOLD', 2.0)
            if duration > slow_threshold:
                logger.warning(
                    f'Slow request: {request.method} {request.path} '
                    f'took {duration:.2f}s (threshold: {slow_threshold}s)'
                )
            
            # Add performance header untuk debugging
            if getattr(settings, 'DEBUG', False):
                response['X-Letters-Response-Time'] = f'{duration:.3f}s'
        
        return response