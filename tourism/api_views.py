"""
Tourism API Views
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json

# Try to import Penduduk model from different apps
try:
    from references.models import Penduduk
    PENDUDUK_MODEL = Penduduk
    PENDUDUK_APP = 'references'
except ImportError:
    try:
        from letters.models import Penduduk
        PENDUDUK_MODEL = Penduduk
        PENDUDUK_APP = 'letters'
    except ImportError:
        PENDUDUK_MODEL = None
        PENDUDUK_APP = None

@csrf_exempt
@require_http_methods(["GET"])
def api_penduduk_search(request):
    """
    API to search penduduk for tourism package owners and self data
    """
    if not PENDUDUK_MODEL:
        return JsonResponse({
            'success': False,
            'error': 'Penduduk model not available'
        }, status=400)
    
    search_query = request.GET.get('q', '').strip()
    
    if not search_query:
        return JsonResponse({
            'success': False,
            'error': 'Search query is required'
        }, status=400)
    
    try:
        # Search penduduk by name or NIK
        if PENDUDUK_APP == 'references':
            # Using references.models.Penduduk
            penduduk_list = PENDUDUK_MODEL.objects.filter(
                Q(name__icontains=search_query) | 
                Q(nik__icontains=search_query)
            ).filter(is_active=True)[:20]
            
            results = []
            for penduduk in penduduk_list:
                results.append({
                    'id': penduduk.id,
                    'name': penduduk.name,
                    'nik': penduduk.nik,
                    'email': getattr(penduduk, 'email', ''),
                    'phone': getattr(penduduk, 'phone', ''),
                    'address': getattr(penduduk, 'address', ''),
                    'is_active': getattr(penduduk, 'is_active', True)
                })
                
        else:
            # Using letters.models.Penduduk
            penduduk_list = PENDUDUK_MODEL.objects.filter(
                Q(nama__icontains=search_query) | 
                Q(nik__icontains=search_query)
            )[:20]
            
            results = []
            for penduduk in penduduk_list:
                results.append({
                    'id': penduduk.id,
                    'name': penduduk.nama,
                    'nik': penduduk.nik,
                    'email': getattr(penduduk, 'email', ''),
                    'phone': getattr(penduduk, 'telepon', ''),
                    'address': getattr(penduduk, 'alamat', ''),
                    'is_active': True
                })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error searching penduduk: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_penduduk_detail(request, penduduk_id):
    """
    API to get detailed penduduk information
    """
    if not PENDUDUK_MODEL:
        return JsonResponse({
            'success': False,
            'error': 'Penduduk model not available'
        }, status=400)
    
    try:
        penduduk = PENDUDUK_MODEL.objects.get(id=penduduk_id)
        
        if PENDUDUK_APP == 'references':
            # Using references.models.Penduduk
            data = {
                'id': penduduk.id,
                'name': penduduk.name,
                'nik': penduduk.nik,
                'email': getattr(penduduk, 'email', ''),
                'phone': getattr(penduduk, 'phone', ''),
                'address': getattr(penduduk, 'address', ''),
                'birth_date': getattr(penduduk, 'birth_date', ''),
                'gender': getattr(penduduk, 'gender', ''),
                'is_active': getattr(penduduk, 'is_active', True),
                'created_at': penduduk.created_at.isoformat() if hasattr(penduduk, 'created_at') else '',
                'updated_at': penduduk.updated_at.isoformat() if hasattr(penduduk, 'updated_at') else ''
            }
        else:
            # Using letters.models.Penduduk
            data = {
                'id': penduduk.id,
                'name': penduduk.nama,
                'nik': penduduk.nik,
                'email': getattr(penduduk, 'email', ''),
                'phone': getattr(penduduk, 'telepon', ''),
                'address': getattr(penduduk, 'alamat', ''),
                'birth_date': getattr(penduduk, 'tanggal_lahir', ''),
                'gender': getattr(penduduk, 'jenis_kelamin', ''),
                'is_active': True,
                'created_at': penduduk.created_at.isoformat() if hasattr(penduduk, 'created_at') else '',
                'updated_at': penduduk.updated_at.isoformat() if hasattr(penduduk, 'updated_at') else ''
            }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except PENDUDUK_MODEL.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Penduduk not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error getting penduduk detail: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_penduduk_self(request):
    """
    API to get current user's penduduk data (if they are a penduduk)
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)
    
    if not PENDUDUK_MODEL:
        return JsonResponse({
            'success': False,
            'error': 'Penduduk model not available'
        }, status=400)
    
    try:
        # Try to find penduduk by user's email or name
        user = request.user
        
        # Search by email first
        penduduk = None
        if user.email:
            try:
                if PENDUDUK_APP == 'references':
                    penduduk = PENDUDUK_MODEL.objects.get(email=user.email)
                else:
                    penduduk = PENDUDUK_MODEL.objects.get(email=user.email)
            except PENDUDUK_MODEL.DoesNotExist:
                pass
        
        # If not found by email, try by name
        if not penduduk:
            try:
                if PENDUDUK_APP == 'references':
                    penduduk = PENDUDUK_MODEL.objects.get(name=user.get_full_name())
                else:
                    penduduk = PENDUDUK_MODEL.objects.get(nama=user.get_full_name())
            except PENDUDUK_MODEL.DoesNotExist:
                pass
        
        if not penduduk:
            return JsonResponse({
                'success': False,
                'error': 'No penduduk data found for current user'
            }, status=404)
        
        # Return penduduk data
        if PENDUDUK_APP == 'references':
            data = {
                'id': penduduk.id,
                'name': penduduk.name,
                'nik': penduduk.nik,
                'email': getattr(penduduk, 'email', ''),
                'phone': getattr(penduduk, 'phone', ''),
                'address': getattr(penduduk, 'address', ''),
                'birth_date': getattr(penduduk, 'birth_date', ''),
                'gender': getattr(penduduk, 'gender', ''),
                'is_active': getattr(penduduk, 'is_active', True)
            }
        else:
            data = {
                'id': penduduk.id,
                'name': penduduk.nama,
                'nik': penduduk.nik,
                'email': getattr(penduduk, 'email', ''),
                'phone': getattr(penduduk, 'telepon', ''),
                'address': getattr(penduduk, 'alamat', ''),
                'birth_date': getattr(penduduk, 'tanggal_lahir', ''),
                'gender': getattr(penduduk, 'jenis_kelamin', ''),
                'is_active': True
            }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error getting self penduduk data: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_penduduk_list(request):
    """
    API to get list of penduduk for package owners
    """
    if not PENDUDUK_MODEL:
        return JsonResponse({
            'success': False,
            'error': 'Penduduk model not available'
        }, status=400)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        search = request.GET.get('search', '').strip()
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build query
        query = Q()
        if search:
            if PENDUDUK_APP == 'references':
                query = Q(name__icontains=search) | Q(nik__icontains=search)
            else:
                query = Q(nama__icontains=search) | Q(nik__icontains=search)
        
        # Add active filter for references model
        if PENDUDUK_APP == 'references':
            query &= Q(is_active=True)
        
        # Get penduduk list
        penduduk_list = PENDUDUK_MODEL.objects.filter(query)[offset:offset + limit]
        total_count = PENDUDUK_MODEL.objects.filter(query).count()
        
        results = []
        for penduduk in penduduk_list:
            if PENDUDUK_APP == 'references':
                results.append({
                    'id': penduduk.id,
                    'name': penduduk.name,
                    'nik': penduduk.nik,
                    'email': getattr(penduduk, 'email', ''),
                    'phone': getattr(penduduk, 'phone', ''),
                    'is_active': getattr(penduduk, 'is_active', True)
                })
            else:
                results.append({
                    'id': penduduk.id,
                    'name': penduduk.nama,
                    'nik': penduduk.nik,
                    'email': getattr(penduduk, 'email', ''),
                    'phone': getattr(penduduk, 'telepon', ''),
                    'is_active': True
                })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': len(results),
            'total_count': total_count,
            'page': page,
            'limit': limit,
            'total_pages': (total_count + limit - 1) // limit
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error getting penduduk list: {str(e)}'
        }, status=500)

