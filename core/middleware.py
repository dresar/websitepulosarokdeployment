from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
import time

class RoleBasedAccessMiddleware:
    """
    Middleware untuk role-based access control
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Simple role check - allow all for now
        response = self.get_response(request)
        return response

class AutoCacheClearMiddleware(MiddlewareMixin):
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
        return response