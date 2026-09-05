from django.shortcuts import render, get_object_or_404, redirect
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
from datetime import datetime
import json


def profile_view(request):
    """Main profile view with all necessary data"""
    try:
        # Get the main village profile (assuming there's only one active village)
        village = VillageProfile.objects.filter(is_active=True).first()
        
        if not village:
            # Create default data if no village exists
            context = {
                'page_title': 'Profil Desa Pulosarok',
                'profile_data': {
                    'name': 'Pulosarok',
                    'district': 'Cina',
                    'regency': 'Bone',
                    'province': 'Sulawesi Selatan',
                    'postal_code': '92700',
                    'village_head': 'Kepala Desa',
                    'area': '10.5',
                    'description': 'Desa Pulosarok adalah desa yang terletak di Kecamatan Cina, Kabupaten Bone, Sulawesi Selatan.',
                    'vision': 'Menjadi desa yang maju, mandiri, dan sejahtera.',
                    'mission': ['Meningkatkan kesejahteraan masyarakat', 'Mengembangkan potensi desa', 'Memperkuat tata kelola pemerintahan']
                },
                'geography_data': {
                    'latitude': '-4.5000000',
                    'longitude': '120.2000000',
                    'altitude': '100',
                    'climate': 'Tropis',
                    'rainfall': '2000',
                    'temperature': '25-32°C',
                    'topography': 'Dataran rendah',
                    'soil_type': 'Alluvial',
                    'boundaries': {
                        'north': 'Desa Utara',
                        'south': 'Desa Selatan',
                        'east': 'Desa Timur',
                        'west': 'Desa Barat'
                    }
                },
                'demography_data': {
                    'total_population': 5000,
                    'male_population': 2500,
                    'female_population': 2500,
                    'total_families': 1250,
                    'population_density': 476.19,
                    'age_groups': {
                        'age_0_14': 1500,
                        'age_15_64': 3000,
                        'age_65_plus': 500
                    },
                    'education': {
                        'none': 200,
                        'elementary': 2000,
                        'junior': 1500,
                        'senior': 1000,
                        'higher': 300
                    },
                    'employment': {
                        'employed': 2800,
                        'unemployed': 200
                    }
                },
                'facilities_data': [
                    {
                        'name': 'Kantor Desa',
                        'type': 'PEMERINTAHAN',
                        'condition': 'BAIK',
                        'location': 'Pusat Desa',
                        'description': 'Kantor pelayanan administrasi desa'
                    },
                    {
                        'name': 'Puskesmas Pembantu',
                        'type': 'KESEHATAN',
                        'condition': 'BAIK',
                        'location': 'Dusun 1',
                        'description': 'Fasilitas kesehatan masyarakat'
                    },
                    {
                        'name': 'SD Negeri Pulosarok',
                        'type': 'PENDIDIKAN',
                        'condition': 'BAIK',
                        'location': 'Dusun 2',
                        'description': 'Sekolah dasar negeri'
                    }
                ],
                'statistics_data': {
                    'total_population': 5000,
                    'total_dusun': 3,
                    'total_facilities': 15,
                    'total_umkm': 25
                },
                'officials_data': [
                    {
                        'name': 'Kepala Desa',
                        'position': 'KEPALA_DESA',
                        'position_display': 'Kepala Desa'
                    },
                    {
                        'name': 'Sekretaris Desa',
                        'position': 'SEKRETARIS',
                        'position_display': 'Sekretaris Desa'
                    }
                ],
                'history_data': [
                    {
                        'title': 'Sejarah Berdirinya Desa Pulosarok',
                        'content': 'Desa Pulosarok didirikan pada tahun 1950...',
                        'period_display': 'Sejak 1950',
                        'history_type': 'FOUNDING'
                    }
                ],
                'photos_data': []
            }
            return render(request, 'public/village_profile/profile.html', context)
        
        # Get related data
        geography = getattr(village, 'geography', None)
        demography = village.demography.filter(is_active=True).order_by('-year').first() if hasattr(village, 'demography') else None
        facilities = village.facilities.filter(is_active=True).order_by('type', 'name')
        officials = village.officials.filter(is_active=True).order_by('display_order', 'position')
        statistics = village.statistics.filter().order_by('-year').first() if hasattr(village, 'statistics') else None
        history = VillageHistory.objects.filter(is_active=True).order_by('-is_featured', 'year_start')
        photos = village.photos.filter(is_active=True).order_by('-is_featured', 'display_order')
        
        # Prepare profile data
        profile_data = {
            'name': village.name,
            'district': village.district,
            'regency': village.regency,
            'province': village.province,
            'postal_code': village.postal_code,
            'village_head': village.village_head,
            'area': str(village.area),
            'description': village.description,
            'vision': village.vision,
            'mission': village.mission_list
        }
        
        # Prepare geography data
        geography_data = {}
        if geography:
            geography_data = {
                'latitude': str(geography.latitude),
                'longitude': str(geography.longitude),
                'altitude': f"{geography.altitude} mdpl",
                'climate': geography.climate,
                'rainfall': f"{geography.rainfall} mm/tahun",
                'temperature': geography.temperature_range,
                'topography': geography.topography,
                'soil_type': geography.soil_type,
                'boundaries': geography.boundaries
            }
        
        # Prepare demography data
        demography_data = {}
        if demography:
            demography_data = {
                'total_population': demography.total_population,
                'male_population': demography.male_population,
                'female_population': demography.female_population,
                'total_families': demography.total_families,
                'population_density': float(demography.population_density),
                'age_groups': {
                    'age_0_14': demography.age_0_14,
                    'age_15_64': demography.age_15_64,
                    'age_65_plus': demography.age_65_plus
                },
                'education': {
                    'none': demography.education_none,
                    'elementary': demography.education_elementary,
                    'junior': demography.education_junior,
                    'senior': demography.education_senior,
                    'higher': demography.education_higher
                },
                'employment': {
                    'employed': demography.employed,
                    'unemployed': demography.unemployed
                }
            }
        
        # Prepare facilities data
        facilities_data = []
        for facility in facilities:
            facilities_data.append({
                'name': facility.name,
                'type': facility.type,
                'condition': facility.condition,
                'location': facility.location,
                'description': facility.description,
                'capacity': facility.capacity or '',
                'manager': facility.manager or '',
                'operational_hours': facility.operational_hours or ''
            })
        
        # Prepare statistics data
        statistics_data = {}
        if statistics:
            statistics_data = {
                'total_population': demography.total_population if demography else 0,
                'total_dusun': statistics.total_dusun,
                'total_facilities': statistics.total_facilities,
                'total_umkm': statistics.total_umkm
            }
        elif demography:
            statistics_data = {
                'total_population': demography.total_population,
                'total_dusun': 3,  # Default value
                'total_facilities': facilities.count(),
                'total_umkm': 25  # Default value
            }
        
        # Prepare officials data
        officials_data = []
        for official in officials:
            officials_data.append({
                'name': official.name,
                'position': official.position,
                'position_display': official.position_display,
                'education': official.education or '',
                'phone': official.phone or '',
                'email': official.email or ''
            })
        
        # Prepare history data
        history_data = []
        for item in history:
            history_data.append({
                'title': item.title,
                'content': item.content,
                'summary': item.summary or '',
                'period_display': item.period_display,
                'history_type': item.history_type,
                'year_start': item.year_start
            })
        
        # Prepare photos data
        photos_data = []
        for photo in photos[:12]:  # Limit to 12 photos
            photos_data.append({
                'title': photo.title,
                'image_url': photo.image.url if photo.image else '',
                'description': photo.description or '',
                'photo_type': photo.photo_type,
                'photographer': photo.photographer or '',
                'location': photo.location or ''
            })
        
        context = {
            'page_title': f'Profil {village.name}',
            'profile_data': profile_data,
            'geography_data': geography_data,
            'demography_data': demography_data,
            'facilities_data': facilities_data,
            'statistics_data': statistics_data,
            'officials_data': officials_data,
            'history_data': history_data,
            'photos_data': photos_data
        }
        
        return render(request, 'public/village_profile/profile.html', context)
        
    except Exception as e:
        # Fallback context in case of any error
        context = {
            'page_title': 'Profil Desa Pulosarok',
            'profile_data': {
                'name': 'Pulosarok',
                'district': 'Cina',
                'regency': 'Bone',
                'province': 'Sulawesi Selatan',
                'postal_code': '92700',
                'village_head': 'Kepala Desa',
                'area': '10.5',
                'description': 'Desa Pulosarok adalah desa yang terletak di Kecamatan Cina, Kabupaten Bone, Sulawesi Selatan.',
                'vision': 'Menjadi desa yang maju, mandiri, dan sejahtera.',
                'mission': ['Meningkatkan kesejahteraan masyarakat', 'Mengembangkan potensi desa', 'Memperkuat tata kelola pemerintahan']
            },
            'geography_data': {},
            'demography_data': {},
            'facilities_data': [],
            'statistics_data': {'total_population': 0, 'total_dusun': 0, 'total_facilities': 0, 'total_umkm': 0},
            'officials_data': [],
            'history_data': [],
            'photos_data': []
        }
        return render(request, 'public/village_profile/profile.html', context)


# AJAX endpoints for dynamic loading (with CSRF protection)
@csrf_exempt
@require_http_methods(["GET", "POST"])
def ajax_profile_data(request):
    """AJAX endpoint for profile data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        if village:
            data = {
                'name': village.name,
                'district': village.district,
                'regency': village.regency,
                'province': village.province,
                'postal_code': village.postal_code,
                'village_head': village.village_head,
                'area': str(village.area),
                'description': village.description,
                'profile_description': village.profile_description,
                'vision': village.vision,
                'mission': village.mission_list,
                'logo': village.logo.url if village.logo else None,
                'profile_image': village.profile_image.url if village.profile_image else None
            }
        else:
            data = {
                'name': 'Pulosarok',
                'district': 'Cina',
                'regency': 'Bone',
                'province': 'Sulawesi Selatan',
                'postal_code': '92700',
                'village_head': 'Kepala Desa',
                'area': '10.5',
                'description': 'Desa Pulosarok adalah desa yang terletak di Kecamatan Cina, Kabupaten Bone, Sulawesi Selatan.',
                'vision': 'Menjadi desa yang maju, mandiri, dan sejahtera.',
                'mission': ['Meningkatkan kesejahteraan masyarakat', 'Mengembangkan potensi desa', 'Memperkuat tata kelola pemerintahan']
            }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ajax_officials_data(request):
    """AJAX endpoint for officials data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        if village:
            officials = VillageOfficial.objects.filter(village=village, is_active=True).order_by('display_order', 'position')
            data = []
            for official in officials:
                data.append({
                    'id': official.id,
                    'name': official.name,
                    'position': official.position,
                    'position_display': official.position_display,
                    'custom_position': official.custom_position or '',
                    'education': official.education or 'Tidak diketahui',
                    'phone': official.phone or '',
                    'email': official.email or '',
                    'address': official.address or '',
                    'photo': official.photo.url if official.photo else None,
                    'start_date': official.start_date.strftime('%Y-%m-%d') if official.start_date else None,
                    'end_date': official.end_date.strftime('%Y-%m-%d') if official.end_date else None,
                    'display_order': official.display_order,
                    'experience': official.experience or '',
                    'is_active': official.is_active
                })
        else:
            # Data dummy jika tidak ada data
            data = [
                {
                    'id': 1,
                    'name': 'Kepala Desa',
                    'position': 'KEPALA_DESA',
                    'position_display': 'Kepala Desa',
                    'custom_position': '',
                    'education': 'S1',
                    'phone': '081234567890',
                    'email': 'kepaladesa@example.com',
                    'address': 'Desa Pulosarok',
                    'photo': None,
                    'start_date': '2020-01-01',
                    'end_date': None,
                    'display_order': 1,
                    'experience': '10 tahun',
                    'is_active': True
                },
                {
                    'id': 2,
                    'name': 'Sekretaris Desa',
                    'position': 'SEKRETARIS',
                    'position_display': 'Sekretaris Desa',
                    'custom_position': '',
                    'education': 'S1',
                    'phone': '081234567891',
                    'email': 'sekretaris@example.com',
                    'address': 'Desa Pulosarok',
                    'photo': None,
                    'start_date': '2020-01-01',
                    'end_date': None,
                    'display_order': 2,
                    'experience': '8 tahun',
                    'is_active': True
                }
            ]
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Dashboard utama
def dashboard_view(request):
    """Main consolidated view with all village data"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        # Get related data
        village_history = None
        village_geography = None
        demographics = None
        officials_data = []
        facilities = []
        gallery_photos = []
        
        if village_profile:
            # Get village history
            village_history = VillageHistory.objects.filter(is_active=True).order_by('-is_featured', 'year_start').first()
            
            # Get geography data
            try:
                village_geography = village_profile.geography
            except:
                village_geography = None
            
            # Get demographics data
            try:
                demographics = village_profile.demography
            except:
                demographics = None
            
            # Get officials data with photos
            officials_data = village_profile.officials.filter(is_active=True).order_by('display_order', 'position')[:8]  # Limit to 8 for dashboard
            
            # Get facilities
            facilities = village_profile.facilities.filter(is_active=True).order_by('type', 'name')[:6]  # Limit to 6 for dashboard
            
            # Get gallery photos for slider
            gallery_photos = village_profile.photos.filter(is_active=True).order_by('-is_featured', 'display_order')[:10]  # Limit to 10 for slider
        
        context = {
            'village_profile': village_profile,
            'village_history': village_history,
            'village_geography': village_geography,
            'demographics': demographics,
            'officials_data': officials_data,
            'facilities': facilities,
            'gallery_photos': gallery_photos,
            'page_title': 'Profil Desa Pulosarok'
        }
        return render(request, 'public/village_profile/index.html', context)
    except Exception as e:
        context = {
            'error': str(e),
            'page_title': 'Profil Desa Pulosarok'
        }
        return render(request, 'public/village_profile/index.html', context)

# View untuk Sejarah Desa
def history_view(request):
    """History page view with search and filter"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        histories = VillageHistory.objects.filter(is_active=True).order_by('-is_featured', 'year_start')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            histories = histories.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(summary__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(source__icontains=search_query)
            )
        
        # Filter by history type
        history_type = request.GET.get('type', '')
        if history_type:
            histories = histories.filter(history_type=history_type)
        
        # Filter by featured
        featured = request.GET.get('featured', '')
        if featured == 'true':
            histories = histories.filter(is_featured=True)
        elif featured == 'false':
            histories = histories.filter(is_featured=False)
        
        context = {
            'village_profile': village_profile,
            'histories': histories,
            'page_title': 'Sejarah Desa',
            'search_query': search_query,
            'selected_type': history_type,
            'selected_featured': featured,
            'history_types': [
                ('FOUNDING', 'Sejarah Berdiri'),
                ('DEVELOPMENT', 'Perkembangan'),
                ('CULTURE', 'Budaya & Tradisi'),
                ('ECONOMY', 'Ekonomi'),
                ('SOCIAL', 'Sosial'),
                ('GOVERNMENT', 'Pemerintahan'),
                ('OTHER', 'Lainnya')
            ]
        }
        return render(request, 'public/village_profile/history.html', context)
    except Exception as e:
        return dashboard_view(request)


# View untuk Detail Sejarah
def history_detail_view(request, history_id):
    """History detail page view"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        history = get_object_or_404(VillageHistory, id=history_id, is_active=True)
        
        # Increment view count
        history.view_count += 1
        history.save(update_fields=['view_count'])
        
        context = {
            'village_profile': village_profile,
            'history': history,
            'page_title': f'Detail Sejarah - {history.title}'
        }
        return render(request, 'public/village_profile/history_detail.html', context)
    except Exception as e:
        return redirect('village_profile:history')

# View untuk Visi Misi
def vision_mission_view(request):
    """Vision and mission page view"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        context = {
            'village_profile': village_profile,
            'page_title': 'Visi & Misi Desa'
        }
        return render(request, 'public/village_profile/vision_mission.html', context)
    except Exception as e:
        return dashboard_view(request)

# View untuk Geografis
def geography_view(request):
    """Geography page view"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        geography = None
        
        if village_profile:
            try:
                geography = village_profile.geography
            except:
                geography = None
        
        context = {
            'village_profile': village_profile,
            'geography': geography,
            'page_title': 'Informasi Geografis'
        }
        return render(request, 'public/village_profile/geography.html', context)
    except Exception as e:
        return dashboard_view(request)

# View untuk Perangkat Desa
def officials_view(request):
    """Officials page view"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        officials = village_profile.officials.filter(is_active=True).order_by('display_order', 'position') if village_profile else []
        
        context = {
            'village_profile': village_profile,
            'officials': officials,
            'page_title': 'Perangkat Desa'
        }
        return render(request, 'public/village_profile/officials.html', context)
    except Exception as e:
        return dashboard_view(request)

# View untuk Fasilitas
def facilities_view(request):
    """Facilities page view"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        facilities = village_profile.facilities.filter(is_active=True).order_by('type', 'name') if village_profile else []
        
        context = {
            'village_profile': village_profile,
            'facilities': facilities,
            'page_title': 'Fasilitas Desa'
        }
        return render(request, 'public/village_profile/facilities.html', context)
    except Exception as e:
        return dashboard_view(request)

# View untuk Galeri Foto
def gallery_view(request):
    """Gallery page view with pagination and search"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        photos = []
        
        if village_profile:
            photos = village_profile.photos.filter(is_active=True).order_by('-is_featured', 'display_order')
            
            # Search functionality
            search_query = request.GET.get('search', '')
            if search_query:
                photos = photos.filter(
                    Q(title__icontains=search_query) | 
                    Q(description__icontains=search_query) |
                    Q(location__icontains=search_query) |
                    Q(photographer__icontains=search_query)
                )
            
            # Filter by photo type
            photo_type = request.GET.get('type', '')
            if photo_type:
                photos = photos.filter(photo_type=photo_type)
            
            # Pagination
            paginator = Paginator(photos, 12)  # 12 photos per page
            page_number = request.GET.get('page')
            photos = paginator.get_page(page_number)
        
        context = {
            'village_profile': village_profile,
            'photos': photos,
            'page_title': 'Galeri Foto',
            'search_query': request.GET.get('search', ''),
            'selected_type': request.GET.get('type', ''),
            'photo_types': [
                ('PEMERINTAHAN', 'Pemerintahan'),
                ('EKONOMI', 'Ekonomi'),
                ('SOSIAL', 'Sosial'),
                ('BUDAYA', 'Budaya'),
                ('PENDIDIKAN', 'Pendidikan'),
                ('KESEHATAN', 'Kesehatan'),
                ('INFRASTRUKTUR', 'Infrastruktur'),
                ('LINGKUNGAN', 'Lingkungan'),
                ('LAINNYA', 'Lainnya')
            ]
        }
        return render(request, 'public/village_profile/gallery.html', context)
    except Exception as e:
        return dashboard_view(request)

# View untuk Demografi
def demography_view(request):
    """Demography page view"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        demography = None
        
        if village_profile:
            try:
                demography = village_profile.demography
            except:
                demography = None
        
        context = {
            'village_profile': village_profile,
            'demography': demography,
            'page_title': 'Informasi Demografi'
        }
        return render(request, 'public/village_profile/demography.html', context)
    except Exception as e:
        return dashboard_view(request)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ajax_geography_data(request):
    """AJAX endpoint for geography data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        if village and hasattr(village, 'geography'):
            geography = village.geography
            data = {
                'latitude': str(geography.latitude),
                'longitude': str(geography.longitude),
                'altitude': f"{geography.altitude} mdpl",
                'climate': geography.climate,
                'rainfall': f"{geography.rainfall} mm/tahun",
                'temperature': geography.temperature_range,
                'topography': geography.topography,
                'soil_type': geography.soil_type,
                'boundaries': geography.boundaries
            }
        else:
            data = {
                'latitude': '-4.5000000',
                'longitude': '120.2000000',
                'altitude': '100 mdpl',
                'climate': 'Tropis',
                'rainfall': '2000 mm/tahun',
                'temperature': '25-32°C',
                'topography': 'Dataran rendah',
                'soil_type': 'Alluvial',
                'boundaries': {
                    'north': 'Desa Utara',
                    'south': 'Desa Selatan',
                    'east': 'Desa Timur',
                    'west': 'Desa Barat'
                }
            }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ajax_demography_data(request):
    """AJAX endpoint for demography data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        if village:
            try:
                demography = village.demography
            except VillageDemography.DoesNotExist:
                demography = None
            if demography:
                data = {
                    'total_population': demography.total_population,
                    'male_population': demography.male_population,
                    'female_population': demography.female_population,
                    'total_families': demography.total_families,
                    'population_density': float(demography.population_density),
                    'age_groups': {
                        'age_0_14': demography.age_0_14,
                        'age_15_64': demography.age_15_64,
                        'age_65_plus': demography.age_65_plus
                    },
                    'education': {
                        'none': demography.education_none,
                        'elementary': demography.education_elementary,
                        'junior': demography.education_junior,
                        'senior': demography.education_senior,
                        'higher': demography.education_higher
                    },
                    'employment': {
                        'employed': demography.employed,
                        'unemployed': demography.unemployed
                    }
                }
            else:
                data = {
                    'total_population': 5000,
                    'male_population': 2500,
                    'female_population': 2500,
                    'total_families': 1250,
                    'population_density': 476.19,
                    'age_groups': {
                        'age_0_14': 1500,
                        'age_15_64': 3000,
                        'age_65_plus': 500
                    },
                    'education': {
                        'none': 200,
                        'elementary': 2000,
                        'junior': 1500,
                        'senior': 1000,
                        'higher': 300
                    },
                    'employment': {
                        'employed': 2800,
                        'unemployed': 200
                    }
                }
        else:
            data = {
                'total_population': 5000,
                'male_population': 2500,
                'female_population': 2500,
                'total_families': 1250,
                'population_density': 476.19,
                'age_groups': {
                    'age_0_14': 1500,
                    'age_15_64': 3000,
                    'age_65_plus': 500
                },
                'education': {
                    'none': 200,
                    'elementary': 2000,
                    'junior': 1500,
                    'senior': 1000,
                    'higher': 300
                },
                'employment': {
                    'employed': 2800,
                    'unemployed': 200
                }
            }
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ajax_facilities_data(request):
    """AJAX endpoint for facilities data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        facilities_data = []
        
        if village:
            facilities = village.facilities.filter(is_active=True).order_by('type', 'name')
            for facility in facilities:
                facilities_data.append({
                    'id': facility.id,
                    'name': facility.name,
                    'type': facility.type,
                    'condition': facility.condition,
                    'location': facility.location,
                    'description': facility.description,
                    'capacity': facility.capacity or '',
                    'manager': facility.manager or '',
                    'contact_person': facility.contact_person or '',
                    'contact_phone': facility.contact_phone or '',
                    'operational_hours': facility.operational_hours or '',
                    'built_year': facility.built_year,
                    'last_renovation': facility.last_renovation.strftime('%Y-%m-%d') if facility.last_renovation else None,
                    'is_public': facility.is_public,
                    'image': facility.image.url if facility.image else None
                })
        
        if not facilities_data:
            facilities_data = [
                {
                    'id': 1,
                    'name': 'Kantor Desa',
                    'type': 'PEMERINTAHAN',
                    'condition': 'BAIK',
                    'location': 'Pusat Desa',
                    'description': 'Kantor pelayanan administrasi desa',
                    'capacity': '50 orang',
                    'manager': 'Sekretaris Desa',
                    'contact_person': 'Sekretaris Desa',
                    'contact_phone': '081234567890',
                    'operational_hours': '08:00 - 16:00',
                    'built_year': 2010,
                    'last_renovation': '2020-01-01',
                    'is_public': True,
                    'image': None
                },
                {
                    'id': 2,
                    'name': 'Puskesmas Pembantu',
                    'type': 'KESEHATAN',
                    'condition': 'BAIK',
                    'location': 'Dusun 1',
                    'description': 'Fasilitas kesehatan masyarakat',
                    'capacity': '30 pasien',
                    'manager': 'Kepala Puskesmas',
                    'contact_person': 'Perawat',
                    'contact_phone': '081234567891',
                    'operational_hours': '08:00 - 15:00',
                    'built_year': 2015,
                    'last_renovation': '2021-06-01',
                    'is_public': True,
                    'image': None
                },
                {
                    'id': 3,
                    'name': 'SD Negeri Pulosarok',
                    'type': 'PENDIDIKAN',
                    'condition': 'BAIK',
                    'location': 'Dusun 2',
                    'description': 'Sekolah dasar negeri',
                    'capacity': '200 siswa',
                    'manager': 'Kepala Sekolah',
                    'contact_person': 'Kepala Sekolah',
                    'contact_phone': '081234567892',
                    'operational_hours': '07:00 - 12:00',
                    'built_year': 2005,
                    'last_renovation': '2019-08-01',
                    'is_public': True,
                    'image': None
                }
            ]
        
        return JsonResponse({'success': True, 'data': facilities_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ajax_history_data(request):
    """AJAX endpoint for history data"""
    try:
        history_list = VillageHistory.objects.filter(is_active=True).order_by('-is_featured', 'year_start')
        data = []
        
        for history in history_list:
            data.append({
                'id': history.id,
                'title': history.title,
                'summary': history.summary or '',
                'content': history.content,
                'history_type': history.history_type,
                'period_start': history.period_start or '',
                'period_end': history.period_end or '',
                'year_start': history.year_start,
                'year_end': history.year_end,
                'period_display': history.period_display,
                'source': history.source or '',
                'author': history.author or '',
                'is_featured': history.is_featured,
                'featured_image': history.featured_image.url if history.featured_image else None,
                'featured_image_caption': history.featured_image_caption or ''
            })
        
        if not data:
            data = [
                {
                    'id': 1,
                    'title': 'Sejarah Berdirinya Desa Pulosarok',
                    'summary': 'Desa Pulosarok didirikan pada tahun 1950 sebagai hasil pemekaran wilayah',
                    'content': 'Desa Pulosarok didirikan pada tahun 1950 sebagai hasil pemekaran wilayah dari desa induk. Pada awalnya, desa ini hanya terdiri dari beberapa keluarga yang bermukim di daerah ini...',
                    'history_type': 'FOUNDING',
                    'period_start': '1950',
                    'period_end': '1950',
                    'year_start': 1950,
                    'year_end': 1950,
                    'period_display': '1950',
                    'source': 'Arsip Desa',
                    'author': 'Tim Peneliti Sejarah',
                    'is_featured': True,
                    'featured_image': None,
                    'featured_image_caption': ''
                }
            ]
        
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ajax_gallery_data(request):
    """AJAX endpoint for gallery data"""
    try:
        village = VillageProfile.objects.filter(is_active=True).first()
        photos_data = []
        
        if village:
            photos = village.photos.filter(is_active=True).order_by('-is_featured', 'display_order')
            for photo in photos:
                photos_data.append({
                    'id': photo.id,
                    'title': photo.title,
                    'description': photo.description or '',
                    'photo_type': photo.photo_type,
                    'photographer': photo.photographer or '',
                    'photo_date': photo.photo_date.strftime('%Y-%m-%d') if photo.photo_date else None,
                    'location': photo.location or '',
                    'is_featured': photo.is_featured,
                    'display_order': photo.display_order,
                    'image': photo.image.url if photo.image else None
                })
        
        if not photos_data:
            photos_data = [
                {
                    'id': 1,
                    'title': 'Kantor Desa Pulosarok',
                    'description': 'Gedung kantor desa yang baru direnovasi',
                    'photo_type': 'PEMERINTAHAN',
                    'photographer': 'Tim Dokumentasi',
                    'photo_date': '2023-01-15',
                    'location': 'Pusat Desa',
                    'is_featured': True,
                    'display_order': 1,
                    'image': None
                },
                {
                    'id': 2,
                    'title': 'Pasar Tradisional',
                    'description': 'Pasar tradisional yang ramai dikunjungi warga',
                    'photo_type': 'EKONOMI',
                    'photographer': 'Tim Dokumentasi',
                    'photo_date': '2023-02-10',
                    'location': 'Dusun 1',
                    'is_featured': False,
                    'display_order': 2,
                    'image': None
                }
            ]
        
        return JsonResponse({'success': True, 'data': photos_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})