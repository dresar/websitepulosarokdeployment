from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from PIL import Image
import json
import os
import io

from .models import (
    VillageProfile, VillageGeography, VillageDemography, 
    VillageOfficial, VillageFacility, VillageHistory, 
    VillagePhoto, VillageStatistic, VillageHistoryPhoto,
    VillageProfilePageHeader
)
# # from references.models import Penduduk  # COMMENTED OUT - references app disabled  # COMMENTED OUT - references app disabled
# Using letters app models instead
try:
    from letters.models import Penduduk  # COMMENTED OUT - references app disabled
except ImportError:
    Penduduk  # COMMENTED OUT - references app disabled = None

# Temporary Penduduk model for village_profile app
class Penduduk(models.Model):
    nama = models.CharField(max_length=200)
    nik = models.CharField(max_length=16, unique=True)
    alamat = models.TextField(blank=True)
    telepon = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Penduduk'
        verbose_name_plural = 'Penduduk'
    
    def __str__(self):
        return self.nama


def is_admin(user):
    """Check if user is admin or superuser"""
    return user.is_authenticated and (user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists())


# ==================== VILLAGE PROFILE DASHBOARD ====================
@login_required
@user_passes_test(is_admin)
def village_profile_dashboard(request):
    """Main dashboard for village profile management"""
    try:
        # Get village profile
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        # Get statistics
        stats = {
            'total_officials': VillageOfficial.objects.filter(village=village_profile, is_active=True).count() if village_profile else 0,
            'total_facilities': VillageFacility.objects.filter(village=village_profile, is_active=True).count() if village_profile else 0,
            'total_photos': VillagePhoto.objects.filter(village=village_profile, is_active=True).count() if village_profile else 0,
            'total_history': VillageHistory.objects.filter(is_active=True).count(),
            'has_geography': VillageGeography.objects.filter(village=village_profile).exists() if village_profile else False,
            'has_demography': VillageDemography.objects.filter(village=village_profile).exists() if village_profile else False,
        }
        
        # Get recent activities
        recent_activities = []
        if village_profile:
            recent_officials = VillageOfficial.objects.filter(village=village_profile).order_by('-created_at')[:3]
            recent_facilities = VillageFacility.objects.filter(village=village_profile).order_by('-created_at')[:3]
            recent_photos = VillagePhoto.objects.filter(village=village_profile).order_by('-created_at')[:3]
            
            for official in recent_officials:
                recent_activities.append({
                    'type': 'official',
                    'title': f'Perangkat Desa: {official.name}',
                    'date': official.created_at,
                    'action': 'Ditambahkan'
                })
            
            for facility in recent_facilities:
                recent_activities.append({
                    'type': 'facility',
                    'title': f'Fasilitas: {facility.name}',
                    'date': facility.created_at,
                    'action': 'Ditambahkan'
                })
            
            for photo in recent_photos:
                recent_activities.append({
                    'type': 'photo',
                    'title': f'Foto: {photo.title}',
                    'date': photo.created_at,
                    'action': 'Ditambahkan'
                })
        
        # Sort by date
        recent_activities.sort(key=lambda x: x['date'], reverse=True)
        recent_activities = recent_activities[:10]
        
        context = {
            'page_title': 'Dashboard Profil Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'dashboard',
            'village_profile': village_profile,
            'stats': stats,
            'recent_activities': recent_activities,
        }
        
        return render(request, 'admin_panel/village_profile/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'admin_panel/village_profile/dashboard.html', {
            'page_title': 'Dashboard Profil Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'dashboard',
            'village_profile': None,
            'stats': {},
            'recent_activities': [],
        })


# ==================== GENERAL INFO MANAGEMENT ====================
@login_required
@user_passes_test(is_admin)
def village_profile_geography(request):
    """Geography management page"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        geography = village_profile.geography if village_profile else None
        
        context = {
            'village_profile': village_profile,
            'geography': geography,
            'page_title': 'Informasi Geografis Desa',
            'breadcrumbs': [
                {'name': 'Dashboard', 'url': reverse('village_profile:admin_dashboard')},
                {'name': 'Geografis', 'url': None}
            ]
        }
        
        return render(request, 'admin_panel/village_profile/geography.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading geography page: {str(e)}')
        return redirect('village_profile:admin_dashboard')


@login_required
@user_passes_test(is_admin)
def village_profile_demography(request):
    """Demography management page"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        demography = village_profile.demography if village_profile else None
        
        context = {
            'village_profile': village_profile,
            'demography': demography,
            'page_title': 'Informasi Demografi Desa',
            'breadcrumbs': [
                {'name': 'Dashboard', 'url': reverse('village_profile:admin_dashboard')},
                {'name': 'Demografi', 'url': None}
            ]
        }
        
        return render(request, 'admin_panel/village_profile/demography.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading demography page: {str(e)}')
        return redirect('village_profile:admin_dashboard')


@login_required
@user_passes_test(is_admin)
def village_profile_general_info(request):
    """Manage general village profile information"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        geography = None
        demography = None
        
        if village_profile:
            try:
                geography = village_profile.geography
            except VillageGeography.DoesNotExist:
                geography = None
            
            try:
                demography = village_profile.demography
            except VillageDemography.DoesNotExist:
                demography = None
        
        context = {
            'page_title': 'Informasi Umum Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'general_info',
            'village_profile': village_profile,
            'geography': geography,
            'demography': demography,
        }
        
        return render(request, 'admin_panel/village_profile/general_info.html', context)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'admin_panel/village_profile/general_info.html', {
            'page_title': 'Informasi Umum Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'general_info',
            'village_profile': None,
            'geography': None,
            'demography': None,
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def save_village_profile(request):
    """Save village profile data"""
    try:
        profile_id = request.POST.get('profile_id')
        
        if profile_id:
            # Update existing profile
            village_profile = get_object_or_404(VillageProfile, id=profile_id)
        else:
            # Create new profile
            village_profile = VillageProfile()
        
        # Validate required fields
        required_fields = ['name', 'district', 'regency', 'province']
        for field in required_fields:
            if not request.POST.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Field {field} wajib diisi'
                })
        
        # Update profile data
        village_profile.name = request.POST.get('name')
        village_profile.code = request.POST.get('code') or village_profile.name.lower().replace(' ', '_')
        village_profile.district = request.POST.get('district')
        village_profile.regency = request.POST.get('regency')
        village_profile.province = request.POST.get('province')
        village_profile.postal_code = request.POST.get('postal_code')
        
        # Handle established_date
        established_date = request.POST.get('established_date')
        if established_date:
            try:
                from datetime import datetime
                village_profile.established_date = datetime.strptime(established_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Format tanggal tidak valid'
                })
        else:
            village_profile.established_date = None
        
        # Handle area as decimal
        area = request.POST.get('area')
        if area:
            try:
                village_profile.area = float(area)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Format luas area tidak valid'
                })
        else:
            village_profile.area = None
        
        village_profile.description = request.POST.get('description')
        village_profile.profile_description = request.POST.get('profile_description')
        village_profile.vision = request.POST.get('vision')
        village_profile.mission = request.POST.get('mission')
        village_profile.phone = request.POST.get('phone')
        village_profile.email = request.POST.get('email')
        village_profile.website = request.POST.get('website')
        
        # Set as active if this is the first profile
        if not VillageProfile.objects.filter(is_active=True).exists():
            village_profile.is_active = True
        
        # Handle file uploads
        if 'logo' in request.FILES:
            village_profile.logo = request.FILES['logo']
        if 'profile_image' in request.FILES:
            village_profile.profile_image = request.FILES['profile_image']
        
        village_profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profil desa berhasil disimpan',
            'profile_id': village_profile.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== GEOGRAPHY MANAGEMENT ====================
@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def save_village_geography(request):
    """Save village geography data"""
    try:
        village_id = request.POST.get('village_id')
        if not village_id:
            return JsonResponse({
                'success': False,
                'message': 'ID desa tidak ditemukan'
            })
        
        village_profile = get_object_or_404(VillageProfile, id=village_id)
        
        # Validate required fields
        required_fields = ['latitude', 'longitude']
        for field in required_fields:
            if not request.POST.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Field {field} wajib diisi'
                })
        
        # Validate latitude and longitude
        try:
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
            
            if not (-90 <= latitude <= 90):
                return JsonResponse({
                    'success': False,
                    'message': 'Latitude harus antara -90 dan 90'
                })
            
            if not (-180 <= longitude <= 180):
                return JsonResponse({
                    'success': False,
                    'message': 'Longitude harus antara -180 dan 180'
                })
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Format koordinat tidak valid'
            })
        
        # Handle optional fields with proper type conversion
        altitude = request.POST.get('altitude')
        if altitude:
            try:
                altitude = int(altitude)
            except ValueError:
                altitude = None
        else:
            altitude = None
            
        rainfall = request.POST.get('rainfall')
        if rainfall:
            try:
                rainfall = int(rainfall)
            except ValueError:
                rainfall = None
        else:
            rainfall = None
            
        temp_min = request.POST.get('temperature_min')
        if temp_min:
            try:
                temp_min = int(temp_min)
            except ValueError:
                temp_min = None
        else:
            temp_min = None
            
        temp_max = request.POST.get('temperature_max')
        if temp_max:
            try:
                temp_max = int(temp_max)
            except ValueError:
                temp_max = None
        else:
            temp_max = None
        
        geography, created = VillageGeography.objects.get_or_create(
            village=village_profile,
            defaults={
                'latitude': latitude,
                'longitude': longitude,
                'altitude': altitude,
                'climate': request.POST.get('climate', ''),
                'rainfall': rainfall,
                'temperature_min': temp_min,
                'temperature_max': temp_max,
                'topography': request.POST.get('topography', ''),
                'soil_type': request.POST.get('soil_type', ''),
                'boundary_north': request.POST.get('boundary_north', ''),
                'boundary_south': request.POST.get('boundary_south', ''),
                'boundary_east': request.POST.get('boundary_east', ''),
                'boundary_west': request.POST.get('boundary_west', ''),
            }
        )
        
        if not created:
            # Update existing geography
            geography.latitude = latitude
            geography.longitude = longitude
            geography.altitude = altitude
            geography.climate = request.POST.get('climate', '')
            geography.rainfall = rainfall
            geography.temperature_min = temp_min
            geography.temperature_max = temp_max
            geography.topography = request.POST.get('topography', '')
            geography.soil_type = request.POST.get('soil_type', '')
            geography.boundary_north = request.POST.get('boundary_north', '')
            geography.boundary_south = request.POST.get('boundary_south', '')
            geography.boundary_east = request.POST.get('boundary_east', '')
            geography.boundary_west = request.POST.get('boundary_west', '')
            geography.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data geografi berhasil disimpan'
        })
        
    except VillageProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data desa tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== DEMOGRAPHY MANAGEMENT ====================
@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def save_village_demography(request):
    """Save village demography data"""
    try:
        village_id = request.POST.get('village_id')
        if not village_id:
            return JsonResponse({
                'success': False,
                'message': 'ID desa tidak ditemukan'
            })
        
        village_profile = get_object_or_404(VillageProfile, id=village_id)
        year = request.POST.get('year')
        
        if not year:
            return JsonResponse({
                'success': False,
                'message': 'Tahun wajib diisi'
            })
        
        # Validate year
        try:
            year = int(year)
            if year < 1900 or year > 2100:
                return JsonResponse({
                    'success': False,
                    'message': 'Tahun harus antara 1900 dan 2100'
                })
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Format tahun tidak valid'
            })
        
        # Validate required fields
        required_fields = ['total_population', 'male_population', 'female_population']
        for field in required_fields:
            if not request.POST.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Field {field} wajib diisi'
                })
        
        # Validate numeric fields
        numeric_fields = {
            'total_population': 'Total populasi',
            'male_population': 'Populasi laki-laki',
            'female_population': 'Populasi perempuan',
            'total_families': 'Total keluarga',
            'population_density': 'Kepadatan penduduk',
            'growth_rate': 'Tingkat pertumbuhan',
            'age_0_14': 'Usia 0-14 tahun',
            'age_15_64': 'Usia 15-64 tahun',
            'age_65_plus': 'Usia 65+ tahun',
            'education_none': 'Tidak sekolah',
            'education_elementary': 'SD',
            'education_junior': 'SMP',
            'education_senior': 'SMA',
            'education_higher': 'Perguruan tinggi',
            'employed': 'Bekerja',
            'unemployed': 'Tidak bekerja'
        }
        
        validated_data = {}
        for field, label in numeric_fields.items():
            value = request.POST.get(field)
            if value and value.strip():
                try:
                    if field in ['population_density', 'growth_rate']:
                        validated_data[field] = float(value)
                    else:
                        validated_data[field] = int(value)
                    if validated_data[field] < 0:
                        return JsonResponse({
                            'success': False,
                            'message': f'{label} tidak boleh negatif'
                        })
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': f'Format {label} tidak valid'
                    })
            else:
                validated_data[field] = 0
        
        # Validate population consistency (only if all values are provided)
        if validated_data['male_population'] > 0 and validated_data['female_population'] > 0 and validated_data['total_population'] > 0:
            if validated_data['male_population'] + validated_data['female_population'] != validated_data['total_population']:
                return JsonResponse({
                    'success': False,
                    'message': 'Jumlah laki-laki + perempuan harus sama dengan total populasi'
                })
        
        demography, created = VillageDemography.objects.get_or_create(
            village=village_profile,
            year=year,
            defaults=validated_data
        )
        
        if not created:
            # Update existing demography
            for field, value in validated_data.items():
                setattr(demography, field, value)
            demography.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data demografi berhasil disimpan'
        })
        
    except VillageProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data desa tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== OFFICIALS MANAGEMENT ====================
@login_required
@user_passes_test(is_admin)
def village_profile_officials(request):
    """Manage village officials"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        officials = []
        
        if village_profile:
            officials = VillageOfficial.objects.filter(village=village_profile, is_active=True).order_by('display_order', 'position')
        
        context = {
            'page_title': 'Struktur Organisasi Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'officials',
            'village_profile': village_profile,
            'officials': officials,
        }
        
        return render(request, 'admin_panel/village_profile/officials.html', context)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'admin_panel/village_profile/officials.html', {
            'page_title': 'Struktur Organisasi Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'officials',
            'village_profile': None,
            'officials': [],
        })


@login_required
@user_passes_test(is_admin)
def village_official_form(request, official_id=None):
    """Form for adding/editing village official"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        if not village_profile:
            messages.error(request, 'Profil desa tidak ditemukan')
            return redirect('village_profile:admin_dashboard')
        
        official = None
        if official_id:
            try:
                official = get_object_or_404(VillageOfficial, id=official_id, village=village_profile)
            except VillageOfficial.DoesNotExist:
                messages.error(request, 'Data perangkat desa tidak ditemukan')
                return redirect('village_profile:admin_officials')
        
        context = {
            'page_title': 'Form Perangkat Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'officials',
            'village_profile': village_profile,
            'official': official,
        }
        
        return render(request, 'admin_panel/village_profile/official_form.html', context)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('village_profile:admin_dashboard')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def save_village_official(request):
    """Save village official data"""
    try:
        official_id = request.POST.get('official_id')
        village_id = request.POST.get('village_id')
        
        if not village_id:
            return JsonResponse({
                'success': False,
                'message': 'ID desa tidak ditemukan'
            })
        
        village_profile = get_object_or_404(VillageProfile, id=village_id)
        
        # Validate required fields
        required_fields = ['name', 'position']
        for field in required_fields:
            if not request.POST.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Field {field} wajib diisi'
                })
        
        if official_id:
            # Update existing official
            official = get_object_or_404(VillageOfficial, id=official_id)
        else:
            # Create new official
            official = VillageOfficial(village=village_profile)
        
        # Update official data
        official.name = request.POST.get('name')
        official.position = request.POST.get('position')
        official.custom_position = request.POST.get('custom_position')
        
        # Personal information
        official.nik = request.POST.get('nik')
        official.birth_date = request.POST.get('birth_date')
        official.birth_place = request.POST.get('birth_place')
        official.gender = request.POST.get('gender')
        official.religion = request.POST.get('religion')
        official.education = request.POST.get('education')
        official.occupation = request.POST.get('occupation')
        official.marital_status = request.POST.get('marital_status')
        official.experience = request.POST.get('experience')
        
        # Contact information
        official.phone = request.POST.get('phone')
        official.mobile = request.POST.get('mobile')
        official.email = request.POST.get('email')
        official.address = request.POST.get('address')
        official.dusun = request.POST.get('dusun')
        official.lorong = request.POST.get('lorong')
        official.rt_number = request.POST.get('rt_number')
        official.rw_number = request.POST.get('rw_number')
        official.house_number = request.POST.get('house_number')
        official.postal_code = request.POST.get('postal_code')
        
        # Handle penduduk_id
        penduduk_id = request.POST.get('penduduk_id')
        if penduduk_id:
            try:
                # from references.models import Penduduk  # COMMENTED OUT - references app disabled
                # Using letters app models instead
                try:
                    from letters.models import Penduduk
                except ImportError:
                    Penduduk = None
                penduduk = get_object_or_404(Penduduk, id=penduduk_id)
                official.penduduk = penduduk
            except:
                pass
        
        # Handle dates
        start_date = request.POST.get('start_date')
        if start_date:
            try:
                from datetime import datetime
                official.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Format tanggal mulai jabatan tidak valid'
                })
        
        end_date = request.POST.get('end_date')
        if end_date:
            try:
                from datetime import datetime
                official.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Format tanggal akhir jabatan tidak valid'
                })
        else:
            official.end_date = None
        
        # Handle display order
        display_order = request.POST.get('display_order', 0)
        try:
            official.display_order = int(display_order)
        except ValueError:
            official.display_order = 0
        
        official.experience = request.POST.get('experience')
        
        # Handle birth date
        birth_date = request.POST.get('birth_date')
        if birth_date:
            try:
                from datetime import datetime
                official.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            except ValueError:
                official.birth_date = None
        else:
            official.birth_date = None
        
        # Handle checkbox for is_active
        official.is_active = 'is_active' in request.POST
        
        # Handle photo upload
        if 'photo' in request.FILES:
            official.photo = request.FILES['photo']
        elif request.POST.get('remove_photo') == 'on':
            official.photo = None
        
        official.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data perangkat desa berhasil disimpan',
            'official_id': official.id
        })
        
    except VillageProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data desa tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def delete_village_official(request):
    """Delete village official"""
    try:
        official_id = request.POST.get('official_id')
        if not official_id:
            return JsonResponse({
                'success': False,
                'message': 'ID perangkat desa tidak ditemukan'
            })
        
        official = get_object_or_404(VillageOfficial, id=official_id)
        official_name = official.name
        official.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data perangkat desa {official_name} berhasil dihapus'
        })
        
    except VillageOfficial.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data perangkat desa tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== HISTORY MANAGEMENT ====================
@login_required
@user_passes_test(is_admin)
def village_profile_history(request):
    """Manage village history"""
    try:
        history_list = VillageHistory.objects.filter(is_active=True).order_by('-is_featured', 'year_start')
        
        context = {
            'page_title': 'Sejarah Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'history',
            'history_list': history_list,
        }
        
        return render(request, 'admin_panel/village_profile/history.html', context)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'admin_panel/village_profile/history.html', {
            'page_title': 'Sejarah Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'history',
            'history_list': [],
        })


@login_required
@user_passes_test(is_admin)
def history_detail_view(request, history_id):
    """View history detail"""
    try:
        history = get_object_or_404(VillageHistory, id=history_id, is_active=True)
        
        # Increment view count
        history.view_count += 1
        history.save(update_fields=['view_count'])
        
        context = {
            'page_title': f'Detail Sejarah - {history.title}',
            'active_menu': 'village_profile',
            'active_submenu': 'history',
            'history': history,
        }
        
        return render(request, 'admin_panel/village_profile/history_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('village_profile:admin_history')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def save_village_history(request):
    """Save village history data"""
    try:
        history_id = request.POST.get('history_id')
        
        if history_id:
            # Update existing history
            history = get_object_or_404(VillageHistory, id=history_id)
        else:
            # Create new history
            history = VillageHistory()
        
        # Update history data
        history.title = request.POST.get('title')
        history.summary = request.POST.get('summary')
        history.content = request.POST.get('content')
        history.history_type = request.POST.get('history_type')
        history.period_start = request.POST.get('period_start')
        history.period_end = request.POST.get('period_end')
        history.year_start = request.POST.get('year_start') or None
        history.year_end = request.POST.get('year_end') or None
        history.source = request.POST.get('source')
        history.author = request.POST.get('author')
        history.is_featured = request.POST.get('is_featured') == 'true'
        
        # Handle featured image upload
        if 'featured_image' in request.FILES:
            history.featured_image = request.FILES['featured_image']
        elif request.POST.get('remove_featured_image') == 'on':
            history.featured_image = None
        
        history.featured_image_caption = request.POST.get('featured_image_caption')
        history.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data sejarah desa berhasil disimpan',
            'history_id': history.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def delete_village_history(request):
    """Delete village history"""
    try:
        history_id = request.POST.get('history_id')
        if not history_id:
            return JsonResponse({
                'success': False,
                'message': 'ID sejarah tidak ditemukan'
            })
        
        history = get_object_or_404(VillageHistory, id=history_id)
        history_title = history.title
        history.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data sejarah "{history_title}" berhasil dihapus'
        })
        
    except VillageHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data sejarah tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== FACILITIES MANAGEMENT ====================
@login_required
@user_passes_test(is_admin)
def village_profile_facilities(request):
    """Manage village facilities"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        facilities = []
        
        if village_profile:
            facilities = VillageFacility.objects.filter(village=village_profile, is_active=True).order_by('type', 'name')
        
        context = {
            'page_title': 'Fasilitas Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'facilities',
            'village_profile': village_profile,
            'facilities': facilities,
        }
        
        return render(request, 'admin_panel/village_profile/facilities.html', context)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'admin_panel/village_profile/facilities.html', {
            'page_title': 'Fasilitas Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'facilities',
            'village_profile': None,
            'facilities': [],
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def save_village_facility(request):
    """Save village facility"""
    try:
        facility_id = request.POST.get('facility_id')
        village_id = request.POST.get('village_id')
        
        if not village_id:
            return JsonResponse({
                'success': False,
                'message': 'ID desa tidak ditemukan'
            })
        
        village_profile = get_object_or_404(VillageProfile, id=village_id)
        
        # Validate required fields
        required_fields = ['name', 'type', 'condition', 'location']
        for field in required_fields:
            if not request.POST.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Field {field} wajib diisi'
                })
        
        if facility_id:
            # Update existing facility
            facility = get_object_or_404(VillageFacility, id=facility_id)
        else:
            # Create new facility
            facility = VillageFacility(village=village_profile)
        
        # Update facility data
        facility.name = request.POST.get('name')
        facility.type = request.POST.get('type')
        facility.condition = request.POST.get('condition')
        facility.description = request.POST.get('description')
        facility.location = request.POST.get('location')
        facility.capacity = request.POST.get('capacity')
        facility.manager = request.POST.get('manager')
        facility.contact_person = request.POST.get('contact_person')
        facility.contact_phone = request.POST.get('contact_phone')
        facility.operational_hours = request.POST.get('operational_hours')
        
        # Handle built_year
        built_year = request.POST.get('built_year')
        if built_year:
            try:
                facility.built_year = int(built_year)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Format tahun dibangun tidak valid'
                })
        else:
            facility.built_year = None
        
        # Handle last_renovation date
        last_renovation = request.POST.get('last_renovation')
        if last_renovation:
            try:
                from datetime import datetime
                facility.last_renovation = datetime.strptime(last_renovation, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Format tanggal renovasi terakhir tidak valid'
                })
        else:
            facility.last_renovation = None
        
        facility.is_public = request.POST.get('is_public', 'true').lower() == 'true'
        facility.is_active = request.POST.get('is_active', 'true').lower() == 'true'
        
        # Handle image upload
        if 'image' in request.FILES:
            facility.image = request.FILES['image']
        elif request.POST.get('remove_image') == 'on':
            facility.image = None
        
        facility.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Fasilitas desa berhasil disimpan',
            'facility_id': facility.id
        })
        
    except VillageProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data desa tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def delete_village_facility(request):
    """Delete village facility"""
    try:
        facility_id = request.POST.get('facility_id')
        if not facility_id:
            return JsonResponse({
                'success': False,
                'message': 'ID fasilitas tidak ditemukan'
            })
        
        facility = get_object_or_404(VillageFacility, id=facility_id)
        facility_name = facility.name
        facility.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Fasilitas {facility_name} berhasil dihapus'
        })
        
    except VillageFacility.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data fasilitas tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== GALLERY MANAGEMENT ====================
@login_required
@user_passes_test(is_admin)
def village_profile_gallery(request):
    """Manage village photo gallery"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        photos = []
        categories = []
        
        if village_profile:
            photos = VillagePhoto.objects.filter(village=village_profile, is_active=True).order_by('-is_featured', 'display_order')
            categories = VillagePhoto.objects.filter(village=village_profile, is_active=True).values_list('photo_type', flat=True).distinct()
        
        context = {
            'page_title': 'Galeri Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'gallery',
            'village_profile': village_profile,
            'gallery_items': photos,
            'categories': categories,
        }
        
        return render(request, 'admin_panel/village_profile/gallery.html', context)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return render(request, 'admin_panel/village_profile/gallery.html', {
            'page_title': 'Galeri Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'gallery',
            'village_profile': None,
            'gallery_items': [],
            'categories': [],
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def save_village_photo(request):
    """Save village photo"""
    try:
        photo_id = request.POST.get('photo_id')
        village_profile = get_object_or_404(VillageProfile, id=request.POST.get('village_id'))
        
        if photo_id:
            # Update existing photo
            photo = get_object_or_404(VillagePhoto, id=photo_id)
        else:
            # Create new photo
            photo = VillagePhoto(village=village_profile)
        
        # Update photo data
        photo.title = request.POST.get('title')
        photo.description = request.POST.get('description')
        photo.photo_type = request.POST.get('photo_type')
        photo.photographer = request.POST.get('photographer')
        photo.photo_date = request.POST.get('photo_date') or None
        photo.location = request.POST.get('location')
        photo.is_featured = request.POST.get('is_featured') == 'true'
        photo.display_order = request.POST.get('display_order', 0)
        
        # Handle image upload
        if 'image' in request.FILES:
            photo.image = request.FILES['image']
        
        photo.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Foto desa berhasil disimpan',
            'photo_id': photo.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def delete_village_photo(request):
    """Delete village photo"""
    try:
        photo_id = request.POST.get('photo_id')
        if not photo_id:
            return JsonResponse({
                'success': False,
                'message': 'ID foto tidak ditemukan'
            })
        
        photo = get_object_or_404(VillagePhoto, id=photo_id)
        photo_title = photo.title
        
        # Delete the image file if it exists
        if photo.image:
            try:
                photo.image.delete(save=False)
            except:
                pass  # Continue even if file deletion fails
        
        photo.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Foto "{photo_title}" berhasil dihapus'
        })
        
    except VillagePhoto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data foto tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== TOGGLE STATUS FUNCTIONS ====================
@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def toggle_official_status(request):
    """Toggle official active status"""
    try:
        official_id = request.POST.get('official_id')
        if not official_id:
            return JsonResponse({
                'success': False,
                'message': 'ID perangkat desa tidak ditemukan'
            })
        
        official = get_object_or_404(VillageOfficial, id=official_id)
        official.is_active = not official.is_active
        official.save()
        
        status = 'diaktifkan' if official.is_active else 'dinonaktifkan'
        return JsonResponse({
            'success': True,
            'message': f'Perangkat desa {official.name} berhasil {status}',
            'is_active': official.is_active
        })
        
    except VillageOfficial.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data perangkat desa tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def toggle_facility_status(request):
    """Toggle facility active status"""
    try:
        facility_id = request.POST.get('facility_id')
        if not facility_id:
            return JsonResponse({
                'success': False,
                'message': 'ID fasilitas tidak ditemukan'
            })
        
        facility = get_object_or_404(VillageFacility, id=facility_id)
        facility.is_active = not facility.is_active
        facility.save()
        
        status = 'diaktifkan' if facility.is_active else 'dinonaktifkan'
        return JsonResponse({
            'success': True,
            'message': f'Fasilitas {facility.name} berhasil {status}',
            'is_active': facility.is_active
        })
        
    except VillageFacility.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data fasilitas tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def toggle_history_status(request):
    """Toggle history active status"""
    try:
        history_id = request.POST.get('history_id')
        if not history_id:
            return JsonResponse({
                'success': False,
                'message': 'ID sejarah tidak ditemukan'
            })
        
        history = get_object_or_404(VillageHistory, id=history_id)
        history.is_active = not history.is_active
        history.save()
        
        status = 'diaktifkan' if history.is_active else 'dinonaktifkan'
        return JsonResponse({
            'success': True,
            'message': f'Sejarah "{history.title}" berhasil {status}',
            'is_active': history.is_active
        })
        
    except VillageHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data sejarah tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def toggle_photo_status(request):
    """Toggle photo active status"""
    try:
        photo_id = request.POST.get('photo_id')
        if not photo_id:
            return JsonResponse({
                'success': False,
                'message': 'ID foto tidak ditemukan'
            })
        
        photo = get_object_or_404(VillagePhoto, id=photo_id)
        photo.is_active = not photo.is_active
        photo.save()
        
        status = 'diaktifkan' if photo.is_active else 'dinonaktifkan'
        return JsonResponse({
            'success': True,
            'message': f'Foto "{photo.title}" berhasil {status}',
            'is_active': photo.is_active
        })
        
    except VillagePhoto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data foto tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== DISPLAY ORDER FUNCTIONS ====================
@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def update_officials_order(request):
    """Update officials display order"""
    try:
        orders = request.POST.get('orders')
        if not orders:
            return JsonResponse({
                'success': False,
                'message': 'Data urutan tidak ditemukan'
            })
        
        import json
        order_data = json.loads(orders)
        
        for item in order_data:
            official_id = item.get('id')
            display_order = item.get('order')
            
            if official_id and display_order is not None:
                try:
                    official = VillageOfficial.objects.get(id=official_id)
                    official.display_order = int(display_order)
                    official.save()
                except VillageOfficial.DoesNotExist:
                    continue
        
        return JsonResponse({
            'success': True,
            'message': 'Urutan perangkat desa berhasil diperbarui'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Format data urutan tidak valid'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def update_photos_order(request):
    """Update photos display order"""
    try:
        orders = request.POST.get('orders')
        if not orders:
            return JsonResponse({
                'success': False,
                'message': 'Data urutan tidak ditemukan'
            })
        
        import json
        order_data = json.loads(orders)
        
        for item in order_data:
            photo_id = item.get('id')
            display_order = item.get('order')
            
            if photo_id and display_order is not None:
                try:
                    photo = VillagePhoto.objects.get(id=photo_id)
                    photo.display_order = int(display_order)
                    photo.save()
                except VillagePhoto.DoesNotExist:
                    continue
        
        return JsonResponse({
            'success': True,
            'message': 'Urutan foto galeri berhasil diperbarui'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Format data urutan tidak valid'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== BULK OPERATIONS ====================
@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def bulk_delete_officials(request):
    """Bulk delete officials"""
    try:
        official_ids = request.POST.getlist('official_ids[]')
        if not official_ids:
            return JsonResponse({
                'success': False,
                'message': 'Tidak ada data yang dipilih'
            })
        
        deleted_count = 0
        for official_id in official_ids:
            try:
                official = VillageOfficial.objects.get(id=official_id)
                official.delete()
                deleted_count += 1
            except VillageOfficial.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} perangkat desa berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def bulk_delete_facilities(request):
    """Bulk delete facilities"""
    try:
        facility_ids = request.POST.getlist('facility_ids[]')
        if not facility_ids:
            return JsonResponse({
                'success': False,
                'message': 'Tidak ada data yang dipilih'
            })
        
        deleted_count = 0
        for facility_id in facility_ids:
            try:
                facility = VillageFacility.objects.get(id=facility_id)
                facility.delete()
                deleted_count += 1
            except VillageFacility.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} fasilitas berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def bulk_toggle_officials_status(request):
    """Bulk toggle officials status"""
    try:
        official_ids = request.POST.getlist('official_ids[]')
        action = request.POST.get('action')  # 'activate' or 'deactivate'
        
        if not official_ids:
            return JsonResponse({
                'success': False,
                'message': 'Tidak ada data yang dipilih'
            })
        
        if action not in ['activate', 'deactivate']:
            return JsonResponse({
                'success': False,
                'message': 'Aksi tidak valid'
            })
        
        is_active = action == 'activate'
        updated_count = 0
        
        for official_id in official_ids:
            try:
                official = VillageOfficial.objects.get(id=official_id)
                official.is_active = is_active
                official.save()
                updated_count += 1
            except VillageOfficial.DoesNotExist:
                continue
        
        status = 'diaktifkan' if is_active else 'dinonaktifkan'
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} perangkat desa berhasil {status}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== API ENDPOINTS ====================
@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_village_profile_data(request):
    """API endpoint for village profile data"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        if not village_profile:
            return JsonResponse({
                'success': False,
                'message': 'Tidak ada profil desa yang aktif'
            })
        
        data = {
            'id': village_profile.id,
            'name': village_profile.name,
            'code': village_profile.code,
            'district': village_profile.district,
            'regency': village_profile.regency,
            'province': village_profile.province,
            'postal_code': village_profile.postal_code,
            'established_date': village_profile.established_date.strftime('%Y-%m-%d') if village_profile.established_date else None,
            'area': str(village_profile.area),
            'description': village_profile.description,
            'profile_description': village_profile.profile_description,
            'vision': village_profile.vision,
            'mission': village_profile.mission,
            'phone': village_profile.phone,
            'email': village_profile.email,
            'website': village_profile.website,
            'logo': village_profile.logo.url if village_profile.logo else None,
            'profile_image': village_profile.profile_image.url if village_profile.profile_image else None,
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_get_official(request):
    """API endpoint to get specific official data"""
    try:
        official_id = request.GET.get('id')
        if not official_id:
            return JsonResponse({
                'success': False,
                'message': 'ID perangkat desa tidak ditemukan'
            })
        
        official = get_object_or_404(VillageOfficial, id=official_id)
        
        data = {
            'id': official.id,
            'name': official.name,
            'position': official.position,
            'custom_position': official.custom_position or '',
            'education': official.education or '',
            'phone': official.phone or '',
            'email': official.email or '',
            'address': official.address or '',
            'start_date': official.start_date.strftime('%Y-%m-%d') if official.start_date else None,
            'end_date': official.end_date.strftime('%Y-%m-%d') if official.end_date else None,
            'display_order': official.display_order,
            'experience': official.experience or '',
            'photo': official.photo.url if official.photo else None,
            'is_active': official.is_active
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except VillageOfficial.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data perangkat desa tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_get_facility(request):
    """API endpoint to get specific facility data"""
    try:
        facility_id = request.GET.get('id')
        if not facility_id:
            return JsonResponse({
                'success': False,
                'message': 'ID fasilitas tidak ditemukan'
            })
        
        facility = get_object_or_404(VillageFacility, id=facility_id)
        
        data = {
            'id': facility.id,
            'name': facility.name,
            'type': facility.type,
            'condition': facility.condition,
            'description': facility.description or '',
            'location': facility.location,
            'capacity': facility.capacity or '',
            'manager': facility.manager or '',
            'contact_person': facility.contact_person or '',
            'contact_phone': facility.contact_phone or '',
            'operational_hours': facility.operational_hours or '',
            'built_year': facility.built_year,
            'last_renovation': facility.last_renovation.strftime('%Y-%m-%d') if facility.last_renovation else None,
            'is_public': facility.is_public,
            'image': facility.image.url if facility.image else None,
            'is_active': facility.is_active
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except VillageFacility.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data fasilitas tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_get_history(request):
    """API endpoint to get specific history data"""
    try:
        history_id = request.GET.get('id')
        if not history_id:
            return JsonResponse({
                'success': False,
                'message': 'ID sejarah tidak ditemukan'
            })
        
        history = get_object_or_404(VillageHistory, id=history_id)
        
        data = {
            'id': history.id,
            'title': history.title,
            'summary': history.summary or '',
            'content': history.content,
            'history_type': history.history_type,
            'period_start': history.period_start or '',
            'period_end': history.period_end or '',
            'year_start': history.year_start,
            'year_end': history.year_end,
            'source': history.source or '',
            'author': history.author or '',
            'is_featured': history.is_featured,
            'featured_image': history.featured_image.url if history.featured_image else None,
            'featured_image_caption': history.featured_image_caption or ''
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except VillageHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data sejarah tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_get_photo(request):
    """API endpoint to get specific photo data"""
    try:
        photo_id = request.GET.get('id')
        if not photo_id:
            return JsonResponse({
                'success': False,
                'message': 'ID foto tidak ditemukan'
            })
        
        photo = get_object_or_404(VillagePhoto, id=photo_id)
        
        data = {
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
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except VillagePhoto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data foto tidak ditemukan'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_village_facilities(request):
    """API endpoint to get village facilities data"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        if not village_profile:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        facilities = village_profile.facilities.filter(is_active=True).order_by('type', 'name')
        
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


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_village_history(request):
    """API endpoint to get village history data"""
    try:
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


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_village_gallery(request):
    """API endpoint to get village gallery data"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        if not village_profile:
            return JsonResponse({
                'success': False,
                'message': 'Data desa tidak ditemukan'
            }, status=404)
        
        photos = village_profile.photos.filter(is_active=True).order_by('-is_featured', 'display_order', '-created_at')
        
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


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_village_officials(request):
    """API endpoint for village officials data"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        if not village_profile:
            return JsonResponse({
                'success': False,
                'message': 'Tidak ada profil desa yang aktif'
            })
        
        # Get filter parameters
        search = request.GET.get('search', '')
        position = request.GET.get('position', '')
        status = request.GET.get('status', '')
        
        # Base queryset
        officials = VillageOfficial.objects.filter(village=village_profile).order_by('display_order', 'position')
        
        # Apply filters
        if search:
            officials = officials.filter(
                Q(name__icontains=search) | 
                Q(nik__icontains=search) |
                Q(phone__icontains=search)
            )
        
        if position:
            officials = officials.filter(position=position)
        
        if status:
            if status == 'aktif':
                officials = officials.filter(is_active=True)
            elif status == 'non_aktif':
                officials = officials.filter(is_active=False)
        
        data = []
        for official in officials:
            data.append({
                'id': official.id,
                'name': official.name,
                'position': official.position,
                'custom_position': official.custom_position,
                'position_display': official.position_display,
                'education': official.education,
                'phone': official.phone,
                'email': official.email,
                'address': official.address,
                'start_date': official.start_date.strftime('%Y-%m-%d') if official.start_date else None,
                'end_date': official.end_date.strftime('%Y-%m-%d') if official.end_date else None,
                'photo': official.photo.url if official.photo else None,
                'display_order': official.display_order,
                'experience': official.experience,
                'nik': official.nik,
                'is_active': official.is_active,
                'gaji_pokok': float(official.gaji_pokok) if official.gaji_pokok else None,
                'tunjangan': float(official.tunjangan) if official.tunjangan else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_village_facilities(request):
    """API endpoint for village facilities data"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        if not village_profile:
            return JsonResponse({
                'success': False,
                'message': 'Tidak ada profil desa yang aktif'
            })
        
        facilities = VillageFacility.objects.filter(village=village_profile, is_active=True).order_by('type', 'name')
        
        data = []
        for facility in facilities:
            data.append({
                'id': facility.id,
                'name': facility.name,
                'type': facility.type,
                'condition': facility.condition,
                'description': facility.description,
                'location': facility.location,
                'capacity': facility.capacity,
                'manager': facility.manager,
                'contact_person': facility.contact_person,
                'contact_phone': facility.contact_phone,
                'operational_hours': facility.operational_hours,
                'built_year': facility.built_year,
                'last_renovation': facility.last_renovation.strftime('%Y-%m-%d') if facility.last_renovation else None,
                'is_public': facility.is_public,
                'image': facility.image.url if facility.image else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_village_history(request):
    """API endpoint for village history data"""
    try:
        history_list = VillageHistory.objects.filter(is_active=True).order_by('-is_featured', 'year_start')
        
        data = []
        for history in history_list:
            data.append({
                'id': history.id,
                'title': history.title,
                'summary': history.summary,
                'content': history.content,
                'history_type': history.history_type,
                'period_start': history.period_start,
                'period_end': history.period_end,
                'year_start': history.year_start,
                'year_end': history.year_end,
                'source': history.source,
                'author': history.author,
                'is_featured': history.is_featured,
                'featured_image': history.featured_image.url if history.featured_image else None,
                'featured_image_caption': history.featured_image_caption,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_village_gallery(request):
    """API endpoint for village gallery data"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        if not village_profile:
            return JsonResponse({
                'success': False,
                'message': 'Tidak ada profil desa yang aktif'
            })
        
        photos = VillagePhoto.objects.filter(village=village_profile, is_active=True).order_by('-is_featured', 'display_order')
        
        data = []
        for photo in photos:
            data.append({
                'id': photo.id,
                'title': photo.title,
                'description': photo.description,
                'photo_type': photo.photo_type,
                'photographer': photo.photographer,
                'photo_date': photo.photo_date.strftime('%Y-%m-%d') if photo.photo_date else None,
                'location': photo.location,
                'is_featured': photo.is_featured,
                'display_order': photo.display_order,
                'image': photo.image.url if photo.image else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_search_penduduk(request):
    """API endpoint for searching penduduk data"""
    try:
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 10))
        
        if len(query) < 2:
            return JsonResponse({
                'success': False,
                'message': 'Minimal 2 karakter untuk pencarian'
            })
        
        penduduk_list = Penduduk.objects.filter(
            Q(name__icontains=query) | Q(nik__icontains=query),
            is_active=True,
            is_alive=True
        ).order_by('name')[:limit]
        
        results = []
        for penduduk in penduduk_list:
            results.append({
                'id': penduduk.id,
                'name': penduduk.name,
                'nik': penduduk.nik,
                'birth_date': penduduk.birth_date.strftime('%Y-%m-%d') if penduduk.birth_date else None,
                'birth_place': penduduk.birth_place or '',
                'phone': penduduk.phone_number or '',
                'mobile': penduduk.mobile_number or '',
                'email': penduduk.email or '',
                'address': penduduk.address,
                'occupation': penduduk.occupation or '',
                'education': penduduk.get_education_display() if penduduk.education else '',
                'religion': penduduk.get_religion_display() if penduduk.religion else '',
                'gender': penduduk.get_gender_display() if penduduk.gender else '',
                'marital_status': penduduk.get_marital_status_display() if penduduk.marital_status else '',
                'dusun': penduduk.dusun.name if penduduk.dusun else '',
                'lorong': penduduk.lorong.nama_lorong if penduduk.lorong else '',
                'rt_number': penduduk.rt_number or '',
                'rw_number': penduduk.rw_number or '',
                'house_number': penduduk.house_number or '',
                'postal_code': penduduk.postal_code or '',
                'photo': penduduk.photo.url if penduduk.photo else None,
            })
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_get_penduduk_detail(request, penduduk_id):
    """API to get detailed penduduk data"""
    try:
        penduduk = get_object_or_404(Penduduk, id=penduduk_id, is_active=True, is_alive=True)
        
        data = {
            'id': penduduk.id,
            'name': penduduk.name,
            'nik': penduduk.nik,
            'birth_date': penduduk.birth_date.strftime('%Y-%m-%d') if penduduk.birth_date else None,
            'birth_place': penduduk.birth_place or '',
            'phone': penduduk.phone_number or '',
            'mobile': penduduk.mobile_number or '',
            'email': penduduk.email or '',
            'address': penduduk.address,
            'occupation': penduduk.occupation or '',
            'education': penduduk.get_education_display() if penduduk.education else '',
            'religion': penduduk.get_religion_display() if penduduk.religion else '',
            'gender': penduduk.get_gender_display() if penduduk.gender else '',
            'marital_status': penduduk.get_marital_status_display() if penduduk.marital_status else '',
            'dusun': penduduk.dusun.name if penduduk.dusun else '',
            'lorong': penduduk.lorong.nama_lorong if penduduk.lorong else '',
            'rt_number': penduduk.rt_number or '',
            'rw_number': penduduk.rw_number or '',
            'house_number': penduduk.house_number or '',
            'postal_code': penduduk.postal_code or '',
            'photo': penduduk.photo.url if penduduk.photo else None,
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== STATISTICS API ====================
@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def api_village_statistics(request):
    """API endpoint for village statistics"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        
        if not village_profile:
            return JsonResponse({
                'success': False,
                'message': 'Tidak ada profil desa yang aktif'
            })
        
        # Get latest statistics
        latest_stats = VillageStatistic.objects.filter(village=village_profile).order_by('-year').first()
        
        # Get demography data
        demography = None
        try:
            demography = village_profile.demography
        except VillageDemography.DoesNotExist:
            pass
        
        # Get counts
        officials_count = VillageOfficial.objects.filter(village=village_profile, is_active=True).count()
        facilities_count = VillageFacility.objects.filter(village=village_profile, is_active=True).count()
        photos_count = VillagePhoto.objects.filter(village=village_profile, is_active=True).count()
        history_count = VillageHistory.objects.filter(is_active=True).count()
        
        data = {
            'officials_count': officials_count,
            'facilities_count': facilities_count,
            'photos_count': photos_count,
            'history_count': history_count,
            'has_geography': VillageGeography.objects.filter(village=village_profile).exists(),
            'has_demography': demography is not None,
            'demography_year': demography.year if demography else None,
            'total_population': demography.total_population if demography else 0,
            'total_families': demography.total_families if demography else 0,
            'population_density': float(demography.population_density) if demography else 0,
        }
        
        if latest_stats:
            data.update({
                'total_dusun': latest_stats.total_dusun,
                'total_rt': latest_stats.total_rt,
                'total_rw': latest_stats.total_rw,
                'total_umkm': latest_stats.total_umkm,
                'poverty_rate': float(latest_stats.poverty_rate),
                'unemployment_rate': float(latest_stats.unemployment_rate),
                'road_length': float(latest_stats.road_length),
                'electricity_coverage': float(latest_stats.electricity_coverage),
                'water_coverage': float(latest_stats.water_coverage),
                'stats_year': latest_stats.year,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


# ==================== EXPORT FUNCTIONS ====================
@login_required
@user_passes_test(is_admin)
def export_village_data(request):
    """Export all village data"""
    try:
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="village_profile_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Module', 'Data', 'Status'])
        
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        if village_profile:
            writer.writerow(['Profile', village_profile.name, 'Active'])
            
            # Officials
            officials = VillageOfficial.objects.filter(village=village_profile, is_active=True)
            for official in officials:
                writer.writerow(['Official', official.name, official.get_position_display()])
            
            # Facilities
            facilities = VillageFacility.objects.filter(village=village_profile, is_active=True)
            for facility in facilities:
                writer.writerow(['Facility', facility.name, facility.get_condition_display()])
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
def export_officials(request):
    """Export officials data"""
    try:
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="village_officials.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Nama', 'Jabatan', 'Pendidikan', 'Telepon', 'Email', 'Mulai Jabatan'])
        
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        if village_profile:
            officials = VillageOfficial.objects.filter(village=village_profile, is_active=True)
            for official in officials:
                writer.writerow([
                    official.name,
                    official.position_display,
                    official.education or '',
                    official.phone or '',
                    official.email or '',
                    official.start_date.strftime('%Y-%m-%d') if official.start_date else ''
                ])
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
def export_facilities(request):
    """Export facilities data"""
    try:
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="village_facilities.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Nama', 'Jenis', 'Kondisi', 'Lokasi', 'Kapasitas', 'Pengelola'])
        
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        if village_profile:
            facilities = VillageFacility.objects.filter(village=village_profile, is_active=True)
            for facility in facilities:
                writer.writerow([
                    facility.name,
                    facility.get_type_display(),
                    facility.get_condition_display(),
                    facility.location,
                    facility.capacity or '',
                    facility.manager or ''
                ])
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
def export_history(request):
    """Export history data"""
    try:
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="village_history.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Judul', 'Jenis', 'Periode', 'Ringkasan', 'Penulis', 'Sumber'])
        
        history_list = VillageHistory.objects.filter(is_active=True)
        for history in history_list:
            writer.writerow([
                history.title,
                history.get_history_type_display(),
                history.period_display,
                history.summary or '',
                history.author or '',
                history.source or ''
            ])
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })
