"""
API Views for Village Profile
Public API endpoints for village profile data
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .models import (
    VillageProfile, VillageGeography, VillageDemography, 
    VillageOfficial, VillageFacility, VillageHistory, 
    VillagePhoto, VillageStatistic, VillageHistoryPhoto
)
from django.utils import timezone
import json


@csrf_exempt
@require_http_methods(["GET"])
def api_village_profile(request):
    """Get village profile data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        
        if not village:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        data = {
            'id': village.id,
            'name': village.name,
            'code': village.code,
            'district': village.district,
            'regency': village.regency,
            'province': village.province,
            'postal_code': village.postal_code,
            'village_head': village.village_head,
            'established_date': village.established_date.isoformat() if village.established_date else None,
            'area': float(village.area) if village.area else None,
            'description': village.description,
            'profile_description': village.profile_description,
            'vision': village.vision,
            'mission': village.mission,
            'phone': village.phone,
            'email': village.email,
            'website': village.website,
            'logo': village.logo.url if village.logo else None,
            'profile_image': village.profile_image.url if village.profile_image else None,
            'is_active': village.is_active,
            'created_at': village.created_at.isoformat(),
            'updated_at': village.updated_at.isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_geography(request):
    """Get village geography data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        
        if not village:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        geography = village.geography
        
        if not geography:
            return JsonResponse({
                'success': False,
                'message': 'Data geografis tidak ditemukan'
            }, status=404)
        
        data = {
            'village_id': geography.village.id,
            'latitude': float(geography.latitude) if geography.latitude else None,
            'longitude': float(geography.longitude) if geography.longitude else None,
            'altitude': geography.altitude,
            'climate': geography.climate,
            'rainfall': geography.rainfall,
            'temperature_min': geography.temperature_min,
            'temperature_max': geography.temperature_max,
            'topography': geography.topography,
            'soil_type': geography.soil_type,
            'boundary_north': geography.boundary_north,
            'boundary_south': geography.boundary_south,
            'boundary_east': geography.boundary_east,
            'boundary_west': geography.boundary_west,
            'created_at': geography.created_at.isoformat(),
            'updated_at': geography.updated_at.isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_demography(request):
    """Get village demography data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        
        if not village:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        demography = village.demography
        
        if not demography:
            return JsonResponse({
                'success': False,
                'message': 'Data demografi tidak ditemukan'
            }, status=404)
        
        data = {
            'village_id': demography.village.id,
            'total_population': demography.total_population,
            'male_population': demography.male_population,
            'female_population': demography.female_population,
            'total_families': demography.total_families,
            'population_density': float(demography.population_density) if demography.population_density else None,
            'growth_rate': float(demography.growth_rate) if demography.growth_rate else None,
            'age_0_14': demography.age_0_14,
            'age_15_64': demography.age_15_64,
            'age_65_plus': demography.age_65_plus,
            'education_none': demography.education_none,
            'education_elementary': demography.education_elementary,
            'education_junior': demography.education_junior,
            'education_senior': demography.education_senior,
            'education_higher': demography.education_higher,
            'employed': demography.employed,
            'unemployed': demography.unemployed,
            'year': demography.year,
            'created_at': demography.created_at.isoformat(),
            'updated_at': demography.updated_at.isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_officials(request):
    """Get village officials data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        
        if not village:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        officials = village.officials.filter(is_active=True).order_by('display_order', 'position', 'name')
        
        data = []
        for official in officials:
            data.append({
                'id': official.id,
                'name': official.name,
                'position': official.position,
                'position_display': official.position_display,
                'custom_position': official.custom_position,
                'photo': official.photo.url if official.photo else None,
                'birth_date': official.birth_date.isoformat() if official.birth_date else None,
                'education': official.education,
                'experience': official.experience,
                'phone': official.phone,
                'email': official.email,
                'address': official.address,
                'start_date': official.start_date.isoformat() if official.start_date else None,
                'end_date': official.end_date.isoformat() if official.end_date else None,
                'is_active': official.is_active,
                'display_order': official.display_order,
                'created_at': official.created_at.isoformat(),
                'updated_at': official.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_facilities(request):
    """Get village facilities data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        
        if not village:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        facilities = village.facilities.filter(is_active=True).order_by('type', 'name')
        
        data = []
        for facility in facilities:
            data.append({
                'id': facility.id,
                'name': facility.name,
                'type': facility.type,
                'type_display': facility.get_type_display(),
                'condition': facility.condition,
                'condition_display': facility.get_condition_display(),
                'description': facility.description,
                'location': facility.location,
                'capacity': facility.capacity,
                'image': facility.image.url if facility.image else None,
                'manager': facility.manager,
                'contact_person': facility.contact_person,
                'contact_phone': facility.contact_phone,
                'operational_hours': facility.operational_hours,
                'built_year': facility.built_year,
                'last_renovation': facility.last_renovation.isoformat() if facility.last_renovation else None,
                'is_active': facility.is_active,
                'is_public': facility.is_public,
                'created_at': facility.created_at.isoformat(),
                'updated_at': facility.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_history(request):
    """Get village history data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        
        if not village:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        # Get all history entries
        histories = VillageHistory.objects.filter(is_active=True).order_by('-is_featured', 'year_start', 'period_start')
        
        data = []
        for history in histories:
            data.append({
                'id': history.id,
                'title': history.title,
                'slug': history.slug,
                'summary': history.summary,
                'content': history.content,
                'history_type': history.history_type,
                'history_type_display': history.get_history_type_display(),
                'period_start': history.period_start,
                'period_end': history.period_end,
                'year_start': history.year_start,
                'year_end': history.year_end,
                'featured_image': history.featured_image.url if history.featured_image else None,
                'featured_image_caption': history.featured_image_caption,
                'source': history.source,
                'author': history.author,
                'is_featured': history.is_featured,
                'is_active': history.is_active,
                'view_count': history.view_count,
                'photo_count': history.photo_count,
                'created_at': history.created_at.isoformat(),
                'updated_at': history.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_gallery(request):
    """Get village gallery data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        
        if not village:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        photos = village.photos.filter(is_active=True).order_by('-is_featured', 'display_order', '-created_at')
        
        data = []
        for photo in photos:
            data.append({
                'id': photo.id,
                'title': photo.title,
                'image': photo.image.url if photo.image else None,
                'description': photo.description,
                'photo_type': photo.photo_type,
                'photo_type_display': photo.get_photo_type_display(),
                'photographer': photo.photographer,
                'photo_date': photo.photo_date.isoformat() if photo.photo_date else None,
                'location': photo.location,
                'is_featured': photo.is_featured,
                'is_active': photo.is_active,
                'display_order': photo.display_order,
                'view_count': photo.view_count,
                'created_at': photo.created_at.isoformat(),
                'updated_at': photo.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_complete(request):
    """Get complete village data including all related information"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        
        if not village:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        # Get all related data
        geography = village.geography
        demography = village.demography
        officials = village.officials.filter(is_active=True).order_by('display_order', 'position', 'name')
        facilities = village.facilities.filter(is_active=True).order_by('type', 'name')
        histories = VillageHistory.objects.filter(is_active=True).order_by('-is_featured', 'year_start', 'period_start')
        photos = village.photos.filter(is_active=True).order_by('-is_featured', 'display_order', '-created_at')
        
        # Build complete data structure
        data = {
            'village': {
                'id': village.id,
                'name': village.name,
                'code': village.code,
                'district': village.district,
                'regency': village.regency,
                'province': village.province,
                'postal_code': village.postal_code,
                'village_head': village.village_head,
                'established_date': village.established_date.isoformat() if village.established_date else None,
                'area': float(village.area) if village.area else None,
                'description': village.description,
                'profile_description': village.profile_description,
                'vision': village.vision,
                'mission': village.mission,
                'phone': village.phone,
                'email': village.email,
                'website': village.website,
                'logo': village.logo.url if village.logo else None,
                'profile_image': village.profile_image.url if village.profile_image else None,
                'is_active': village.is_active,
                'created_at': village.created_at.isoformat(),
                'updated_at': village.updated_at.isoformat()
            },
            'geography': {
                'latitude': float(geography.latitude) if geography and geography.latitude else None,
                'longitude': float(geography.longitude) if geography and geography.longitude else None,
                'altitude': geography.altitude if geography else None,
                'climate': geography.climate if geography else None,
                'rainfall': geography.rainfall if geography else None,
                'temperature_min': geography.temperature_min if geography else None,
                'temperature_max': geography.temperature_max if geography else None,
                'topography': geography.topography if geography else None,
                'soil_type': geography.soil_type if geography else None,
                'boundary_north': geography.boundary_north if geography else None,
                'boundary_south': geography.boundary_south if geography else None,
                'boundary_east': geography.boundary_east if geography else None,
                'boundary_west': geography.boundary_west if geography else None,
            } if geography else None,
            'demography': {
                'total_population': demography.total_population if demography else None,
                'male_population': demography.male_population if demography else None,
                'female_population': demography.female_population if demography else None,
                'total_families': demography.total_families if demography else None,
                'population_density': float(demography.population_density) if demography and demography.population_density else None,
                'growth_rate': float(demography.growth_rate) if demography and demography.growth_rate else None,
                'year': demography.year if demography else None,
            } if demography else None,
            'officials': [
                {
                    'id': official.id,
                    'name': official.name,
                    'position': official.position,
                    'position_display': official.position_display,
                    'photo': official.photo.url if official.photo else None,
                    'education': official.education,
                    'phone': official.phone,
                    'email': official.email,
                    'start_date': official.start_date.isoformat() if official.start_date else None,
                    'end_date': official.end_date.isoformat() if official.end_date else None,
                }
                for official in officials
            ],
            'facilities': [
                {
                    'id': facility.id,
                    'name': facility.name,
                    'type': facility.type,
                    'type_display': facility.get_type_display(),
                    'condition': facility.condition,
                    'condition_display': facility.get_condition_display(),
                    'description': facility.description,
                    'location': facility.location,
                    'capacity': facility.capacity,
                    'image': facility.image.url if facility.image else None,
                    'manager': facility.manager,
                    'operational_hours': facility.operational_hours,
                    'is_public': facility.is_public,
                }
                for facility in facilities
            ],
            'histories': [
                {
                    'id': history.id,
                    'title': history.title,
                    'slug': history.slug,
                    'summary': history.summary,
                    'content': history.content,
                    'history_type': history.history_type,
                    'history_type_display': history.get_history_type_display(),
                    'year_start': history.year_start,
                    'year_end': history.year_end,
                    'featured_image': history.featured_image.url if history.featured_image else None,
                    'is_featured': history.is_featured,
                    'view_count': history.view_count,
                }
                for history in histories
            ],
            'gallery': [
                {
                    'id': photo.id,
                    'title': photo.title,
                    'image': photo.image.url if photo.image else None,
                    'description': photo.description,
                    'photo_type': photo.photo_type,
                    'photo_type_display': photo.get_photo_type_display(),
                    'is_featured': photo.is_featured,
                    'view_count': photo.view_count,
                }
                for photo in photos
            ]
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
