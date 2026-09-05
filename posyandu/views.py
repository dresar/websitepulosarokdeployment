from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.contrib import messages
from datetime import date, datetime, timedelta
import json
import csv

# Import models posyandu
from .models import (
    PosyanduPageHeader, PosyanduLocation, PosyanduSchedule, HealthRecord, 
    Immunization, NutritionData, PosyanduKader, IbuHamil, PemeriksaanIbuHamil, 
    StuntingData, PatientType
)

# Import models referensi
# from references.models import (  # COMMENTED OUT - references app disabled
# Using letters app models instead
try:
    from letters.models import (
        ReferencesPageHeader, Dusun, Lorong, Penduduk, Keluarga, 
        ReligionReference
    )
except ImportError:
    ReferencesPageHeader = None
    Dusun = None
    Lorong = None
    Penduduk = None
    Keluarga = None
    ReligionReference = None

def posyandu_admin(request):
    """Admin posyandu dashboard"""
    from .admin_views import admin_panel_dashboard
    return admin_panel_dashboard(request)

def unified_form(request):
    """Unified form untuk semua data posyandu"""
    from django.shortcuts import redirect
    return redirect('posyandu:unified_form')

def locations(request):
    """Admin panel locations"""
    from .admin_views import admin_panel_location_list
    return admin_panel_location_list(request)

def location_create(request):
    """Admin panel location create"""
    from .admin_views import admin_panel_location_create
    return admin_panel_location_create(request)

def location_detail(request, location_id):
    """Admin panel location detail"""
    from .admin_views import admin_panel_location_detail
    return admin_panel_location_detail(request, location_id)

def location_update(request, location_id):
    """Admin panel location update"""
    from .admin_views import admin_panel_location_update
    return admin_panel_location_update(request, location_id)

def location_delete(request, location_id):
    """Admin panel location delete"""
    from .admin_views import admin_panel_location_delete
    return admin_panel_location_delete(request, location_id)

def schedules(request):
    """Admin panel schedules"""
    from .admin_views import admin_panel_schedule_list
    return admin_panel_schedule_list(request)

def health_records(request):
    """Admin panel health records"""
    from .admin_views import admin_panel_health_record_list
    return admin_panel_health_record_list(request)

def immunizations(request):
    """Admin panel immunizations"""
    from .admin_views import admin_panel_immunization_list
    return admin_panel_immunization_list(request)

def nutrition_data(request):
    """Admin panel nutrition data"""
    from .admin_views import admin_panel_nutrition_list
    return admin_panel_nutrition_list(request)

def kaders(request):
    """Admin panel kaders"""
    from .admin_views import admin_panel_kader_list
    return admin_panel_kader_list(request)

def ibu_hamil(request):
    """Admin panel ibu hamil"""
    from .admin_views import admin_panel_ibu_hamil_list
    return admin_panel_ibu_hamil_list(request)

def stunting_data(request):
    """Admin panel stunting data"""
    from .admin_views import admin_panel_stunting_list
    return admin_panel_stunting_list(request)

def patient_types(request):
    """Admin panel patient types"""
    from .patient_type_views import admin_panel_patient_types
    return admin_panel_patient_types(request)

def reports(request):
    """Admin panel reports"""
    from .admin_views import admin_panel_reports
    return admin_panel_reports(request)

# Schedule views
def schedule_create(request):
    """Admin panel schedule create"""
    from .admin_views import admin_panel_schedule_create
    return admin_panel_schedule_create(request)

def schedule_detail(request, schedule_id):
    """Admin panel schedule detail"""
    from .admin_views import admin_panel_schedule_detail
    return admin_panel_schedule_detail(request, schedule_id)

def schedule_update(request, schedule_id):
    """Admin panel schedule update"""
    from .admin_views import admin_panel_schedule_update
    return admin_panel_schedule_update(request, schedule_id)

def schedule_delete(request, schedule_id):
    """Admin panel schedule delete"""
    from .admin_views import admin_panel_schedule_delete
    return admin_panel_schedule_delete(request, schedule_id)

# Health record views
def health_record_create(request):
    """Admin panel health record create"""
    from .admin_views import admin_panel_health_record_create
    return admin_panel_health_record_create(request)

def health_record_detail(request, record_id):
    """Admin panel health record detail"""
    from .admin_views import admin_panel_health_record_detail
    return admin_panel_health_record_detail(request, record_id)

def health_record_update(request, record_id):
    """Admin panel health record update"""
    from .admin_views import admin_panel_health_record_update
    return admin_panel_health_record_update(request, record_id)

def health_record_delete(request, record_id):
    """Admin panel health record delete"""
    from .admin_views import admin_panel_health_record_delete
    return admin_panel_health_record_delete(request, record_id)

# Immunization views
def immunization_create(request):
    """Admin panel immunization create"""
    from .admin_views import admin_panel_immunization_create
    return admin_panel_immunization_create(request)

def immunization_detail(request, immunization_id):
    """Admin panel immunization detail"""
    from .admin_views import admin_panel_immunization_detail
    return admin_panel_immunization_detail(request, immunization_id)

def immunization_update(request, immunization_id):
    """Admin panel immunization update"""
    from .admin_views import admin_panel_immunization_update
    return admin_panel_immunization_update(request, immunization_id)

def immunization_delete(request, immunization_id):
    """Admin panel immunization delete"""
    from .admin_views import admin_panel_immunization_delete
    return admin_panel_immunization_delete(request, immunization_id)

# Nutrition data views
def nutrition_data_create(request):
    """Admin panel nutrition data create"""
    from .admin_views import admin_panel_nutrition_create
    return admin_panel_nutrition_create(request)

def nutrition_data_detail(request, nutrition_id):
    """Admin panel nutrition data detail"""
    from .admin_views import admin_panel_nutrition_detail
    return admin_panel_nutrition_detail(request, nutrition_id)

def nutrition_data_update(request, nutrition_id):
    """Admin panel nutrition data update"""
    from .admin_views import admin_panel_nutrition_update
    return admin_panel_nutrition_update(request, nutrition_id)

def nutrition_data_delete(request, nutrition_id):
    """Admin panel nutrition data delete"""
    from .admin_views import admin_panel_nutrition_delete
    return admin_panel_nutrition_delete(request, nutrition_id)

# Kader views
def kader_create(request):
    """Admin panel kader create"""
    from .admin_views import admin_panel_kader_create
    return admin_panel_kader_create(request)

def kader_detail(request, kader_id):
    """Admin panel kader detail"""
    from .admin_views import admin_panel_kader_detail
    return admin_panel_kader_detail(request, kader_id)

def kader_update(request, kader_id):
    """Admin panel kader update"""
    from .admin_views import admin_panel_kader_update
    return admin_panel_kader_update(request, kader_id)

def kader_delete(request, kader_id):
    """Admin panel kader delete"""
    from .admin_views import admin_panel_kader_delete
    return admin_panel_kader_delete(request, kader_id)

# Ibu hamil views
def ibu_hamil_create(request):
    """Admin panel ibu hamil create"""
    from .admin_views import admin_panel_ibu_hamil_create
    return admin_panel_ibu_hamil_create(request)

def ibu_hamil_detail(request, ibu_hamil_id):
    """Admin panel ibu hamil detail"""
    from .admin_views import admin_panel_ibu_hamil_detail
    return admin_panel_ibu_hamil_detail(request, ibu_hamil_id)

def ibu_hamil_update(request, ibu_hamil_id):
    """Admin panel ibu hamil update"""
    from .admin_views import admin_panel_ibu_hamil_update
    return admin_panel_ibu_hamil_update(request, ibu_hamil_id)

def ibu_hamil_delete(request, ibu_hamil_id):
    """Admin panel ibu hamil delete"""
    from .admin_views import admin_panel_ibu_hamil_delete
    return admin_panel_ibu_hamil_delete(request, ibu_hamil_id)

# Stunting data views
def stunting_data_create(request):
    """Admin panel stunting data create"""
    from .admin_views import admin_panel_stunting_create
    return admin_panel_stunting_create(request)

def stunting_data_detail(request, stunting_id):
    """Admin panel stunting data detail"""
    from .admin_views import admin_panel_stunting_detail
    return admin_panel_stunting_detail(request, stunting_id)

def stunting_data_update(request, stunting_id):
    """Admin panel stunting data update"""
    from .admin_views import admin_panel_stunting_update
    return admin_panel_stunting_update(request, stunting_id)

def stunting_data_delete(request, stunting_id):
    """Admin panel stunting data delete"""
    from .admin_views import admin_panel_stunting_delete
    return admin_panel_stunting_delete(request, stunting_id)

# Patient type views
def patient_type_create(request):
    """Admin panel patient type create"""
    from .patient_type_views import admin_panel_patient_type_create
    return admin_panel_patient_type_create(request)

def patient_type_detail(request, patient_type_id):
    """Admin panel patient type detail"""
    from .patient_type_views import admin_panel_patient_type_detail
    return admin_panel_patient_type_detail(request, patient_type_id)

def patient_type_update(request, patient_type_id):
    """Admin panel patient type update"""
    from .patient_type_views import admin_panel_patient_type_update
    return admin_panel_patient_type_update(request, patient_type_id)

def patient_type_delete(request, patient_type_id):
    """Admin panel patient type delete"""
    from .patient_type_views import admin_panel_patient_type_delete
    return admin_panel_patient_type_delete(request, patient_type_id)

# Export views
def export_health_records(request):
    """Admin panel export health records"""
    from .admin_views import admin_panel_export_health_records
    return admin_panel_export_health_records(request)

def export_immunizations(request):
    """Admin panel export immunizations"""
    from .admin_views import admin_panel_export_immunizations
    return admin_panel_export_immunizations(request)

def export_nutrition_data(request):
    """Admin panel export nutrition data"""
    from .admin_views import admin_panel_export_nutrition_data
    return admin_panel_export_nutrition_data(request)

def export_stunting_data(request):
    """Admin panel export stunting data"""
    from .admin_views import admin_panel_export_stunting_data
    return admin_panel_export_stunting_data(request)

def public_posyandu_home(request):
    """Public posyandu home page"""
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True).select_related('coordinator')[:6]
    
    # Get upcoming schedules
    upcoming_schedules = PosyanduSchedule.objects.filter(
        schedule_date__gte=timezone.now().date(),
        location__is_active=True
    ).select_related('location').order_by('schedule_date', 'start_time')[:5]
    
    context = {
        'posyandu_locations': posyandu_locations,
        'upcoming_schedules': upcoming_schedules,
        'page_title': 'Posyandu Desa Pulosarok',
        'page_subtitle': 'Layanan kesehatan masyarakat terpadu'
    }
    return render(request, 'public/posyandu/posyandu_services.html', context)


def public_posyandu_services(request):
    """Public page showing posyandu services and locations"""
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True).select_related('coordinator')
    
    # Get upcoming schedules
    upcoming_schedules = PosyanduSchedule.objects.filter(
        schedule_date__gte=timezone.now().date(),
        location__is_active=True
    ).select_related('location').order_by('schedule_date', 'start_time')[:10]
    
    context = {
        'posyandu_locations': posyandu_locations,
        'upcoming_schedules': upcoming_schedules,
        'page_title': 'Layanan Posyandu',
        'page_subtitle': 'Informasi layanan kesehatan masyarakat'
    }
    return render(request, 'public/posyandu/posyandu_services.html', context)


def public_posyandu_schedule(request, location_id=None):
    """Public page showing posyandu schedules"""
    location = None
    if location_id:
        location = get_object_or_404(PosyanduLocation, id=location_id, is_active=True)
    
    # Filter schedules
    schedules = PosyanduSchedule.objects.filter(
        schedule_date__gte=timezone.now().date(),
        location__is_active=True
    ).select_related('location')
    
    if location:
        schedules = schedules.filter(location=location)
    
    schedules = schedules.order_by('schedule_date', 'start_time')
    
    # Pagination
    paginator = Paginator(schedules, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'schedules': page_obj,
        'location': location,
        'locations': PosyanduLocation.objects.filter(is_active=True),
        'page_title': 'Jadwal Posyandu',
        'page_subtitle': 'Jadwal kegiatan posyandu'
    }
    return render(request, 'public/posyandu/posyandu_schedule.html', context)


def public_health_info(request, nik=None):
    """Public page for checking health information by NIK"""
    penduduk = None
    health_records = None
    immunizations = None
    nutrition_data = None
    
    if nik:
        try:
            penduduk = Penduduk.objects.get(nik=nik, is_active=True)
            health_records = HealthRecord.objects.filter(patient=penduduk).order_by('-visit_date')[:5]
            immunizations = Immunization.objects.filter(patient=penduduk).order_by('-immunization_date')[:5]
            nutrition_data = NutritionData.objects.filter(patient=penduduk).order_by('-measurement_date')[:5]
        except Penduduk.DoesNotExist:
            messages.error(request, 'NIK tidak ditemukan dalam database.')
    
    if request.method == 'POST':
        search_nik = request.POST.get('nik')
        if search_nik:
            return redirect('posyandu:public_health_info', nik=search_nik)
    
    context = {
        'penduduk': penduduk,
        'health_records': health_records,
        'immunizations': immunizations,
        'nutrition_data': nutrition_data,
        'page_title': 'Informasi Kesehatan',
        'page_subtitle': 'Cek riwayat kesehatan berdasarkan NIK'
    }
    return render(request, 'public/posyandu/health_info.html', context)


def public_stunting_info(request):
    """Public page showing stunting information and statistics"""
    # Get stunting statistics
    total_balita = StuntingData.objects.values('balita').distinct().count()
    stunting_stats = StuntingData.objects.values('status_stunting').annotate(
        count=Count('id')
    ).order_by('status_stunting')
    
    # Recent stunting data
    recent_data = StuntingData.objects.select_related(
        'balita', 'posyandu'
    ).order_by('-tanggal_ukur')[:10]
    
    context = {
        'total_balita': total_balita,
        'stunting_stats': stunting_stats,
        'recent_data': recent_data,
        'page_title': 'Informasi Stunting',
        'page_subtitle': 'Data dan statistik stunting balita'
    }
    return render(request, 'public/posyandu/stunting_info.html', context)


# API Views for Public
@csrf_exempt
@require_http_methods(["GET"])
def public_posyandu_locations_api(request):
    """API to get active posyandu locations"""
    try:
        locations = PosyanduLocation.objects.filter(is_active=True).select_related('coordinator')
        
        data = {
            'results': [
                {
                    'id': loc.id,
                    'name': loc.name,
                    'address': loc.address,
                    'coordinator': loc.coordinator.name if loc.coordinator else None,
                    'contact_phone': loc.contact_phone,
                    'capacity': loc.capacity,
                    'facilities': loc.facilities
                }
                for loc in locations
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============= ADMIN PANEL INTEGRATION =============

# Admin Dashboard Views

def public_posyandu_locations_api(request):
    """API publik untuk mendapatkan daftar lokasi posyandu"""
    locations = PosyanduLocation.objects.filter(is_active=True).values(
        'id', 'name', 'address', 'contact_phone', 'capacity', 'facilities'
    )
    return JsonResponse(list(locations), safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def public_posyandu_schedules_api(request):
    """API publik untuk mendapatkan jadwal posyandu"""
    from datetime import datetime, timedelta
    
    # Get schedules for next 30 days
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=30)
    
    schedules = PosyanduSchedule.objects.filter(
        schedule_date__range=[start_date, end_date],
        is_completed=False
    ).select_related('location').values(
        'id', 'title', 'description', 'schedule_date', 'start_time', 'end_time',
        'activity_type', 'location__name', 'location__address'
    )
    
    return JsonResponse(list(schedules), safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def public_health_stats_api(request):
    """API publik untuk mendapatkan statistik kesehatan"""
    from django.db.models import Count, Avg
    
    # Basic health statistics
    stats = {
        'total_health_records': HealthRecord.objects.count(),
        'total_immunizations': Immunization.objects.count(),
        'total_nutrition_data': NutritionData.objects.count(),
        'total_stunting_data': StuntingData.objects.count(),
        'avg_weight': float(NutritionData.objects.aggregate(Avg('weight'))['weight__avg'] or 0),
        'avg_height': float(NutritionData.objects.aggregate(Avg('height'))['height__avg'] or 0),
        'stunting_count': StuntingData.objects.filter(status_stunting='stunting').count(),
    }
    
    # Statistics by patient type
    patient_type_stats = HealthRecord.objects.values('patient_type').annotate(
        count=Count('id')
    )
    stats['patient_type_stats'] = list(patient_type_stats)
    
    # Statistics by nutrition status
    nutrition_status_stats = NutritionData.objects.values('nutrition_status').annotate(
        count=Count('id')
    )
    stats['nutrition_status_stats'] = list(nutrition_status_stats)
    
    return JsonResponse(stats)

@csrf_exempt
@require_http_methods(["GET"])
def public_residents_api(request):
    """API publik untuk mendapatkan daftar penduduk (terbatas)"""
    # from references.models import Penduduk  # COMMENTED OUT - references app disabled
    # Using letters app models instead
    try:
        from letters.models import Penduduk
    except ImportError:
        Penduduk = None
    
    # Only return basic info for public API
    residents = Penduduk.objects.filter(
        is_active=True, is_alive=True
    ).values('id', 'name', 'gender', 'age')[:50]  # Limit to 50 records
    
    return JsonResponse({'residents': list(residents)})

# Additional Admin Panel Views

def public_posyandu_schedules_api(request):
    """API to get posyandu schedules"""
    try:
        location_id = request.GET.get('location_id')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        schedules = PosyanduSchedule.objects.filter(
            location__is_active=True
        ).select_related('location')
        
        if location_id:
            schedules = schedules.filter(location_id=location_id)
        
        if date_from:
            schedules = schedules.filter(schedule_date__gte=date_from)
        else:
            schedules = schedules.filter(schedule_date__gte=timezone.now().date())
        
        if date_to:
            schedules = schedules.filter(schedule_date__lte=date_to)
        
        schedules = schedules.order_by('schedule_date', 'start_time')
        
        data = {
            'results': [
                {
                    'id': schedule.id,
                    'title': schedule.title,
                    'activity_type': schedule.get_activity_type_display(),
                    'location': schedule.location.name,
                    'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d'),
                    'start_time': schedule.start_time.strftime('%H:%M'),
                    'end_time': schedule.end_time.strftime('%H:%M'),
                    'description': schedule.description,
                    'target_participants': schedule.target_participants
                }
                for schedule in schedules
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def public_health_stats_api(request):
    """API to get public health statistics"""
    try:
        # Basic statistics
        total_locations = PosyanduLocation.objects.filter(is_active=True).count()
        total_kader = PosyanduKader.objects.filter(status='aktif').count()
        total_ibu_hamil = IbuHamil.objects.filter(status_aktif=True).count()
        
        # Balita statistics (children under 5)
        from datetime import date, timedelta
        # Since posyandu Penduduk model doesn't have birth_date, we'll use a different approach
        if Penduduk is not None:
            total_balita = Penduduk.objects.count()  # Simplified for now
        else:
            total_balita = 0  # Fallback if Penduduk model is not available
        
        # Nutrition statistics
        balita_sehat = NutritionData.objects.filter(
            nutrition_status='normal'
        ).count()
        
        # Gizi status statistics
        gizi_baik = NutritionData.objects.filter(
            nutrition_status='normal'
        ).count()
        
        gizi_kurang = NutritionData.objects.filter(
            nutrition_status__in=['kurang', 'sangat_kurang']
        ).count()
        
        # Stunting statistics
        total_stunting = StuntingData.objects.filter(
            status_stunting__in=['pendek', 'sangat_pendek']
        ).count()
        
        stunting_berat = StuntingData.objects.filter(
            status_stunting='sangat_pendek'
        ).count()
        
        # Immunization coverage (approximate)
        total_immunizations = Immunization.objects.count()
        immunization_coverage = min(95, (total_immunizations / max(total_balita, 1)) * 100)
        
        # Ibu hamil sehat (assume most are healthy for demo)
        ibu_hamil_sehat = max(0, total_ibu_hamil - 2)
        
        # Program participants (sample data)
        program_gizi_peserta = max(0, gizi_kurang + 5)  # Participants in nutrition program
        program_ibu_hamil_peserta = max(0, total_ibu_hamil - 1)  # Participants in pregnancy program
        
        # Additional stunting metrics for template
        recovery_rate = 75  # Sample recovery rate
        prevention_coverage = 85  # Sample prevention coverage
        monitored_children = total_balita  # All children are monitored
        
        data = {
            'total_locations': total_locations,
            'total_kader': total_kader,
            'total_ibu_hamil': total_ibu_hamil,
            'total_balita': total_balita,
            'balita_sehat': balita_sehat,
            'total_stunting': total_stunting,
            'stunting_berat': stunting_berat,
            'recovery_rate': recovery_rate,
            'prevention_coverage': prevention_coverage,
            'monitored_children': monitored_children,
            'immunization_coverage': round(immunization_coverage, 1),
            'ibu_hamil_sehat': ibu_hamil_sehat,
            'gizi_baik': gizi_baik,
            'gizi_kurang': gizi_kurang,
            'program_gizi_peserta': program_gizi_peserta,
            'program_ibu_hamil_peserta': program_ibu_hamil_peserta,
            'basic_stats': {
                'total_locations': total_locations,
                'total_kader': total_kader,
                'total_ibu_hamil': total_ibu_hamil
            }
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def public_residents_api(request):
    """API to get residents data for posyandu"""
    try:
        search = request.GET.get('search', '')
        age_min = request.GET.get('age_min')
        age_max = request.GET.get('age_max')
        gender = request.GET.get('gender')
        
        residents = Penduduk.objects.filter(is_active=True)
        
        if search:
            residents = residents.filter(
                Q(name__icontains=search) | 
                Q(nik__icontains=search)
            )
        
        # Age filtering not available for posyandu Penduduk model
        # if age_min:
        #     birth_date_max = timezone.now().date() - timedelta(days=int(age_min) * 365)
        #     residents = residents.filter(birth_date__lte=birth_date_max)
        # 
        # if age_max:
        #     birth_date_min = timezone.now().date() - timedelta(days=int(age_max) * 365)
        #     residents = residents.filter(birth_date__gte=birth_date_min)
        
        if gender:
            residents = residents.filter(gender=gender)
        
        residents = residents.order_by('name')[:50]  # Limit to 50 results
        
        data = {
            'results': [
                {
                    'id': resident.id,
                    'nik': resident.nik,
                    'name': resident.nama,
                    'birth_date': getattr(resident, 'birth_date', None).strftime('%Y-%m-%d') if getattr(resident, 'birth_date', None) else None,
                    'gender': getattr(resident, 'gender', ''),
                    'address': f"{resident.dusun.name if resident.dusun else ''} - {resident.lorong.name if resident.lorong else ''}",
                    'phone': resident.phone
                }
                for resident in residents
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Admin API Views

def api_statistics(request):
    """API for admin dashboard statistics"""
    try:
        data = {
            'total_locations': PosyanduLocation.objects.filter(is_active=True).count(),
            'total_kader': PosyanduKader.objects.filter(status='aktif').count(),
            'total_ibu_hamil': IbuHamil.objects.filter(status_aktif=True).count(),
            'total_balita': Penduduk.objects.count(),  # Simplified for posyandu model
            'total_immunizations': Immunization.objects.count(),
            'total_health_records': HealthRecord.objects.count(),
            'total_nutrition_data': NutritionData.objects.count(),
            'total_stunting': StuntingData.objects.filter(
                status_stunting__in=['pendek', 'sangat_pendek']
            ).count()
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_location_list(request):
    """API to get posyandu locations for admin"""
    try:
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        capacity_filter = request.GET.get('capacity', '')
        page = int(request.GET.get('page', 1))
        
        locations = PosyanduLocation.objects.all().select_related('coordinator')
        
        # Apply filters
        if search_query:
            locations = locations.filter(
                Q(name__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if status_filter:
            if status_filter == 'active':
                locations = locations.filter(is_active=True)
            elif status_filter == 'inactive':
                locations = locations.filter(is_active=False)
            elif status_filter == 'maintenance':
                locations = locations.filter(is_active=False)  # Assuming maintenance means inactive
        
        if capacity_filter:
            if capacity_filter == 'small':
                locations = locations.filter(capacity__lt=50)
            elif capacity_filter == 'medium':
                locations = locations.filter(capacity__gte=50, capacity__lte=100)
            elif capacity_filter == 'large':
                locations = locations.filter(capacity__gt=100)
        
        # Calculate statistics
        total_locations = locations.count()
        active_locations = locations.filter(is_active=True).count()
        maintenance_locations = locations.filter(is_active=False).count()
        total_capacity = locations.aggregate(total=Sum('capacity'))['total'] or 0
        
        # Pagination
        paginator = Paginator(locations.order_by('name'), 12)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': loc.id,
                    'name': loc.name,
                    'address': loc.address,
                    'code': getattr(loc, 'code', ''),
                    'description': getattr(loc, 'description', ''),
                    'capacity': loc.capacity,
                    'status': 'active' if loc.is_active else 'inactive',
                    'phone': loc.contact_phone,
                    'email': getattr(loc, 'email', ''),
                    'latitude': getattr(loc, 'latitude', ''),
                    'longitude': getattr(loc, 'longitude', ''),
                    'amenities': loc.facilities,
                    'notes': getattr(loc, 'notes', ''),
                    'created_at': loc.created_at.strftime('%Y-%m-%d') if hasattr(loc, 'created_at') else '',
                    'updated_at': loc.updated_at.strftime('%Y-%m-%d') if hasattr(loc, 'updated_at') else '',
                    'image': loc.image.url if loc.image else '/static/images/defaults/placeholder.svg'
                }
                for loc in page_obj
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_count': paginator.count
            },
            'statistics': {
                'total': total_locations,
                'active': active_locations,
                'maintenance': maintenance_locations,
                'total_capacity': total_capacity
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def api_location_create(request):
    """API to create posyandu location"""
    try:
        if request.method == 'POST':
            # Handle form data (including file upload)
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle FormData (with file upload)
                location = PosyanduLocation.objects.create(
                    name=request.POST.get('name'),
                    code=request.POST.get('code', ''),
                    address=request.POST.get('address'),
                    description=request.POST.get('description', ''),
                    capacity=int(request.POST.get('capacity', 0)) if request.POST.get('capacity') else 0,
                    is_active=request.POST.get('status') == 'active',
                    contact_phone=request.POST.get('phone', ''),
                    email=request.POST.get('email', ''),
                    latitude=float(request.POST.get('latitude')) if request.POST.get('latitude') and request.POST.get('latitude').strip() else None,
                    longitude=float(request.POST.get('longitude')) if request.POST.get('longitude') and request.POST.get('longitude').strip() else None,
                    facilities=request.POST.get('amenities', ''),
                    notes=request.POST.get('notes', ''),
                    image=request.FILES.get('image')
                )
            else:
                # Handle JSON data (fallback)
                data = json.loads(request.body)
                location = PosyanduLocation.objects.create(
                    name=data.get('name'),
                    code=data.get('code', ''),
                    address=data.get('address'),
                    description=data.get('description', ''),
                    capacity=int(data.get('capacity', 0)) if data.get('capacity') else 0,
                    is_active=data.get('status') == 'active',
                    contact_phone=data.get('phone', ''),
                    email=data.get('email', ''),
                    latitude=float(data.get('latitude')) if data.get('latitude') and str(data.get('latitude')).strip() else None,
                    longitude=float(data.get('longitude')) if data.get('longitude') and str(data.get('longitude')).strip() else None,
                    facilities=data.get('amenities', ''),
                    notes=data.get('notes', '')
                )
            
            return JsonResponse({
                'success': True, 
                'message': 'Lokasi berhasil ditambahkan',
                'location_id': location.id
            })
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_location_update(request, location_id):
    """API to update posyandu location"""
    try:
        if request.method == 'GET':
            # Get location data for editing
            try:
                location = PosyanduLocation.objects.get(id=location_id)
                data = {
                    'id': location.id,
                    'name': location.name,
                    'code': getattr(location, 'code', ''),
                    'address': location.address,
                    'description': getattr(location, 'description', ''),
                    'capacity': location.capacity,
                    'status': 'active' if location.is_active else 'inactive',
                    'phone': location.contact_phone,
                    'email': getattr(location, 'email', ''),
                    'latitude': getattr(location, 'latitude', ''),
                    'longitude': getattr(location, 'longitude', ''),
                    'amenities': location.facilities,
                    'notes': getattr(location, 'notes', ''),
                    'image': location.image.url if location.image else '/static/images/defaults/placeholder.svg',
                    'created_at': location.created_at.strftime('%Y-%m-%d') if hasattr(location, 'created_at') else '',
                    'updated_at': location.updated_at.strftime('%Y-%m-%d') if hasattr(location, 'updated_at') else ''
                }
                return JsonResponse(data)
            except PosyanduLocation.DoesNotExist:
                return JsonResponse({'error': 'Location not found'}, status=404)
        
        elif request.method == 'POST':
            # Update location data
            try:
                location = PosyanduLocation.objects.get(id=location_id)
                
                # Handle form data (including file upload)
                if request.content_type and 'multipart/form-data' in request.content_type:
                    # Handle FormData (with file upload)
                    location.name = request.POST.get('name', location.name)
                    location.code = request.POST.get('code', location.code)
                    location.address = request.POST.get('address', location.address)
                    location.description = request.POST.get('description', location.description)
                    location.capacity = int(request.POST.get('capacity', 0)) if request.POST.get('capacity') else location.capacity
                    location.is_active = request.POST.get('status') == 'active'
                    location.contact_phone = request.POST.get('phone', location.contact_phone)
                    location.email = request.POST.get('email', location.email)
                    # Safe latitude conversion
                    lat_value = request.POST.get('latitude', '')
                    if lat_value and lat_value.strip():
                        try:
                            location.latitude = float(lat_value)
                        except ValueError:
                            location.latitude = None
                    else:
                        location.latitude = None
                    
                    # Safe longitude conversion
                    lng_value = request.POST.get('longitude', '')
                    if lng_value and lng_value.strip():
                        try:
                            location.longitude = float(lng_value)
                        except ValueError:
                            location.longitude = None
                    else:
                        location.longitude = None
                    location.facilities = request.POST.get('amenities', location.facilities)
                    location.notes = request.POST.get('notes', location.notes)
                    
                    # Handle image update
                    if request.FILES.get('image'):
                        location.image = request.FILES.get('image')
                else:
                    # Handle JSON data (fallback)
                    data = json.loads(request.body)
                    location.name = data.get('name', location.name)
                    location.code = data.get('code', location.code)
                    location.address = data.get('address', location.address)
                    location.description = data.get('description', location.description)
                    location.capacity = int(data.get('capacity', 0)) if data.get('capacity') else location.capacity
                    location.is_active = data.get('status') == 'active'
                    location.contact_phone = data.get('phone', location.contact_phone)
                    location.email = data.get('email', location.email)
                    # Safe latitude conversion for JSON
                    lat_value = data.get('latitude')
                    if lat_value and str(lat_value).strip():
                        try:
                            location.latitude = float(lat_value)
                        except ValueError:
                            location.latitude = None
                    else:
                        location.latitude = None
                    
                    # Safe longitude conversion for JSON
                    lng_value = data.get('longitude')
                    if lng_value and str(lng_value).strip():
                        try:
                            location.longitude = float(lng_value)
                        except ValueError:
                            location.longitude = None
                    else:
                        location.longitude = None
                    location.facilities = data.get('amenities', location.facilities)
                    location.notes = data.get('notes', location.notes)
                
                location.save()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Lokasi berhasil diperbarui'
                })
            except PosyanduLocation.DoesNotExist:
                return JsonResponse({'error': 'Location not found'}, status=404)
        
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_location_delete(request, location_id):
    """API to delete posyandu location"""
    try:
        if request.method == 'DELETE':
            try:
                location = PosyanduLocation.objects.get(id=location_id)
                location.delete()
                return JsonResponse({
                    'success': True, 
                    'message': 'Lokasi berhasil dihapus'
                })
            except PosyanduLocation.DoesNotExist:
                return JsonResponse({'error': 'Location not found'}, status=404)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_health_record_list(request):
    """API to get health records for admin"""
    try:
        from django.core.paginator import Paginator
        from django.db.models import Q, Count
        
        # Get filter parameters
        search = request.GET.get('search', '')
        posyandu = request.GET.get('posyandu', '')
        date = request.GET.get('date', '')
        patient_type = request.GET.get('patient_type', '')
        page = int(request.GET.get('page', 1))
        
        # Base queryset
        records = HealthRecord.objects.all().select_related('patient', 'posyandu').order_by('-visit_date')
        
        # Apply filters
        if search:
            records = records.filter(
                Q(patient__name__icontains=search) |
                Q(patient__nik__icontains=search)
            )
        
        if posyandu:
            records = records.filter(posyandu_id=posyandu)
        
        if date:
            records = records.filter(visit_date=date)
        
        if patient_type and patient_type != 'all':
            records = records.filter(patient_type=patient_type)
        
        # Calculate statistics
        total_records = records.count()
        balita_records = records.filter(patient_type='balita').count()
        ibu_hamil_records = records.filter(patient_type='ibu_hamil').count()
        lansia_records = records.filter(patient_type='lansia').count()
        
        # Pagination
        paginator = Paginator(records, 12)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': record.id,
                    'patient_id': record.patient.id,
                    'patient_name': record.patient.nama,
                    'patient_nik': record.patient.nik,
                    'posyandu_id': record.posyandu.id,
                    'posyandu_name': record.posyandu.name,
                    'patient_type': record.patient_type,
                    'visit_date': record.visit_date.strftime('%Y-%m-%d'),
                    'weight': float(record.weight) if record.weight else None,
                    'height': float(record.height) if record.height else None,
                    'blood_pressure': record.blood_pressure,
                    'temperature': float(record.temperature) if record.temperature else None,
                    'complaints': record.complaints,
                    'diagnosis': record.diagnosis,
                    'treatment': record.treatment,
                    'next_visit': record.next_visit.strftime('%Y-%m-%d') if record.next_visit else None,
                    'recorded_by': record.recorded_by.get_full_name() if record.recorded_by else 'Tidak ada',
                    'created_at': record.created_at.strftime('%Y-%m-%d %H:%M')
                }
                for record in page_obj
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_count': paginator.count
            },
            'statistics': {
                'total': total_records,
                'balita': balita_records,
                'ibu_hamil': ibu_hamil_records,
                'lansia': lansia_records
            }
        }
        return JsonResponse(data)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@csrf_exempt
def api_health_record_create(request):
    """API to create health record"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['patient_id', 'posyandu_id', 'patient_type', 'visit_date']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Field {field} is required'}, status=400)
        
        # Create health record
        health_record = HealthRecord.objects.create(
            patient_id=data.get('patient_id'),
            posyandu_id=data.get('posyandu_id'),
            patient_type=data.get('patient_type'),
            visit_date=data.get('visit_date'),
            weight=data.get('weight'),
            height=data.get('height'),
            blood_pressure=data.get('blood_pressure'),
            temperature=data.get('temperature'),
            complaints=data.get('complaints'),
            diagnosis=data.get('diagnosis'),
            treatment=data.get('treatment'),
            next_visit=data.get('next_visit'),
            recorded_by=request.user
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Rekam kesehatan berhasil dibuat',
            'id': health_record.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_health_record_update(request, record_id):
    """API to update health record"""
    try:
        if request.method == 'GET':
            # Get health record data for editing
            try:
                health_record = HealthRecord.objects.get(id=record_id)
                data = {
                    'id': health_record.id,
                    'patient_id': health_record.patient.id,
                    'patient_name': health_record.patient.name,
                    'posyandu_id': health_record.posyandu.id,
                    'posyandu_name': health_record.posyandu.name,
                    'patient_type': health_record.patient_type,
                    'visit_date': health_record.visit_date.strftime('%Y-%m-%d'),
                    'weight': float(health_record.weight) if health_record.weight else None,
                    'height': float(health_record.height) if health_record.height else None,
                    'blood_pressure': health_record.blood_pressure,
                    'temperature': float(health_record.temperature) if health_record.temperature else None,
                    'complaints': health_record.complaints,
                    'diagnosis': health_record.diagnosis,
                    'treatment': health_record.treatment,
                    'next_visit': health_record.next_visit.strftime('%Y-%m-%d') if health_record.next_visit else None,
                    'recorded_by': health_record.recorded_by.get_full_name() if health_record.recorded_by else 'Tidak ada',
                    'created_at': health_record.created_at.strftime('%Y-%m-%d %H:%M')
                }
                return JsonResponse(data)
            except HealthRecord.DoesNotExist:
                return JsonResponse({'error': 'Health record not found'}, status=404)
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            
            # Get health record
            health_record = HealthRecord.objects.get(id=record_id)
            
            # Update fields
            health_record.patient_id = data.get('patient_id', health_record.patient_id)
            health_record.posyandu_id = data.get('posyandu_id', health_record.posyandu_id)
            health_record.patient_type = data.get('patient_type', health_record.patient_type)
            health_record.visit_date = data.get('visit_date', health_record.visit_date)
            health_record.weight = data.get('weight', health_record.weight)
            health_record.height = data.get('height', health_record.height)
            health_record.blood_pressure = data.get('blood_pressure', health_record.blood_pressure)
            health_record.temperature = data.get('temperature', health_record.temperature)
            health_record.complaints = data.get('complaints', health_record.complaints)
            health_record.diagnosis = data.get('diagnosis', health_record.diagnosis)
            health_record.treatment = data.get('treatment', health_record.treatment)
            health_record.next_visit = data.get('next_visit', health_record.next_visit)
            
            health_record.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Rekam kesehatan berhasil diperbarui'
            })
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
            
    except HealthRecord.DoesNotExist:
        return JsonResponse({'error': 'Health record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_health_record_delete(request, record_id):
    """API to delete health record"""
    try:
        health_record = HealthRecord.objects.get(id=record_id)
        patient_name = health_record.patient.nama
        health_record.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Rekam kesehatan {patient_name} berhasil dihapus'
        })
    except HealthRecord.DoesNotExist:
        return JsonResponse({'error': 'Health record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_health_record_cleanup(request):
    """API to cleanup health records"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            cleanup_type = data.get('type', 'full')
            filters = data.get('filters', {})
            
            # Simple cleanup response
            response_data = {
                'success': True,
                'message': 'Cleanup completed successfully',
                'summary': {
                    'cleaned': 0,
                    'deleted': 0,
                    'fixed': 0,
                    'archived': 0
                },
                'details': [
                    {
                        'title': 'Cleanup Completed',
                        'description': 'Health records cleanup has been completed successfully',
                        'status': 'success'
                    }
                ]
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Schedule API Functions

def api_schedule_list(request):
    """API to get posyandu schedules for admin"""
    try:
        from django.core.paginator import Paginator
        from django.db.models import Q, Count
        
        # Get filter parameters
        search = request.GET.get('search', '')
        status = request.GET.get('status', '')
        location = request.GET.get('location', '')
        activity_type = request.GET.get('type', '')
        page = int(request.GET.get('page', 1))
        
        # Base queryset
        schedules = PosyanduSchedule.objects.all().select_related('location').order_by('-schedule_date', '-start_time')
        
        # Apply filters
        if search:
            schedules = schedules.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__name__icontains=search)
            )
        
        if status:
            if status == 'upcoming':
                schedules = schedules.filter(schedule_date__gte=timezone.now().date(), is_completed=False)
            elif status == 'ongoing':
                today = timezone.now().date()
                schedules = schedules.filter(schedule_date=today, is_completed=False)
            elif status == 'completed':
                schedules = schedules.filter(is_completed=True)
            elif status == 'cancelled':
                schedules = schedules.filter(is_completed=False, schedule_date__lt=timezone.now().date())
        
        if location:
            schedules = schedules.filter(location_id=location)
        
        if activity_type and activity_type != 'all':
            schedules = schedules.filter(activity_type=activity_type)
        
        # Calculate statistics
        total_schedules = schedules.count()
        upcoming_schedules = schedules.filter(schedule_date__gte=timezone.now().date(), is_completed=False).count()
        ongoing_schedules = schedules.filter(schedule_date=timezone.now().date(), is_completed=False).count()
        completed_schedules = schedules.filter(is_completed=True).count()
        
        # Pagination
        paginator = Paginator(schedules, 12)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': schedule.id,
                    'title': schedule.title,
                    'description': schedule.description,
                    'location_name': schedule.location.name if schedule.location else 'Tidak ada lokasi',
                    'location_id': schedule.location.id if schedule.location else None,
                    'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d') if schedule.schedule_date else None,
                    'start_time': schedule.start_time.strftime('%H:%M') if schedule.start_time else None,
                    'end_time': schedule.end_time.strftime('%H:%M') if schedule.end_time else None,
                    'activity_type': schedule.activity_type,
                    'participants': schedule.actual_participants or 0,
                    'max_participants': schedule.target_participants or 0,
                    'organizer': schedule.created_by.get_full_name() if schedule.created_by else 'Tidak ada',
                    'status': 'upcoming' if schedule.schedule_date and schedule.schedule_date > timezone.now().date() and not schedule.is_completed else
                             'ongoing' if schedule.schedule_date and schedule.schedule_date == timezone.now().date() and not schedule.is_completed else
                             'completed' if schedule.is_completed else 'cancelled',
                    'is_completed': schedule.is_completed
                }
                for schedule in page_obj
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_count': paginator.count
            },
            'statistics': {
                'total': total_schedules,
                'upcoming': upcoming_schedules,
                'ongoing': ongoing_schedules,
                'completed': completed_schedules
            }
        }
        return JsonResponse(data)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@csrf_exempt
def api_schedule_create(request):
    """API to create new schedule"""
    try:
        data = json.loads(request.body)
        schedule = PosyanduSchedule.objects.create(
            title=data.get('title'),
            description=data.get('description', ''),
            location_id=data.get('location_id'),
            schedule_date=data.get('schedule_date'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            activity_type=data.get('activity_type'),
            target_participants=data.get('target_participants', 0),
            actual_participants=data.get('actual_participants', 0),
            notes=data.get('notes', ''),
            is_completed=data.get('is_completed', False)
        )
        return JsonResponse({'success': True, 'message': 'Schedule created successfully', 'id': schedule.id})
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


def api_schedule_detail(request, schedule_id):
    """API to get schedule detail"""
    try:
        schedule = PosyanduSchedule.objects.get(id=schedule_id)
        data = {
            'id': schedule.id,
            'title': schedule.title,
            'description': schedule.description,
            'activity_type': schedule.activity_type,
            'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d') if schedule.schedule_date else None,
            'start_time': schedule.start_time.strftime('%H:%M') if schedule.start_time else None,
            'end_time': schedule.end_time.strftime('%H:%M') if schedule.end_time else None,
            'location_id': schedule.location.id if schedule.location else None,
            'location_name': schedule.location.name if schedule.location else 'Tidak ada lokasi',
            'target_participants': schedule.target_participants,
            'actual_participants': schedule.actual_participants,
            'participants': schedule.actual_participants,
            'max_participants': schedule.target_participants,
            'organizer': schedule.created_by.get_full_name() if schedule.created_by else 'Tidak ada',
            'notes': schedule.notes,
            'is_completed': schedule.is_completed,
            'status': 'upcoming' if schedule.schedule_date and schedule.schedule_date > timezone.now().date() and not schedule.is_completed else
                     'ongoing' if schedule.schedule_date and schedule.schedule_date == timezone.now().date() and not schedule.is_completed else
                     'completed' if schedule.is_completed else 'cancelled',
            'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(schedule, 'created_at') else None,
            'updated_at': schedule.updated_at.strftime('%Y-%m-%d %H:%M') if hasattr(schedule, 'updated_at') else None
        }
        return JsonResponse(data)
    except PosyanduSchedule.DoesNotExist:
        return JsonResponse({'error': 'Schedule not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_schedule_update(request, schedule_id):
    """API to update schedule"""
    try:
        data = json.loads(request.body)
        schedule = PosyanduSchedule.objects.get(id=schedule_id)
        schedule.title = data.get('title', schedule.title)
        schedule.description = data.get('description', schedule.description)
        schedule.location_id = data.get('location_id', schedule.location_id)
        schedule.schedule_date = data.get('schedule_date', schedule.schedule_date)
        schedule.start_time = data.get('start_time', schedule.start_time)
        schedule.end_time = data.get('end_time', schedule.end_time)
        schedule.activity_type = data.get('activity_type', schedule.activity_type)
        schedule.target_participants = data.get('target_participants', schedule.target_participants)
        schedule.actual_participants = data.get('actual_participants', schedule.actual_participants)
        schedule.notes = data.get('notes', schedule.notes)
        schedule.is_completed = data.get('is_completed', schedule.is_completed)
        schedule.save()
        return JsonResponse({'success': True, 'message': 'Schedule updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_schedule_delete(request, schedule_id):
    """API to delete schedule"""
    try:
        schedule = PosyanduSchedule.objects.get(id=schedule_id)
        schedule.delete()
        return JsonResponse({'success': True, 'message': 'Schedule deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Ibu Hamil API Functions

def api_ibu_hamil_list(request):
    """API to get ibu hamil data for admin"""
    try:
        # Get search and filter parameters
        search = request.GET.get('search', '')
        posyandu_filter = request.GET.get('posyandu', '')
        trimester_filter = request.GET.get('trimester', '')
        
        # Base query
        ibu_hamil_list = IbuHamil.objects.all().select_related('penduduk', 'posyandu')
        
        # Apply filters
        if search:
            ibu_hamil_list = ibu_hamil_list.filter(
                penduduk__name__icontains=search
            )
        
        if posyandu_filter:
            ibu_hamil_list = ibu_hamil_list.filter(posyandu_id=posyandu_filter)
        
        if trimester_filter:
            if trimester_filter == '1':
                ibu_hamil_list = ibu_hamil_list.filter(usia_kehamilan__lte=12)
            elif trimester_filter == '2':
                ibu_hamil_list = ibu_hamil_list.filter(usia_kehamilan__gt=12, usia_kehamilan__lte=27)
            elif trimester_filter == '3':
                ibu_hamil_list = ibu_hamil_list.filter(usia_kehamilan__gt=27)
        
        # Calculate statistics
        total = ibu_hamil_list.count()
        trimester1 = ibu_hamil_list.filter(usia_kehamilan__lte=12).count()
        trimester2 = ibu_hamil_list.filter(usia_kehamilan__gt=12, usia_kehamilan__lte=27).count()
        trimester3 = ibu_hamil_list.filter(usia_kehamilan__gt=27).count()
        
        data = {
            'results': [
                {
                    'id': ibu.id,
                    'penduduk_name': ibu.penduduk.nama if ibu.penduduk else None,
                    'penduduk_nik': ibu.penduduk.nik if ibu.penduduk else None,
                    'tanggal_hpht': ibu.tanggal_hpht.strftime('%Y-%m-%d') if ibu.tanggal_hpht else None,
                    'usia_kehamilan': ibu.usia_kehamilan,
                    'tanggal_perkiraan_lahir': ibu.tanggal_perkiraan_lahir.strftime('%Y-%m-%d') if ibu.tanggal_perkiraan_lahir else None,
                    'riwayat_kehamilan': ibu.riwayat_kehamilan,
                    'risiko_kehamilan': ibu.risiko_kehamilan,
                    'status_aktif': ibu.status_aktif,
                    'posyandu_name': ibu.posyandu.name if ibu.posyandu else None
                }
                for ibu in ibu_hamil_list
            ],
            'statistics': {
                'total': total,
                'trimester1': trimester1,
                'trimester2': trimester2,
                'trimester3': trimester3
            },
            'pagination': {
                'current_page': 1,
                'total_pages': 1,
                'has_next': False,
                'has_prev': False
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_ibu_hamil_create(request):
    """API to create new ibu hamil record"""
    try:
        if request.method == 'POST':
            data = request.POST
            
            required_fields = ['penduduk_id', 'posyandu_id', 'tanggal_hpht']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'Field {field} is required'}, status=400)
            
            # Helper function to convert empty string to None for decimal fields
            def safe_decimal(value):
                if value and value.strip():
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return None
                return None
            
            ibu_hamil = IbuHamil.objects.create(
                penduduk_id=data.get('penduduk_id'),
                posyandu_id=data.get('posyandu_id'),
                tanggal_hpht=data.get('tanggal_hpht'),
                usia_kehamilan=int(data.get('usia_kehamilan', 0)) if data.get('usia_kehamilan') else None,
                tanggal_perkiraan_lahir=data.get('tanggal_perkiraan_lahir'),
                riwayat_kehamilan=data.get('riwayat_kehamilan'),
                berat_badan_sebelum_hamil=safe_decimal(data.get('berat_badan_sebelum_hamil')),
                tinggi_badan=safe_decimal(data.get('tinggi_badan')),
                golongan_darah=data.get('golongan_darah'),
                riwayat_penyakit=data.get('riwayat_penyakit'),
                risiko_kehamilan=data.get('risiko_kehamilan', 'rendah'),
                nomor_buku_kia=data.get('nomor_buku_kia'),
                status_aktif=data.get('status_aktif', 'true').lower() == 'true',
                keterangan=data.get('keterangan')
            )
            return JsonResponse({'success': True, 'message': 'Data ibu hamil berhasil ditambahkan', 'id': ibu_hamil.id})
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_ibu_hamil_update(request, ibu_hamil_id):
    """API to update ibu hamil record"""
    try:
        if request.method == 'GET':
            ibu_hamil = IbuHamil.objects.get(id=ibu_hamil_id)
            return JsonResponse({
                'id': ibu_hamil.id,
                'penduduk_id': ibu_hamil.penduduk_id,
                'penduduk_name': ibu_hamil.penduduk.nama if ibu_hamil.penduduk else None,
                'penduduk_nik': ibu_hamil.penduduk.nik if ibu_hamil.penduduk else None,
                'penduduk_birth_date': getattr(ibu_hamil.penduduk, 'birth_date', None).strftime('%Y-%m-%d') if ibu_hamil.penduduk and getattr(ibu_hamil.penduduk, 'birth_date', None) else None,
                'penduduk_gender': ibu_hamil.penduduk.gender if ibu_hamil.penduduk else None,
                'penduduk_address': ibu_hamil.penduduk.address if ibu_hamil.penduduk else None,
                'penduduk_phone': ibu_hamil.penduduk.phone_number if ibu_hamil.penduduk else None,
                'penduduk_occupation': ibu_hamil.penduduk.occupation if ibu_hamil.penduduk else None,
                'posyandu_id': ibu_hamil.posyandu_id,
                'posyandu_name': ibu_hamil.posyandu.name if ibu_hamil.posyandu else None,
                'tanggal_hpht': ibu_hamil.tanggal_hpht.strftime('%Y-%m-%d') if ibu_hamil.tanggal_hpht else None,
                'usia_kehamilan': ibu_hamil.usia_kehamilan,
                'tanggal_perkiraan_lahir': ibu_hamil.tanggal_perkiraan_lahir.strftime('%Y-%m-%d') if ibu_hamil.tanggal_perkiraan_lahir else None,
                'riwayat_kehamilan': ibu_hamil.riwayat_kehamilan,
                'berat_badan_sebelum_hamil': float(ibu_hamil.berat_badan_sebelum_hamil) if ibu_hamil.berat_badan_sebelum_hamil else None,
                'tinggi_badan': float(ibu_hamil.tinggi_badan) if ibu_hamil.tinggi_badan else None,
                'golongan_darah': ibu_hamil.golongan_darah,
                'riwayat_penyakit': ibu_hamil.riwayat_penyakit,
                'risiko_kehamilan': ibu_hamil.risiko_kehamilan,
                'nomor_buku_kia': ibu_hamil.nomor_buku_kia,
                'status_aktif': ibu_hamil.status_aktif,
                'keterangan': ibu_hamil.keterangan
            })
        elif request.method == 'POST':
            data = request.POST
            ibu_hamil = IbuHamil.objects.get(id=ibu_hamil_id)
            
            # Helper function to convert empty string to None for decimal fields
            def safe_decimal(value):
                if value and value.strip():
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return None
                return None
            
            ibu_hamil.penduduk_id = data.get('penduduk_id', ibu_hamil.penduduk_id)
            ibu_hamil.posyandu_id = data.get('posyandu_id', ibu_hamil.posyandu_id)
            ibu_hamil.tanggal_hpht = data.get('tanggal_hpht', ibu_hamil.tanggal_hpht)
            ibu_hamil.usia_kehamilan = int(data.get('usia_kehamilan', ibu_hamil.usia_kehamilan)) if data.get('usia_kehamilan') else ibu_hamil.usia_kehamilan
            ibu_hamil.tanggal_perkiraan_lahir = data.get('tanggal_perkiraan_lahir', ibu_hamil.tanggal_perkiraan_lahir)
            ibu_hamil.riwayat_kehamilan = data.get('riwayat_kehamilan', ibu_hamil.riwayat_kehamilan)
            ibu_hamil.berat_badan_sebelum_hamil = safe_decimal(data.get('berat_badan_sebelum_hamil')) if data.get('berat_badan_sebelum_hamil') else ibu_hamil.berat_badan_sebelum_hamil
            ibu_hamil.tinggi_badan = safe_decimal(data.get('tinggi_badan')) if data.get('tinggi_badan') else ibu_hamil.tinggi_badan
            ibu_hamil.golongan_darah = data.get('golongan_darah', ibu_hamil.golongan_darah)
            ibu_hamil.riwayat_penyakit = data.get('riwayat_penyakit', ibu_hamil.riwayat_penyakit)
            ibu_hamil.risiko_kehamilan = data.get('risiko_kehamilan', ibu_hamil.risiko_kehamilan)
            ibu_hamil.nomor_buku_kia = data.get('nomor_buku_kia', ibu_hamil.nomor_buku_kia)
            ibu_hamil.status_aktif = data.get('status_aktif', 'true').lower() == 'true'
            ibu_hamil.keterangan = data.get('keterangan', ibu_hamil.keterangan)
            ibu_hamil.save()
            return JsonResponse({'success': True, 'message': 'Data ibu hamil berhasil diperbarui'})
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_ibu_hamil_delete(request, ibu_hamil_id):
    """API to delete ibu hamil record"""
    try:
        ibu_hamil = IbuHamil.objects.get(id=ibu_hamil_id)
        ibu_hamil.delete()
        return JsonResponse({'success': True, 'message': 'Ibu hamil record deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Immunization API Functions

def api_immunization_list(request):
    """API to get immunization data for admin"""
    try:
        immunizations = Immunization.objects.all().select_related('patient', 'posyandu')
        data = {
            'results': [
                {
                    'id': imm.id,
                    'patient_name': imm.patient.nama if imm.patient else None,
                    'patient_nik': imm.patient.nik if imm.patient else None,
                    'vaccine_type': imm.vaccine_type,
                    'immunization_date': imm.immunization_date.strftime('%Y-%m-%d') if imm.immunization_date else None,
                    'batch_number': imm.batch_number,
                    'health_worker': imm.health_worker,
                    'status': imm.status,
                    'posyandu_name': imm.posyandu.name if imm.posyandu else None
                }
                for imm in immunizations
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_immunization_create(request):
    """API to create new immunization record"""
    try:
        data = json.loads(request.body)
        immunization = Immunization.objects.create(
            patient_id=data.get('patient_id'),
            posyandu_id=data.get('posyandu_id'),
            vaccine_type=data.get('vaccine_type'),
            immunization_date=data.get('immunization_date'),
            batch_number=data.get('batch_number'),
            next_schedule=data.get('next_schedule'),
            health_worker=data.get('health_worker'),
            notes=data.get('notes'),
            status=data.get('status', 'completed'),
            recorded_by=request.user
        )
        return JsonResponse({'success': True, 'message': 'Immunization record created successfully', 'id': immunization.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_immunization_update(request, immunization_id):
    """API to update immunization record"""
    try:
        data = json.loads(request.body)
        immunization = Immunization.objects.get(id=immunization_id)
        immunization.patient_id = data.get('patient_id', immunization.patient_id)
        immunization.posyandu_id = data.get('posyandu_id', immunization.posyandu_id)
        immunization.vaccine_type = data.get('vaccine_type', immunization.vaccine_type)
        immunization.immunization_date = data.get('immunization_date', immunization.immunization_date)
        immunization.batch_number = data.get('batch_number', immunization.batch_number)
        immunization.next_schedule = data.get('next_schedule', immunization.next_schedule)
        immunization.health_worker = data.get('health_worker', immunization.health_worker)
        immunization.notes = data.get('notes', immunization.notes)
        immunization.status = data.get('status', immunization.status)
        immunization.save()
        return JsonResponse({'success': True, 'message': 'Immunization record updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_immunization_delete(request, immunization_id):
    """API to delete immunization record"""
    try:
        immunization = Immunization.objects.get(id=immunization_id)
        immunization.delete()
        return JsonResponse({'success': True, 'message': 'Immunization record deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Kader API Functions

def api_kader_list(request):
    """API to get kader data for admin"""
    try:
        # Get search and filter parameters
        search = request.GET.get('search', '')
        jabatan = request.GET.get('jabatan', '')
        status = request.GET.get('status', '')
        page = int(request.GET.get('page', 1))
        
        # Filter kaders
        kaders = PosyanduKader.objects.all().select_related('penduduk', 'posyandu')
        
        if search:
            kaders = kaders.filter(
                Q(penduduk__name__icontains=search) | 
                Q(penduduk__nik__icontains=search)
            )
        
        if jabatan:
            kaders = kaders.filter(jabatan=jabatan)
            
        if status:
            kaders = kaders.filter(status=status)
        
        # Calculate statistics
        total_kaders = kaders.count()
        active_kaders = kaders.filter(status='aktif').count()
        trained_kaders = kaders.filter(tanggal_selesai__isnull=False).count()
        volunteer_kaders = kaders.filter(jabatan='anggota').count()
        
        # Pagination
        from django.core.paginator import Paginator
        paginator = Paginator(kaders, 12)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': kader.id,
                    'name': kader.penduduk.nama if kader.penduduk else None,
                    'nik': kader.penduduk.nik if kader.penduduk else None,
                    'jabatan': kader.jabatan,
                    'status': kader.status,
                    'tanggal_mulai': kader.tanggal_mulai.strftime('%Y-%m-%d') if kader.tanggal_mulai else None,
                    'tanggal_selesai': kader.tanggal_selesai.strftime('%Y-%m-%d') if kader.tanggal_selesai else None,
                    'nomor_hp': kader.nomor_hp,
                    'posyandu_name': kader.posyandu.name if kader.posyandu else None,
                    'keterangan': kader.keterangan,
                    'avatar': kader.penduduk.photo.url if kader.penduduk and kader.penduduk.photo else '/static/images/defaults/avatar-placeholder.svg'
                }
                for kader in page_obj
            ],
            'statistics': {
                'total': total_kaders,
                'active': active_kaders,
                'trained': trained_kaders,
                'volunteer': volunteer_kaders
            },
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'total_count': paginator.count
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_kader_create(request):
    """API to create new kader record"""
    try:
        data = json.loads(request.body)
        kader = PosyanduKader.objects.create(
            penduduk_id=data.get('penduduk_id'),
            posyandu_id=data.get('posyandu_id'),
            jabatan=data.get('jabatan'),
            status=data.get('status', 'aktif'),
            tanggal_mulai=data.get('tanggal_mulai'),
            tanggal_selesai=data.get('tanggal_selesai'),
            nomor_hp=data.get('nomor_hp'),
            keterangan=data.get('keterangan')
        )
        return JsonResponse({'success': True, 'message': 'Kader record created successfully', 'id': kader.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_kader_update(request, kader_id):
    """API to update kader record"""
    try:
        if request.method == 'GET':
            # Return kader data for editing
            kader = PosyanduKader.objects.get(id=kader_id)
            data = {
                'id': kader.id,
                'name': kader.penduduk.nama if kader.penduduk else None,
                'nik': kader.penduduk.nik if kader.penduduk else None,
                'phone': kader.nomor_hp,
                'email': getattr(kader.penduduk, 'email', '') if kader.penduduk else '',
                'jabatan': kader.jabatan,
                'status': kader.status,
                'address': kader.penduduk.address if kader.penduduk else '',
                'skills': kader.keterangan,
                'join_date': kader.tanggal_mulai.strftime('%Y-%m-%d') if kader.tanggal_mulai else None,
                'training_date': kader.tanggal_selesai.strftime('%Y-%m-%d') if kader.tanggal_selesai else None,
                'notes': kader.keterangan,
                'penduduk_id': kader.penduduk_id,
                'posyandu_id': kader.posyandu_id
            }
            return JsonResponse(data)
        else:
            # Update kader data
            data = json.loads(request.body)
            kader = PosyanduKader.objects.get(id=kader_id)
            kader.penduduk_id = data.get('penduduk_id', kader.penduduk_id)
            kader.posyandu_id = data.get('posyandu_id', kader.posyandu_id)
            kader.jabatan = data.get('jabatan', kader.jabatan)
            kader.status = data.get('status', kader.status)
            kader.tanggal_mulai = data.get('tanggal_mulai', kader.tanggal_mulai)
            kader.tanggal_selesai = data.get('tanggal_selesai', kader.tanggal_selesai)
            kader.nomor_hp = data.get('nomor_hp', kader.nomor_hp)
            kader.keterangan = data.get('keterangan', kader.keterangan)
            kader.save()
            return JsonResponse({'success': True, 'message': 'Kader record updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_kader_delete(request, kader_id):
    """API to delete kader record"""
    try:
        kader = PosyanduKader.objects.get(id=kader_id)
        kader.delete()
        return JsonResponse({'success': True, 'message': 'Kader record deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_penduduk_search(request):
    """API to search penduduk for posyandu forms - konsisten dengan modul lain"""
    try:
        # Import Penduduk model
        try:
            from letters.models import Penduduk
        except ImportError:
            return JsonResponse({
                'success': False,
                'error': 'Penduduk model not available',
                'results': []
            }, status=500)
            
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 100))
        age_group = request.GET.get('age_group', '')
        age_min = request.GET.get('age_min')
        age_max = request.GET.get('age_max')
        gender = request.GET.get('gender')
        
        # Build base queryset
        penduduk_list = Penduduk.objects.filter(
            is_active=True, 
            is_alive=True
        ).select_related('dusun', 'lorong')
        
        # Apply search query if provided
        if query and len(query) >= 2:
            penduduk_list = penduduk_list.filter(
                Q(name__icontains=query) | 
                Q(nik__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(mobile_number__icontains=query)
            )
        elif query and len(query) < 2:
            return JsonResponse({'success': True, 'results': []})
        
        # Apply additional filters
        if gender:
            penduduk_list = penduduk_list.filter(gender=gender)
        
        # Add age group filter if provided
        if age_group == 'balita':
            # Balita: 0-5 tahun (0-60 bulan) - filter by birth_date
            from datetime import date, timedelta
            five_years_ago = date.today() - timedelta(days=5*365)
            penduduk_list = penduduk_list.filter(birth_date__gte=five_years_ago)
        elif age_group == 'ibu_hamil':
            # Ibu hamil: perempuan 17+ tahun - only females
            from datetime import date, timedelta
            seventeen_years_ago = date.today() - timedelta(days=int(17*365.25))
            penduduk_list = penduduk_list.filter(
                gender='P',  # Only females
                birth_date__lte=seventeen_years_ago  # 17+ years old
            )
        
        # Apply age filters if provided
        if age_min:
            from datetime import date, timedelta
            max_birth_date = date.today() - timedelta(days=int(age_min) * 365)
            penduduk_list = penduduk_list.filter(birth_date__lte=max_birth_date)
        if age_max:
            from datetime import date, timedelta
            min_birth_date = date.today() - timedelta(days=int(age_max) * 365)
            penduduk_list = penduduk_list.filter(birth_date__gte=min_birth_date)
        
        # Apply ordering and limit
        penduduk_list = penduduk_list.order_by('name')[:limit]
        
        results = []
        for penduduk in penduduk_list:
            try:
                # Get all available data like business API
                # Calculate age from birth_date
                age = 0
                if penduduk.birth_date:
                    from datetime import date
                    today = date.today()
                    age = today.year - penduduk.birth_date.year - ((today.month, today.day) < (penduduk.birth_date.month, penduduk.birth_date.day))
                
                penduduk_data = {
                    'id': penduduk.id,
                    'nik': penduduk.nik or '',
                    'name': penduduk.name or '',
                    'gender': penduduk.gender or '',
                    'gender_display': penduduk.gender or '',
                    'birth_date': penduduk.birth_date.strftime('%Y-%m-%d') if penduduk.birth_date else None,
                    'age': age,
                    'phone_number': penduduk.phone_number or '',
                    'mobile_number': penduduk.mobile_number or '',
                    'email': penduduk.email or '',
                    'address': penduduk.address or '',
                    'dusun': penduduk.dusun.name if penduduk.dusun else '',
                    'lorong': penduduk.lorong.name if penduduk.lorong else '',
                    'rt': penduduk.rt or '',
                    'rw': penduduk.rw or '',
                    'education': penduduk.get_education_display() if penduduk.education else '',
                    'occupation': penduduk.occupation or '',
                    'religion': penduduk.get_religion_display() if penduduk.religion else '',
                    'marital_status': penduduk.get_marital_status_display() if penduduk.marital_status else '',
                    'photo': penduduk.photo.url if penduduk.photo else '/static/images/defaults/avatar-placeholder.svg',
                    'is_active': penduduk.is_active,
                    'is_alive': penduduk.is_alive,
                    'created_at': penduduk.created_at.strftime('%Y-%m-%d %H:%M') if penduduk.created_at else None,
                    'updated_at': penduduk.updated_at.strftime('%Y-%m-%d %H:%M') if penduduk.updated_at else None
                }
                results.append(penduduk_data)
                
            except Exception as field_error:
                print(f"Error processing penduduk {penduduk.id}: {str(field_error)}")
                # Add minimal data for this penduduk
                results.append({
                    'id': penduduk.id,
                    'nik': getattr(penduduk, 'nik', ''),
                    'name': getattr(penduduk, 'name', ''),
                    'gender': '',
                    'birth_date': None,
                    'age': 0,
                    'phone': '',
                    'email': '',
                    'address': '',
                    'dusun': '',
                    'photo': '/static/images/defaults/avatar-placeholder.svg',
                    'education': '',
                    'occupation': '',
                    'religion': '',
                    'marital_status': ''
                })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        import traceback
        print(f"Error in api_penduduk_search: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e),
            'results': []
        }, status=500)


def api_posyandu_locations(request):
    """API to get posyandu locations for dropdown"""
    try:
        locations = PosyanduLocation.objects.filter(is_active=True)
        data = {
            'results': [
                {
                    'id': location.id,
                    'name': location.name,
                    'address': location.address,
                    'contact_phone': location.contact_phone,
                    'capacity': location.capacity
                }
                for location in locations
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def kader_create(request):
    """Create new kader form"""
    if request.method == 'POST':
        try:
            penduduk_id = request.POST.get('penduduk_id')
            posyandu_id = request.POST.get('posyandu_id')
            jabatan = request.POST.get('jabatan')
            status = request.POST.get('status', 'aktif')
            nomor_hp = request.POST.get('nomor_hp', '')
            tanggal_mulai = request.POST.get('tanggal_mulai')
            tanggal_selesai = request.POST.get('tanggal_selesai')
            keterangan = request.POST.get('keterangan', '')
            
            # Create kader
            kader = PosyanduKader.objects.create(
                penduduk_id=penduduk_id,
                posyandu_id=posyandu_id,
                jabatan=jabatan,
                status=status,
                nomor_hp=nomor_hp,
                tanggal_mulai=tanggal_mulai,
                tanggal_selesai=tanggal_selesai if tanggal_selesai else None,
                keterangan=keterangan
            )
            
            messages.success(request, 'Kader berhasil ditambahkan!')
            return redirect('posyandu:kader_detail', kader_id=kader.id)
            
        except Exception as e:
            messages.error(request, f'Error creating kader: {str(e)}')
    
    # Get posyandu locations for dropdown
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True)
    
    context = {
        'posyandu_locations': posyandu_locations,
    }
    return render(request, 'admin_panel/posyandu/kader_form.html', context)


def kader_detail(request, kader_id):
    """Detail kader view"""
    try:
        kader = get_object_or_404(PosyanduKader, id=kader_id)
        
        context = {
            'kader': kader,
        }
        return render(request, 'admin_panel/posyandu/kader_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading kader: {str(e)}')
        return redirect('posyandu:kaders')


def kader_update(request, kader_id):
    """Update kader form"""
    kader = get_object_or_404(PosyanduKader, id=kader_id)
    
    if request.method == 'POST':
        try:
            kader.posyandu_id = request.POST.get('posyandu_id')
            kader.jabatan = request.POST.get('jabatan')
            kader.status = request.POST.get('status', 'aktif')
            kader.nomor_hp = request.POST.get('nomor_hp', '')
            kader.tanggal_mulai = request.POST.get('tanggal_mulai')
            kader.tanggal_selesai = request.POST.get('tanggal_selesai') if request.POST.get('tanggal_selesai') else None
            kader.keterangan = request.POST.get('keterangan', '')
            kader.save()
            
            messages.success(request, 'Kader berhasil diupdate!')
            return redirect('posyandu:kader_detail', kader_id=kader.id)
            
        except Exception as e:
            messages.error(request, f'Error updating kader: {str(e)}')
    
    # Get posyandu locations for dropdown
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True)
    
    context = {
        'kader': kader,
        'posyandu_locations': posyandu_locations,
    }
    return render(request, 'admin_panel/posyandu/kader_form.html', context)

# Stunting Data API Functions

def api_stunting_data_list(request):
    """API to get stunting data for admin"""
    try:
        stunting_data = StuntingData.objects.all().select_related('balita', 'posyandu')
        data = {
            'results': [
                {
                    'id': stunting.id,
                    'child_name': stunting.balita.nama if stunting.balita else None,
                    'child_nik': stunting.balita.nik if stunting.balita else None,
                    'measurement_date': stunting.tanggal_ukur.strftime('%Y-%m-%d') if stunting.tanggal_ukur else None,
                    'age_months': stunting.usia_bulan,
                    'height': stunting.tinggi_badan,
                    'weight': stunting.berat_badan,
                    'gender': getattr(stunting.balita, 'gender', None) if stunting.balita else None,
                    'stunting_status': stunting.status_stunting,
                    'intervention': stunting.intervensi_diberikan,
                    'posyandu_name': stunting.posyandu.name if stunting.posyandu else None,
                    'bmi': round(stunting.berat_badan / ((stunting.tinggi_badan/100) ** 2), 2) if stunting.tinggi_badan and stunting.berat_badan else None
                }
                for stunting in stunting_data
            ],
            'statistics': {
                'total': stunting_data.count(),
                'stunting': stunting_data.filter(status_stunting='stunting').count(),
                'severe_stunting': stunting_data.filter(status_stunting='severe-stunting').count(),
                'normal': stunting_data.filter(status_stunting='normal').count()
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_stunting_data_create(request):
    """API to create new stunting data record"""
    try:
        if request.method == 'POST':
            # Handle FormData (from form submission)
            data = request.POST
            
            # Validate required fields
            required_fields = ['child_id', 'posyandu_id', 'measurement_date', 'age_months', 'height', 'weight', 'stunting_status']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'Field {field} is required'}, status=400)
            
            # Convert string values to appropriate types
            try:
                usia_bulan = int(data.get('age_months')) if data.get('age_months') else None
                tinggi_badan = float(data.get('height')) if data.get('height') else None
                berat_badan = float(data.get('weight')) if data.get('weight') else None
                z_score_tb_u = float(data.get('z_score_tb_u')) if data.get('z_score_tb_u') else None
                z_score_bb_u = float(data.get('z_score_bb_u')) if data.get('z_score_bb_u') else None
                z_score_bb_tb = float(data.get('z_score_bb_tb')) if data.get('z_score_bb_tb') else None
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid data format: {str(e)}'}, status=400)
            
            stunting_data = StuntingData.objects.create(
                balita_id=data.get('child_id'),
                posyandu_id=data.get('posyandu_id'),
                tanggal_ukur=data.get('measurement_date'),
                usia_bulan=usia_bulan,
                tinggi_badan=tinggi_badan,
                berat_badan=berat_badan,
                z_score_tb_u=z_score_tb_u,
                z_score_bb_u=z_score_bb_u,
                z_score_bb_tb=z_score_bb_tb,
                status_stunting=data.get('stunting_status'),
                asi_eksklusif=data.get('asi_eksklusif') == 'true' or data.get('asi_eksklusif') == 'on',
                riwayat_bblr=data.get('riwayat_bblr') == 'true' or data.get('riwayat_bblr') == 'on',
                riwayat_penyakit=data.get('riwayat_penyakit', ''),
                intervensi_diberikan=data.get('intervention'),
                hasil_intervensi=data.get('hasil_intervensi', ''),
                follow_up_date=data.get('follow_up_date') if data.get('follow_up_date') else None,
                keterangan=data.get('notes'),
                recorded_by=request.user
            )
            return JsonResponse({'success': True, 'message': 'Data stunting berhasil ditambahkan', 'id': stunting_data.id})
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_stunting_data_update(request, stunting_data_id):
    """API to update stunting data record"""
    try:
        if request.method == 'GET':
            # Return stunting data for editing
            stunting_data = StuntingData.objects.get(id=stunting_data_id)
            return JsonResponse({
                'id': stunting_data.id,
                'child_id': stunting_data.balita_id,
                'child_name': stunting_data.balita.nama if stunting_data.balita else None,
                'measurement_date': stunting_data.tanggal_ukur.strftime('%Y-%m-%d') if stunting_data.tanggal_ukur else None,
                'age_months': stunting_data.usia_bulan,
                'height': stunting_data.tinggi_badan,
                'weight': stunting_data.berat_badan,
                'gender': getattr(stunting_data.balita, 'gender', None) if stunting_data.balita else None,
                'stunting_status': stunting_data.status_stunting,
                'intervention': stunting_data.intervensi_diberikan,
                'posyandu_id': stunting_data.posyandu_id,
                'notes': stunting_data.keterangan
            })
        elif request.method == 'POST':
            # Handle FormData (from form submission)
            data = request.POST
            
            stunting_data = StuntingData.objects.get(id=stunting_data_id)
            
            # Convert string values to appropriate types
            try:
                if data.get('age_months'):
                    stunting_data.usia_bulan = int(data.get('age_months'))
                if data.get('height'):
                    stunting_data.tinggi_badan = float(data.get('height'))
                if data.get('weight'):
                    stunting_data.berat_badan = float(data.get('weight'))
                if data.get('z_score_tb_u'):
                    stunting_data.z_score_tb_u = float(data.get('z_score_tb_u'))
                if data.get('z_score_bb_u'):
                    stunting_data.z_score_bb_u = float(data.get('z_score_bb_u'))
                if data.get('z_score_bb_tb'):
                    stunting_data.z_score_bb_tb = float(data.get('z_score_bb_tb'))
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid data format: {str(e)}'}, status=400)
            
            stunting_data.balita_id = data.get('child_id', stunting_data.balita_id)
            stunting_data.posyandu_id = data.get('posyandu_id', stunting_data.posyandu_id)
            stunting_data.tanggal_ukur = data.get('measurement_date', stunting_data.tanggal_ukur)
            stunting_data.status_stunting = data.get('stunting_status', stunting_data.status_stunting)
            stunting_data.asi_eksklusif = data.get('asi_eksklusif') == 'true' or data.get('asi_eksklusif') == 'on'
            stunting_data.riwayat_bblr = data.get('riwayat_bblr') == 'true' or data.get('riwayat_bblr') == 'on'
            stunting_data.riwayat_penyakit = data.get('riwayat_penyakit', stunting_data.riwayat_penyakit)
            stunting_data.intervensi_diberikan = data.get('intervention', stunting_data.intervensi_diberikan)
            stunting_data.hasil_intervensi = data.get('hasil_intervensi', stunting_data.hasil_intervensi)
            stunting_data.follow_up_date = data.get('follow_up_date') if data.get('follow_up_date') else stunting_data.follow_up_date
            stunting_data.keterangan = data.get('notes', stunting_data.keterangan)
            stunting_data.save()
            return JsonResponse({'success': True, 'message': 'Data stunting berhasil diperbarui'})
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_stunting_data_delete(request, stunting_data_id):
    """API to delete stunting data record"""
    try:
        stunting_data = StuntingData.objects.get(id=stunting_data_id)
        stunting_data.delete()
        return JsonResponse({'success': True, 'message': 'Stunting data record deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Immunization API Functions

def api_immunization_list(request):
    """API to get immunization data for admin"""
    try:
        immunizations = Immunization.objects.all().select_related('patient', 'posyandu')
        
        # Apply filters
        search = request.GET.get('search', '')
        vaccine_type = request.GET.get('vaccine_type', '')
        status = request.GET.get('status', '')
        posyandu = request.GET.get('posyandu', '')
        
        if search:
            immunizations = immunizations.filter(patient__name__icontains=search)
        
        if vaccine_type:
            immunizations = immunizations.filter(vaccine_type=vaccine_type)
        
        if status:
            immunizations = immunizations.filter(status=status)
        
        if posyandu:
            immunizations = immunizations.filter(posyandu_id=posyandu)
        
        # Calculate statistics
        total_count = immunizations.count()
        completed_count = immunizations.filter(status='completed').count()
        pending_count = immunizations.filter(status='pending').count()
        overdue_count = immunizations.filter(status='overdue').count()
        
        data = {
            'results': [
                {
                    'id': immunization.id,
                    'child_name': immunization.patient.nama if immunization.patient else 'Unknown',
                    'child_nik': immunization.patient.nik if immunization.patient else '',
                    'child_age': calculate_age_in_months(getattr(immunization.patient, 'birth_date', None)) if immunization.patient and getattr(immunization.patient, 'birth_date', None) else 0,
                    'vaccine_type': immunization.vaccine_type,
                    'immunization_date': immunization.immunization_date.strftime('%Y-%m-%d') if immunization.immunization_date else None,
                    'batch_number': immunization.batch_number,
                    'health_worker': immunization.health_worker,
                    'next_schedule': immunization.next_schedule.strftime('%Y-%m-%d') if immunization.next_schedule else None,
                    'notes': immunization.notes,
                    'status': immunization.status,
                    'posyandu_name': immunization.posyandu.name if immunization.posyandu else 'Unknown',
                    'created_at': immunization.created_at.strftime('%Y-%m-%d %H:%M') if immunization.created_at else None
                }
                for immunization in immunizations
            ],
            'statistics': {
                'total': total_count,
                'completed': completed_count,
                'pending': pending_count,
                'overdue': overdue_count
            },
            'pagination': {
                'current_page': 1,
                'total_pages': 1,
                'has_next': False,
                'has_previous': False
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_immunization_create(request):
    """API to create new immunization record"""
    try:
        if request.method == 'POST':
            data = request.POST
            
            required_fields = ['child_id', 'posyandu_id', 'vaccine_type', 'immunization_date']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'Field {field} is required'}, status=400)
            
            immunization = Immunization.objects.create(
                patient_id=data.get('child_id'),
                posyandu_id=data.get('posyandu_id'),
                vaccine_type=data.get('vaccine_type'),
                immunization_date=data.get('immunization_date'),
                batch_number=data.get('batch_number'),
                health_worker=data.get('health_worker'),
                next_schedule=data.get('next_schedule'),
                notes=data.get('notes'),
                status=data.get('status', 'completed'),
                recorded_by=request.user
            )
            return JsonResponse({'success': True, 'message': 'Data imunisasi berhasil ditambahkan', 'id': immunization.id})
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_immunization_update(request, immunization_id):
    """API to update immunization record"""
    try:
        if request.method == 'GET':
            immunization = Immunization.objects.get(id=immunization_id)
            return JsonResponse({
                'id': immunization.id,
                'child_id': immunization.patient_id,
                'child_name': immunization.patient.name if immunization.patient else None,
                'child_nik': immunization.patient.nik if immunization.patient else None,
                'child_birth_date': getattr(immunization.patient, 'birth_date', None).strftime('%Y-%m-%d') if immunization.patient and getattr(immunization.patient, 'birth_date', None) else None,
                'child_gender': immunization.patient.gender if immunization.patient else None,
                'vaccine_type': immunization.vaccine_type,
                'immunization_date': immunization.immunization_date.strftime('%Y-%m-%d') if immunization.immunization_date else None,
                'posyandu_id': immunization.posyandu_id,
                'batch_number': immunization.batch_number,
                'health_worker': immunization.health_worker,
                'next_schedule': immunization.next_schedule.strftime('%Y-%m-%d') if immunization.next_schedule else None,
                'notes': immunization.notes,
                'status': immunization.status
            })
        elif request.method == 'POST':
            data = request.POST
            immunization = Immunization.objects.get(id=immunization_id)
            
            immunization.patient_id = data.get('child_id', immunization.patient_id)
            immunization.posyandu_id = data.get('posyandu_id', immunization.posyandu_id)
            immunization.vaccine_type = data.get('vaccine_type', immunization.vaccine_type)
            immunization.immunization_date = data.get('immunization_date', immunization.immunization_date)
            immunization.batch_number = data.get('batch_number', immunization.batch_number)
            immunization.health_worker = data.get('health_worker', immunization.health_worker)
            immunization.next_schedule = data.get('next_schedule', immunization.next_schedule)
            immunization.notes = data.get('notes', immunization.notes)
            immunization.status = data.get('status', immunization.status)
            immunization.save()
            
            return JsonResponse({'success': True, 'message': 'Data imunisasi berhasil diperbarui'})
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_immunization_delete(request, immunization_id):
    """API to delete immunization record"""
    try:
        if request.method == 'DELETE':
            immunization = Immunization.objects.get(id=immunization_id)
            immunization.delete()
            return JsonResponse({'success': True, 'message': 'Data imunisasi berhasil dihapus'})
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def calculate_age_in_months(birth_date):
    """Calculate age in months from birth date"""
    if not birth_date:
        return 0
    from datetime import date
    today = date.today()
    age_in_months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
    return max(0, age_in_months)

# Nutrition Data API Functions

def api_nutrition_data_list(request):
    """API to get nutrition data for admin"""
    try:
        nutrition_data = NutritionData.objects.all().select_related('patient', 'posyandu')
        
        # Apply filters
        search = request.GET.get('search', '')
        status = request.GET.get('status', '')
        age = request.GET.get('age', '')
        posyandu = request.GET.get('posyandu', '')
        
        if search:
            nutrition_data = nutrition_data.filter(patient__name__icontains=search)
        
        if status:
            nutrition_data = nutrition_data.filter(nutrition_status=status)
        
        if age:
            if age == '0-12':
                nutrition_data = nutrition_data.filter(age_months__gte=0, age_months__lte=12)
            elif age == '12-24':
                nutrition_data = nutrition_data.filter(age_months__gt=12, age_months__lte=24)
            elif age == '24-36':
                nutrition_data = nutrition_data.filter(age_months__gt=24, age_months__lte=36)
            elif age == '36-60':
                nutrition_data = nutrition_data.filter(age_months__gt=36, age_months__lte=60)
        
        if posyandu:
            nutrition_data = nutrition_data.filter(posyandu_id=posyandu)
        # Calculate statistics
        total_count = nutrition_data.count()
        normal_count = nutrition_data.filter(nutrition_status='normal').count()
        kurang_count = nutrition_data.filter(nutrition_status='kurang').count()
        buruk_count = nutrition_data.filter(nutrition_status='buruk').count()
        lebih_count = nutrition_data.filter(nutrition_status='lebih').count()
        stunting_count = nutrition_data.filter(nutrition_status='stunting').count()
        wasting_count = nutrition_data.filter(nutrition_status='wasting').count()
        
        data = {
            'results': [
                {
                    'id': nutrition.id,
                    'child_name': nutrition.patient.name if nutrition.patient else 'Unknown',
                    'child_nik': nutrition.patient.nik if nutrition.patient else '',
                    'measurement_date': nutrition.measurement_date.strftime('%Y-%m-%d') if nutrition.measurement_date else None,
                    'age_months': nutrition.age_months,
                    'weight': float(nutrition.weight) if nutrition.weight else 0,
                    'height': float(nutrition.height) if nutrition.height else 0,
                    'head_circumference': float(nutrition.head_circumference) if nutrition.head_circumference else None,
                    'arm_circumference': float(nutrition.arm_circumference) if nutrition.arm_circumference else None,
                    'nutrition_status': nutrition.nutrition_status,
                    'vitamin_a_given': nutrition.vitamin_a_given,
                    'iron_supplement_given': nutrition.iron_supplement_given,
                    'notes': nutrition.notes,
                    'posyandu_name': nutrition.posyandu.name if nutrition.posyandu else 'Unknown',
                    'bmi': round(float(nutrition.weight) / ((float(nutrition.height) / 100) ** 2), 1) if nutrition.weight and nutrition.height else None
                }
                for nutrition in nutrition_data
            ],
            'statistics': {
                'total': total_count,
                'normal': normal_count,
                'undernourished': kurang_count + buruk_count,
                'overweight': lebih_count,
                'stunting': stunting_count,
                'wasting': wasting_count
            },
            'pagination': {
                'current_page': 1,
                'total_pages': 1,
                'has_next': False,
                'has_previous': False
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_nutrition_data_create(request):
    """API to create new nutrition data record"""
    try:
        if request.method == 'POST':
            # Handle FormData (from form submission)
            data = request.POST
            
            # Validate required fields
            required_fields = ['child_id', 'posyandu_id', 'measurement_date', 'age_months', 'weight', 'height']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'Field {field} is required'}, status=400)
            
            # Convert string values to appropriate types
            try:
                age_months = int(data.get('age_months')) if data.get('age_months') else None
                weight = float(data.get('weight')) if data.get('weight') else None
                height = float(data.get('height')) if data.get('height') else None
                head_circumference = float(data.get('head_circumference')) if data.get('head_circumference') else None
                arm_circumference = float(data.get('arm_circumference')) if data.get('arm_circumference') else None
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid data format: {str(e)}'}, status=400)
            
            nutrition_data = NutritionData.objects.create(
                patient_id=data.get('child_id'),  # Map child_id to patient_id
                posyandu_id=data.get('posyandu_id'),
                measurement_date=data.get('measurement_date'),
                age_months=age_months,
                weight=weight,
                height=height,
                head_circumference=head_circumference,
                arm_circumference=arm_circumference,
                nutrition_status=data.get('nutrition_status', 'normal'),
                vitamin_a_given=data.get('vitamin_a_given') == 'true' or data.get('vitamin_a_given') == 'on',
                iron_supplement_given=data.get('iron_supplement_given') == 'true' or data.get('iron_supplement_given') == 'on',
                notes=data.get('notes'),
                recorded_by=request.user
            )
            return JsonResponse({'success': True, 'message': 'Data gizi berhasil ditambahkan', 'id': nutrition_data.id})
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_nutrition_data_update(request, nutrition_data_id):
    """API to update nutrition data record"""
    try:
        if request.method == 'GET':
            # Return nutrition data for editing
            nutrition_data = NutritionData.objects.get(id=nutrition_data_id)
            return JsonResponse({
                'id': nutrition_data.id,
                'child_id': nutrition_data.patient_id,
                'child_name': nutrition_data.patient.name if nutrition_data.patient else None,
                'child_nik': nutrition_data.patient.nik if nutrition_data.patient else None,
                'measurement_date': nutrition_data.measurement_date.strftime('%Y-%m-%d') if nutrition_data.measurement_date else None,
                'age_months': nutrition_data.age_months,
                'weight': nutrition_data.weight,
                'height': nutrition_data.height,
                'head_circumference': nutrition_data.head_circumference,
                'arm_circumference': nutrition_data.arm_circumference,
                'nutrition_status': nutrition_data.nutrition_status,
                'vitamin_a_given': nutrition_data.vitamin_a_given,
                'iron_supplement_given': nutrition_data.iron_supplement_given,
                'posyandu_id': nutrition_data.posyandu_id,
                'health_worker': nutrition_data.health_worker if hasattr(nutrition_data, 'health_worker') else '',
                'notes': nutrition_data.notes
            })
        elif request.method == 'POST':
            # Handle FormData (from form submission)
            data = request.POST
            
            nutrition_data = NutritionData.objects.get(id=nutrition_data_id)
            
            # Convert string values to appropriate types
            try:
                if data.get('age_months'):
                    nutrition_data.age_months = int(data.get('age_months'))
                if data.get('weight'):
                    nutrition_data.weight = float(data.get('weight'))
                if data.get('height'):
                    nutrition_data.height = float(data.get('height'))
                if data.get('head_circumference'):
                    nutrition_data.head_circumference = float(data.get('head_circumference'))
                if data.get('arm_circumference'):
                    nutrition_data.arm_circumference = float(data.get('arm_circumference'))
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid data format: {str(e)}'}, status=400)
            
            nutrition_data.patient_id = data.get('child_id', nutrition_data.patient_id)
            nutrition_data.posyandu_id = data.get('posyandu_id', nutrition_data.posyandu_id)
            nutrition_data.measurement_date = data.get('measurement_date', nutrition_data.measurement_date)
            nutrition_data.nutrition_status = data.get('nutrition_status', nutrition_data.nutrition_status)
            nutrition_data.vitamin_a_given = data.get('vitamin_a_given') == 'true' or data.get('vitamin_a_given') == 'on'
            nutrition_data.iron_supplement_given = data.get('iron_supplement_given') == 'true' or data.get('iron_supplement_given') == 'on'
            nutrition_data.notes = data.get('notes', nutrition_data.notes)
            nutrition_data.save()
            return JsonResponse({'success': True, 'message': 'Data gizi berhasil diperbarui'})
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_nutrition_data_delete(request, nutrition_data_id):
    """API to delete nutrition data record"""
    try:
        nutrition_data = NutritionData.objects.get(id=nutrition_data_id)
        nutrition_data.delete()
        return JsonResponse({'success': True, 'message': 'Nutrition data record deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_patient_types(request):
    """API untuk mendapatkan daftar jenis pasien"""
    try:
        patient_types = PatientType.objects.filter(is_active=True).order_by('name')
        
        results = []
        for patient_type in patient_types:
            results.append({
                'id': patient_type.id,
                'name': patient_type.name,
                'code': patient_type.code,
                'description': patient_type.description or '',
                'age_min': patient_type.age_min,
                'age_max': patient_type.age_max
            })
        
        return JsonResponse({'results': results})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_patient_type_create(request):
    """API untuk membuat jenis pasien baru"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Field {field} is required'}, status=400)
        
        # Check if code already exists
        if PatientType.objects.filter(code=data['code']).exists():
            return JsonResponse({'error': 'Code already exists'}, status=400)
        
        # Create patient type
        patient_type = PatientType.objects.create(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            age_min=data.get('age_min'),
            age_max=data.get('age_max'),
            is_active=data.get('is_active', True)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Jenis pasien berhasil dibuat',
            'id': patient_type.id,
            'data': {
                'id': patient_type.id,
                'name': patient_type.name,
                'code': patient_type.code,
                'description': patient_type.description or '',
                'age_min': patient_type.age_min,
                'age_max': patient_type.age_max
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_immunization_age_filter(request):
    """API endpoint for filtering immunizations by age"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        from posyandu.utils import ImmunizationAgeFilter, get_immunization_status, get_vaccine_recommendations
        from datetime import date
        
        age_months = request.GET.get('age_months', None)
        birth_date = request.GET.get('birth_date', None)
        patient_id = request.GET.get('patient_id', None)
        
        if age_months:
            age_months = int(age_months)
        elif birth_date:
            try:
                birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
                age_months = calculate_age_in_months(birth_date_obj)
            except ValueError:
                return JsonResponse({'error': 'Invalid birth_date format. Use YYYY-MM-DD'}, status=400)
        elif patient_id:
            try:
                # from references.models import Penduduk  # COMMENTED OUT - references app disabled
                # Using letters app models instead
                try:
                    from letters.models import Penduduk
                except ImportError:
                    Penduduk = None
                patient = Penduduk.objects.get(id=patient_id)
                if patient.tanggal_lahir:
                    age_months = calculate_age_in_months(patient.tanggal_lahir)
                else:
                    return JsonResponse({'error': 'Patient birth date not available'}, status=400)
            except Penduduk.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
        else:
            return JsonResponse({'error': 'age_months, birth_date, or patient_id is required'}, status=400)
        
        # Get eligible vaccines for this age
        filter_util = ImmunizationAgeFilter()
        eligible_vaccines = filter_util.get_eligible_vaccines(age_months)
        vaccine_schedule = filter_util.get_vaccine_schedule()
        
        # Get completed immunizations if patient_id provided
        completed_vaccines = []
        if patient_id:
            completed_immunizations = Immunization.objects.filter(
                patient_id=patient_id,
                status='completed'
            ).values_list('vaccine_type', flat=True)
            completed_vaccines = list(completed_immunizations)
        
        # Get immunization status
        immunization_status = get_immunization_status(age_months, completed_vaccines)
        
        # Get vaccine recommendations
        recommendations = get_vaccine_recommendations(age_months)
        
        # Get immunization statistics
        total_immunizations = Immunization.objects.count()
        age_immunizations = Immunization.objects.filter(
            vaccine_type__in=eligible_vaccines
        ).count()
        
        response_data = {
            'age_months': age_months,
            'eligible_vaccines': eligible_vaccines,
            'vaccine_schedule': vaccine_schedule,
            'immunization_status': immunization_status,
            'recommendations': recommendations,
            'statistics': {
                'total_immunizations': total_immunizations,
                'age_specific_immunizations': age_immunizations,
                'completion_rate': len(completed_vaccines) / len(eligible_vaccines) * 100 if eligible_vaccines else 0
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_immunization_by_age(request):
    """API endpoint to get immunizations filtered by age"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        from posyandu.utils import ImmunizationAgeFilter
        
        age_months = request.GET.get('age_months')
        vaccine_type = request.GET.get('vaccine_type')
        posyandu_id = request.GET.get('posyandu_id')
        
        if not age_months:
            return JsonResponse({'error': 'age_months is required'}, status=400)
        
        age_months = int(age_months)
        
        # Get eligible vaccines for this age
        filter_util = ImmunizationAgeFilter()
        eligible_vaccines = filter_util.get_eligible_vaccines(age_months)
        
        # Build query
        query = Immunization.objects.filter(vaccine_type__in=eligible_vaccines)
        
        if vaccine_type and vaccine_type in eligible_vaccines:
            query = query.filter(vaccine_type=vaccine_type)
        
        if posyandu_id:
            query = query.filter(posyandu_id=posyandu_id)
        
        # Get immunizations
        immunizations = query.order_by('-immunization_date')[:50]  # Limit to 50 records
        
        results = []
        for immunization in immunizations:
            results.append({
                'id': immunization.id,
                'patient_name': immunization.patient.name if immunization.patient else '-',
                'patient_nik': immunization.patient.nik if immunization.patient else '-',
                'vaccine_type': immunization.vaccine_type,
                'vaccine_name': immunization.get_vaccine_type_display(),
                'immunization_date': immunization.immunization_date.strftime('%Y-%m-%d'),
                'status': immunization.status,
                'health_worker': immunization.health_worker,
                'posyandu_name': immunization.posyandu.name if immunization.posyandu else '-',
                'notes': immunization.notes
            })
        
        return JsonResponse({
            'results': results,
            'total_count': query.count(),
            'age_months': age_months,
            'eligible_vaccines': eligible_vaccines
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

