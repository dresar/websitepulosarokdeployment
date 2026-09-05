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
    StuntingData
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

@login_required
def admin_panel_dashboard(request):
    """Dashboard admin panel untuk posyandu"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    # Statistics
    total_locations = PosyanduLocation.objects.count()
    active_locations = PosyanduLocation.objects.filter(is_active=True).count()
    total_schedules = PosyanduSchedule.objects.count()
    total_health_records = HealthRecord.objects.count()
    total_immunizations = Immunization.objects.count()
    total_nutrition_data = NutritionData.objects.count()
    total_kaders = PosyanduKader.objects.count()
    total_ibu_hamil = IbuHamil.objects.count()
    total_stunting_data = StuntingData.objects.count()
    
    # Recent activities
    recent_health_records = HealthRecord.objects.order_by('-created_at')[:5]
    recent_immunizations = Immunization.objects.order_by('-created_at')[:5]
    recent_schedules = PosyanduSchedule.objects.order_by('-created_at')[:5]
    
    # Monthly statistics
    current_month = datetime.now().replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    current_month_records = HealthRecord.objects.filter(
        created_at__gte=current_month
    ).count()
    last_month_records = HealthRecord.objects.filter(
        created_at__gte=last_month,
        created_at__lt=current_month
    ).count()
    
    # Health statistics
    avg_weight = NutritionData.objects.aggregate(Avg('weight'))['weight__avg'] or 0
    avg_height = NutritionData.objects.aggregate(Avg('height'))['height__avg'] or 0
    stunting_count = StuntingData.objects.filter(status_stunting='stunting').count()
    
    context = {
        'total_locations': total_locations,
        'active_locations': active_locations,
        'total_schedules': total_schedules,
        'total_health_records': total_health_records,
        'total_immunizations': total_immunizations,
        'total_nutrition_data': total_nutrition_data,
        'total_kaders': total_kaders,
        'total_ibu_hamil': total_ibu_hamil,
        'total_stunting_data': total_stunting_data,
        'recent_health_records': recent_health_records,
        'recent_immunizations': recent_immunizations,
        'recent_schedules': recent_schedules,
        'current_month_records': current_month_records,
        'last_month_records': last_month_records,
        'avg_weight': round(avg_weight, 2),
        'avg_height': round(avg_height, 2),
        'stunting_count': stunting_count,
        'page_title': 'Dashboard Posyandu',
        'page_subtitle': 'Kelola data kesehatan masyarakat'
    }
    return render(request, 'admin_panel/posyandu/dashboard.html', context)

# Location Management Views

@login_required
def admin_panel_location_list(request):
    """List semua lokasi posyandu untuk admin panel"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    locations = PosyanduLocation.objects.all()
    
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
    
    locations = locations.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(locations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'page_title': 'Lokasi Posyandu',
        'page_subtitle': 'Kelola lokasi posyandu'
    }
    return render(request, 'admin_panel/posyandu/locations.html', context)


@login_required
def admin_panel_location_create(request):
    """Create lokasi posyandu baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            location = PosyanduLocation.objects.create(
                name=data.get('name'),
                address=data.get('address'),
                coordinator_id=data.get('coordinator_id'),
                contact_phone=data.get('contact_phone', ''),
                capacity=data.get('capacity', 50),
                established_date=data.get('established_date'),
                facilities=data.get('facilities', ''),
                is_active=data.get('is_active', True)
            )
            messages.success(request, 'Lokasi posyandu berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': location.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    context = {
        'page_title': 'Tambah Lokasi Posyandu',
        'page_subtitle': 'Tambah lokasi posyandu baru'
    }
    return render(request, 'admin_panel/posyandu/locations_form.html', context)


@login_required
def admin_panel_location_detail(request, location_id):
    """Detail lokasi posyandu"""
    location = get_object_or_404(PosyanduLocation, id=location_id)
    schedules = PosyanduSchedule.objects.filter(location=location).order_by('-schedule_date')[:10]
    health_records = HealthRecord.objects.filter(posyandu=location).order_by('-created_at')[:10]
    
    # Statistics
    total_schedules = PosyanduSchedule.objects.filter(location=location).count()
    total_records = HealthRecord.objects.filter(posyandu=location).count()
    
    context = {
        'location': location,
        'schedules': schedules,
        'health_records': health_records,
        'total_schedules': total_schedules,
        'total_records': total_records,
        'page_title': f'Detail {location.name}',
        'page_subtitle': 'Informasi detail lokasi posyandu'
    }
    return render(request, 'admin_panel/posyandu/locations_detail.html', context)


@login_required
def admin_panel_location_update(request, location_id):
    """Update lokasi posyandu"""
    print(f"DEBUG: admin_panel_location_update called with location_id={location_id}")
    location = get_object_or_404(PosyanduLocation, id=location_id)
    print(f"DEBUG: Found location: {location.name}")
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            location.name = data.get('name', location.name)
            location.address = data.get('address', location.address)
            location.coordinator_id = data.get('coordinator_id', location.coordinator_id)
            location.contact_phone = data.get('contact_phone', location.contact_phone)
            location.capacity = data.get('capacity', location.capacity)
            location.established_date = data.get('established_date', location.established_date)
            location.facilities = data.get('facilities', location.facilities)
            location.is_active = data.get('is_active', location.is_active)
            location.save()
            
            messages.success(request, 'Lokasi posyandu berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Prepare location data for template
    location_data = {
        'id': location.id,
        'name': location.name or '',
        'code': getattr(location, 'code', '') or '',
        'address': location.address or '',
        'description': getattr(location, 'description', '') or '',
        'capacity': location.capacity or 0,
        'status': 'active' if location.is_active else 'inactive',
        'phone': location.contact_phone or '',
        'email': getattr(location, 'email', '') or '',
        'latitude': str(getattr(location, 'latitude', '')) if getattr(location, 'latitude', None) else '',
        'longitude': str(getattr(location, 'longitude', '')) if getattr(location, 'longitude', None) else '',
        'amenities': location.facilities or '',
        'notes': getattr(location, 'notes', '') or '',
        'image': location.image.url if location.image else '/static/images/defaults/placeholder.svg',
        'is_edit': True
    }
    
    print(f"DEBUG: Location data for template: {location_data}")
    
    context = {
        'location': location,
        'location_data': location_data,
        'page_title': f'Edit {location.name}',
        'page_subtitle': 'Edit lokasi posyandu'
    }
    
    print(f"DEBUG: Context keys: {list(context.keys())}")
    print(f"DEBUG: location_data in context: {'location_data' in context}")
    
    return render(request, 'admin_panel/posyandu/locations_form.html', context)


@login_required
def admin_panel_location_delete(request, location_id):
    """Delete lokasi posyandu"""
    try:
        location = get_object_or_404(PosyanduLocation, id=location_id)
    except:
        # Location already deleted or doesn't exist
        messages.warning(request, 'Lokasi posyandu tidak ditemukan atau sudah dihapus.')
        return redirect('posyandu:locations')
    
    if request.method == 'POST':
        try:
            location_name = location.name
            location.delete()
            messages.success(request, f'Lokasi posyandu "{location_name}" berhasil dihapus!')
            return redirect('posyandu:locations')
        except Exception as e:
            messages.error(request, f'Error menghapus lokasi: {str(e)}')
            return redirect('posyandu:locations')
    
    # GET request - show confirmation page
    context = {
        'location': location,
        'page_title': 'Hapus Lokasi Posyandu',
        'page_subtitle': f'Konfirmasi penghapusan {location.name}'
    }
    return render(request, 'admin_panel/posyandu/location_delete_confirm.html', context)


@login_required
def admin_panel_schedule_list(request):
    """List semua jadwal posyandu"""
    search_query = request.GET.get('search', '')
    location_filter = request.GET.get('location', '')
    date_filter = request.GET.get('date', '')
    
    schedules = PosyanduSchedule.objects.select_related('location')
    
    if search_query:
        schedules = schedules.filter(
            Q(title__icontains=search_query) |
            Q(location__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if location_filter:
        schedules = schedules.filter(location_id=location_filter)
    
    if date_filter:
        schedules = schedules.filter(schedule_date=date_filter)
    
    schedules = schedules.order_by('-schedule_date', '-start_time')
    
    # Pagination
    paginator = Paginator(schedules, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'locations': locations,
        'search_query': search_query,
        'location_filter': location_filter,
        'date_filter': date_filter,
        'page_title': 'Jadwal Posyandu',
        'page_subtitle': 'Kelola jadwal posyandu'
    }
    return render(request, 'admin_panel/posyandu/schedules.html', context)


@login_required
def admin_panel_reports(request):
    """Laporan dan analitik posyandu"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    # Date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Health records statistics
    health_records = HealthRecord.objects.filter(
        visit_date__range=[start_date, end_date]
    )
    
    # Immunization statistics
    immunizations = Immunization.objects.filter(
        immunization_date__range=[start_date, end_date]
    )
    
    # Nutrition statistics
    nutrition_data = NutritionData.objects.filter(
        measurement_date__range=[start_date, end_date]
    )
    
    # Stunting statistics
    stunting_data = StuntingData.objects.filter(
        tanggal_ukur__range=[start_date, end_date]
    )
    
    # Statistics by location
    location_stats = PosyanduLocation.objects.annotate(
        health_record_count=Count('healthrecord'),
        schedule_count=Count('schedules')
    )
    
    # Monthly trends
    monthly_health_records = []
    monthly_immunizations = []
    for i in range(12):
        month_start = datetime.now().replace(day=1, month=i+1 if i < 12 else 12)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        health_count = HealthRecord.objects.filter(
            visit_date__range=[month_start, month_end]
        ).count()
        
        immunization_count = Immunization.objects.filter(
            immunization_date__range=[month_start, month_end]
        ).count()
        
        monthly_health_records.append(health_count)
        monthly_immunizations.append(immunization_count)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'health_records_count': health_records.count(),
        'immunizations_count': immunizations.count(),
        'nutrition_data_count': nutrition_data.count(),
        'stunting_data_count': stunting_data.count(),
        'location_stats': location_stats,
        'monthly_health_records': monthly_health_records,
        'monthly_immunizations': monthly_immunizations,
        'avg_weight': nutrition_data.aggregate(Avg('weight'))['weight__avg'] or 0,
        'avg_height': nutrition_data.aggregate(Avg('height'))['height__avg'] or 0,
        'stunting_count': stunting_data.filter(status_stunting='stunting').count(),
        'page_title': 'Laporan Posyandu',
        'page_subtitle': 'Laporan dan analitik posyandu'
    }
    return render(request, 'admin_panel/posyandu/reports.html', context)

# Export Data Views

@login_required
def admin_panel_export_health_records(request):
    """Export data rekam kesehatan ke CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="health_records.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nama Pasien', 'NIK', 'Lokasi', 'Tanggal Pemeriksaan',
        'Berat Badan', 'Tinggi Badan', 'Tekanan Darah', 'Suhu',
        'Diagnosis', 'Pengobatan', 'Catatan'
    ])
    
    records = HealthRecord.objects.select_related('patient', 'posyandu')
    for record in records:
        writer.writerow([
            record.id,
            record.patient.nama,
            record.patient.nik,
            record.posyandu.name,
            record.visit_date,
            record.weight,
            record.height,
            record.blood_pressure,
            record.temperature,
            record.diagnosis,
            record.treatment,
            record.complaints
        ])
    
    return response


@login_required
def admin_panel_export_immunizations(request):
    """Export data imunisasi ke CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="immunizations.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nama Pasien', 'NIK', 'Nama Vaksin', 'Tanggal Vaksinasi',
        'Nomor Batch', 'Petugas Vaksin', 'Catatan'
    ])
    
    immunizations = Immunization.objects.select_related('patient')
    for immunization in immunizations:
        writer.writerow([
            immunization.id,
            immunization.patient.nama,
            immunization.patient.nik,
            immunization.vaccine_type,
            immunization.immunization_date,
            immunization.batch_number,
            immunization.health_worker,
            immunization.status
        ])
    
    return response

# Bulk Operations

@csrf_exempt
def admin_panel_api_locations(request):
    """API untuk mendapatkan daftar lokasi posyandu"""
    from django.core.paginator import Paginator
    from django.db.models import Sum
    
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    capacity = request.GET.get('capacity', '')
    page = int(request.GET.get('page', 1))
    
    locations = PosyanduLocation.objects.all().order_by('name')
    
    # Apply search filter
    if search:
        locations = locations.filter(
            Q(name__icontains=search) |
            Q(address__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Apply status filter
    if status:
        if status == 'active':
            locations = locations.filter(is_active=True)
        elif status == 'inactive':
            locations = locations.filter(is_active=False)
        elif status == 'maintenance':
            locations = locations.filter(is_active=False)  # Assuming maintenance means inactive
    
    # Apply capacity filter
    if capacity:
        if capacity == 'small':
            locations = locations.filter(capacity__lt=50)
        elif capacity == 'medium':
            locations = locations.filter(capacity__gte=50, capacity__lte=100)
        elif capacity == 'large':
            locations = locations.filter(capacity__gt=100)
    
    # Calculate statistics
    total_locations = locations.count()
    active_locations = locations.filter(is_active=True).count()
    maintenance_locations = locations.filter(is_active=False).count()
    total_capacity = locations.aggregate(total=Sum('capacity'))['total'] or 0
    
    # Pagination
    paginator = Paginator(locations, 12)
    page_obj = paginator.get_page(page)
    
    locations_data = []
    for location in page_obj:
        locations_data.append({
            'id': location.id,
            'name': location.name,
            'address': location.address,
            'code': getattr(location, 'code', ''),
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
        })
    
    data = {
        'results': locations_data,
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
    
    return JsonResponse(data, safe=False)


@csrf_exempt
def admin_panel_api_statistics(request):
    """API untuk mendapatkan statistik posyandu"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    # Basic statistics
    stats = {
        'total_locations': PosyanduLocation.objects.count(),
        'active_locations': PosyanduLocation.objects.filter(is_active=True).count(),
        'total_health_records': HealthRecord.objects.count(),
        'total_immunizations': Immunization.objects.count(),
        'total_nutrition_data': NutritionData.objects.count(),
        'total_kaders': PosyanduKader.objects.count(),
        'total_ibu_hamil': IbuHamil.objects.count(),
        'total_stunting_data': StuntingData.objects.count(),
    }
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    stats['recent_health_records'] = HealthRecord.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    stats['recent_immunizations'] = Immunization.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    # Health statistics
    stats['avg_weight'] = float(NutritionData.objects.aggregate(Avg('weight'))['weight__avg'] or 0)
    stats['avg_height'] = float(NutritionData.objects.aggregate(Avg('height'))['height__avg'] or 0)
    stats['stunting_count'] = StuntingData.objects.filter(status_stunting='stunting').count()
    
    return JsonResponse(stats)


@login_required
def admin_panel_api_search_residents(request):
    """API untuk mencari penduduk"""
    query = request.GET.get('q', '')
    gender = request.GET.get('gender', '')
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # from references.models import Penduduk  # COMMENTED OUT - references app disabled
    # Using letters app models instead
    try:
        from letters.models import Penduduk
    except ImportError:
        Penduduk = None
    
    residents = Penduduk.objects.filter(
        Q(name__icontains=query) | Q(nik__icontains=query)
    )
    
    if gender:
        residents = residents.filter(gender=gender)
    
    residents_data = []
    for resident in residents[:10]:
        residents_data.append({
            'id': resident.id,
            'name': resident.name,
            'nik': resident.nik,
            'gender': resident.gender,
            'age': resident.age if hasattr(resident, 'age') else None,
            'birth_date': resident.birth_date.strftime('%Y-%m-%d') if resident.birth_date else None
        })
    
    return JsonResponse({'results': residents_data})


@login_required
def admin_panel_api_monthly_stats(request):
    """API untuk mendapatkan statistik bulanan"""
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Get last 12 months
    months = []
    for i in range(12):
        month_start = datetime.now().replace(day=1, month=i+1 if i < 12 else 12)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        health_count = HealthRecord.objects.filter(
            visit_date__range=[month_start, month_end]
        ).count()
        
        immunization_count = Immunization.objects.filter(
            immunization_date__range=[month_start, month_end]
        ).count()
        
        months.append({
            'month': month_start.strftime('%Y-%m'),
            'health_records': health_count,
            'immunizations': immunization_count
        })
    
    return JsonResponse({'months': months})

# Public API Views
@csrf_exempt
@require_http_methods(["GET"])
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

@login_required
def admin_panel_health_record_create(request):
    """Create rekam kesehatan baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = HealthRecord.objects.create(
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
            messages.success(request, 'Rekam kesehatan berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': record.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'locations': locations,
        'page_title': 'Tambah Rekam Kesehatan',
        'page_subtitle': 'Tambah rekam kesehatan baru'
    }
    return render(request, 'admin_panel/posyandu/health_records_form.html', context)


@login_required
def admin_panel_health_record_update(request, record_id):
    """Update rekam kesehatan"""
    record = get_object_or_404(HealthRecord, id=record_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record.patient_id = data.get('patient_id', record.patient_id)
            record.posyandu_id = data.get('posyandu_id', record.posyandu_id)
            record.patient_type = data.get('patient_type', record.patient_type)
            record.visit_date = data.get('visit_date', record.visit_date)
            record.weight = data.get('weight', record.weight)
            record.height = data.get('height', record.height)
            record.blood_pressure = data.get('blood_pressure', record.blood_pressure)
            record.temperature = data.get('temperature', record.temperature)
            record.complaints = data.get('complaints', record.complaints)
            record.diagnosis = data.get('diagnosis', record.diagnosis)
            record.treatment = data.get('treatment', record.treatment)
            record.next_visit = data.get('next_visit', record.next_visit)
            record.save()
            
            messages.success(request, 'Rekam kesehatan berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'record': record,
        'locations': locations,
        'page_title': f'Edit Rekam Kesehatan - {record.patient.nama}',
        'page_subtitle': 'Edit rekam kesehatan'
    }
    return render(request, 'admin_panel/posyandu/health_records_form.html', context)


@login_required
def admin_panel_immunization_create(request):
    """Create data imunisasi baru"""
    if request.method == 'POST':
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
            messages.success(request, 'Data imunisasi berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': immunization.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'locations': locations,
        'page_title': 'Tambah Data Imunisasi',
        'page_subtitle': 'Tambah data imunisasi baru'
    }
    return render(request, 'admin_panel/posyandu/immunizations.html', context)


@login_required
def admin_panel_immunization_update(request, immunization_id):
    """Update data imunisasi"""
    immunization = get_object_or_404(Immunization, id=immunization_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
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
            
            messages.success(request, 'Data imunisasi berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'immunization': immunization,
        'locations': locations,
        'page_title': f'Edit Data Imunisasi - {immunization.patient.nama}',
        'page_subtitle': 'Edit data imunisasi'
    }
    return render(request, 'admin_panel/posyandu/immunizations.html', context)


@login_required
def admin_panel_nutrition_create(request):
    """Create data gizi baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nutrition = NutritionData.objects.create(
                patient_id=data.get('patient_id'),
                posyandu_id=data.get('posyandu_id'),
                tanggal_ukur=data.get('tanggal_ukur'),
                age_months=data.get('age_months'),
                weight=data.get('weight'),
                height=data.get('height'),
                head_circumference=data.get('head_circumference'),
                arm_circumference=data.get('arm_circumference'),
                nutrition_status=data.get('nutrition_status'),
                vitamin_a_given=data.get('vitamin_a_given', False),
                iron_supplement_given=data.get('iron_supplement_given', False),
                notes=data.get('notes'),
                recorded_by=request.user
            )
            messages.success(request, 'Data gizi berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': nutrition.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'locations': locations,
        'page_title': 'Tambah Data Gizi',
        'page_subtitle': 'Tambah data gizi baru'
    }
    return render(request, 'admin_panel/posyandu/nutrition_data.html', context)


@login_required
def admin_panel_nutrition_update(request, nutrition_id):
    """Update data gizi"""
    nutrition = get_object_or_404(NutritionData, id=nutrition_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nutrition.patient_id = data.get('patient_id', nutrition.patient_id)
            nutrition.posyandu_id = data.get('posyandu_id', nutrition.posyandu_id)
            nutrition.measurement_date = data.get('measurement_date', nutrition.measurement_date)
            nutrition.age_months = data.get('age_months', nutrition.age_months)
            nutrition.weight = data.get('weight', nutrition.weight)
            nutrition.height = data.get('height', nutrition.height)
            nutrition.head_circumference = data.get('head_circumference', nutrition.head_circumference)
            nutrition.arm_circumference = data.get('arm_circumference', nutrition.arm_circumference)
            nutrition.nutrition_status = data.get('nutrition_status', nutrition.nutrition_status)
            nutrition.vitamin_a_given = data.get('vitamin_a_given', nutrition.vitamin_a_given)
            nutrition.iron_supplement_given = data.get('iron_supplement_given', nutrition.iron_supplement_given)
            nutrition.notes = data.get('notes', nutrition.notes)
            nutrition.save()
            
            messages.success(request, 'Data gizi berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'nutrition': nutrition,
        'locations': locations,
        'page_title': f'Edit Data Gizi - {nutrition.patient.nama}',
        'page_subtitle': 'Edit data gizi'
    }
    return render(request, 'admin_panel/posyandu/nutrition_data.html', context)


@login_required
def admin_panel_kader_create(request):
    """Create kader posyandu baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kader = PosyanduKader.objects.create(
                penduduk_id=data.get('penduduk_id'),
                posyandu_id=data.get('posyandu_id'),
                jabatan=data.get('jabatan'),
                nomor_hp=data.get('nomor_hp'),
                tanggal_mulai=data.get('tanggal_mulai'),
                tanggal_selesai=data.get('tanggal_selesai'),
                status=data.get('status', 'aktif'),
                keterangan=data.get('keterangan')
            )
            messages.success(request, 'Kader posyandu berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': kader.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True).order_by('name')
    context = {
        'posyandu_locations': posyandu_locations,
        'page_title': 'Tambah Kader Posyandu',
        'page_subtitle': 'Tambah kader posyandu baru'
    }
    return render(request, 'admin_panel/posyandu/kader_form.html', context)


@login_required
def admin_panel_kader_update(request, kader_id):
    """Update kader posyandu"""
    kader = get_object_or_404(PosyanduKader, id=kader_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kader.penduduk_id = data.get('penduduk_id', kader.penduduk_id)
            kader.posyandu_id = data.get('posyandu_id', kader.posyandu_id)
            kader.jabatan = data.get('jabatan', kader.jabatan)
            kader.nomor_hp = data.get('nomor_hp', kader.nomor_hp)
            kader.tanggal_mulai = data.get('tanggal_mulai', kader.tanggal_mulai)
            kader.tanggal_selesai = data.get('tanggal_selesai', kader.tanggal_selesai)
            kader.status = data.get('status', kader.status)
            kader.keterangan = data.get('keterangan', kader.keterangan)
            kader.save()
            
            messages.success(request, 'Kader posyandu berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True).order_by('name')
    context = {
        'kader': kader,
        'posyandu_locations': posyandu_locations,
        'page_title': f'Edit Kader Posyandu - {kader.penduduk.nama}',
        'page_subtitle': 'Edit kader posyandu'
    }
    return render(request, 'admin_panel/posyandu/kader_form.html', context)


@login_required
def admin_panel_ibu_hamil_create(request):
    """Create data ibu hamil baru"""
    context = {
        'page_title': 'Tambah Data Ibu Hamil',
        'page_subtitle': 'Form tambah data ibu hamil baru'
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil_form.html', context)


@login_required
def admin_panel_ibu_hamil_update(request, ibu_hamil_id):
    """Update data ibu hamil"""
    ibu_hamil = get_object_or_404(IbuHamil, id=ibu_hamil_id)
    
    context = {
        'ibu_hamil': ibu_hamil,
        'page_title': f'Edit Data Ibu Hamil - {ibu_hamil.penduduk.nama if ibu_hamil.penduduk else "Unknown"}',
        'page_subtitle': 'Form edit data ibu hamil'
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil_form.html', context)


@login_required
def admin_panel_stunting_create(request):
    """Create data stunting baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stunting = StuntingData.objects.create(
                balita_id=data.get('balita_id'),
                posyandu_id=data.get('posyandu_id'),
                tanggal_ukur=data.get('tanggal_ukur'),
                usia_bulan=data.get('usia_bulan'),
                tinggi_badan=data.get('tinggi_badan'),
                berat_badan=data.get('berat_badan'),
                z_score_tb_u=data.get('z_score_tb_u'),
                z_score_bb_u=data.get('z_score_bb_u'),
                z_score_bb_tb=data.get('z_score_bb_tb'),
                status_stunting=data.get('status_stunting'),
                asi_eksklusif=data.get('asi_eksklusif', False),
                riwayat_bblr=data.get('riwayat_bblr', False),
                riwayat_penyakit=data.get('riwayat_penyakit'),
                intervensi_diberikan=data.get('intervensi_diberikan'),
                hasil_intervensi=data.get('hasil_intervensi'),
                follow_up_date=data.get('follow_up_date'),
                keterangan=data.get('keterangan'),
                recorded_by=request.user
            )
            messages.success(request, 'Data stunting berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': stunting.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'locations': locations,
        'page_title': 'Tambah Data Stunting',
        'page_subtitle': 'Tambah data stunting baru'
    }
    return render(request, 'admin_panel/posyandu/stunting_data.html', context)


@login_required
def admin_panel_stunting_update(request, stunting_id):
    """Update data stunting"""
    stunting = get_object_or_404(StuntingData, id=stunting_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stunting.balita_id = data.get('balita_id', stunting.balita_id)
            stunting.posyandu_id = data.get('posyandu_id', stunting.posyandu_id)
            stunting.tanggal_ukur = data.get('tanggal_ukur', stunting.tanggal_ukur)
            stunting.usia_bulan = data.get('usia_bulan', stunting.usia_bulan)
            stunting.tinggi_badan = data.get('tinggi_badan', stunting.tinggi_badan)
            stunting.berat_badan = data.get('berat_badan', stunting.berat_badan)
            stunting.z_score_tb_u = data.get('z_score_tb_u', stunting.z_score_tb_u)
            stunting.z_score_bb_u = data.get('z_score_bb_u', stunting.z_score_bb_u)
            stunting.z_score_bb_tb = data.get('z_score_bb_tb', stunting.z_score_bb_tb)
            stunting.status_stunting = data.get('status_stunting', stunting.status_stunting)
            stunting.asi_eksklusif = data.get('asi_eksklusif', stunting.asi_eksklusif)
            stunting.riwayat_bblr = data.get('riwayat_bblr', stunting.riwayat_bblr)
            stunting.riwayat_penyakit = data.get('riwayat_penyakit', stunting.riwayat_penyakit)
            stunting.intervensi_diberikan = data.get('intervensi_diberikan', stunting.intervensi_diberikan)
            stunting.hasil_intervensi = data.get('hasil_intervensi', stunting.hasil_intervensi)
            stunting.follow_up_date = data.get('follow_up_date', stunting.follow_up_date)
            stunting.keterangan = data.get('keterangan', stunting.keterangan)
            stunting.save()
            
            messages.success(request, 'Data stunting berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'stunting': stunting,
        'locations': locations,
        'page_title': f'Edit Data Stunting - {stunting.balita.nama}',
        'page_subtitle': 'Edit data stunting'
    }
    return render(request, 'admin_panel/posyandu/stunting_data.html', context)


@login_required
def admin_panel_schedule_create(request):
    """Create jadwal posyandu baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule = PosyanduSchedule.objects.create(
                location_id=data.get('location_id'),
                activity_type=data.get('activity_type'),
                title=data.get('title'),
                description=data.get('description'),
                schedule_date=data.get('schedule_date'),
                start_time=data.get('start_time'),
                end_time=data.get('end_time'),
                target_participants=data.get('target_participants', 0),
                actual_participants=data.get('actual_participants', 0),
                notes=data.get('notes'),
                is_completed=data.get('is_completed', False),
                created_by=request.user
            )
            messages.success(request, 'Jadwal posyandu berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': schedule.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    
    # Prepare empty schedule data for create
    schedule_data = {
        'id': None,
        'title': '',
        'activity_type': '',
        'schedule_date': '',
        'start_time': '',
        'end_time': '',
        'location_id': '',
        'max_participants': 0,
        'organizer': '',
        'status': 'upcoming',
        'description': '',
        'notes': '',
        'is_edit': False
    }
    
    import json
    context = {
        'schedule_data': json.dumps(schedule_data),
        'locations': locations,
        'page_title': 'Tambah Jadwal Posyandu',
        'page_subtitle': 'Tambah jadwal posyandu baru'
    }
    return render(request, 'admin_panel/posyandu/schedules_form.html', context)


@login_required
def admin_panel_schedule_update(request, schedule_id):
    """Update jadwal posyandu"""
    schedule = get_object_or_404(PosyanduSchedule, id=schedule_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule.location_id = data.get('location_id', schedule.location_id)
            schedule.activity_type = data.get('activity_type', schedule.activity_type)
            schedule.title = data.get('title', schedule.title)
            schedule.description = data.get('description', schedule.description)
            schedule.schedule_date = data.get('schedule_date', schedule.schedule_date)
            schedule.start_time = data.get('start_time', schedule.start_time)
            schedule.end_time = data.get('end_time', schedule.end_time)
            schedule.target_participants = data.get('target_participants', schedule.target_participants)
            schedule.actual_participants = data.get('actual_participants', schedule.actual_participants)
            schedule.notes = data.get('notes', schedule.notes)
            schedule.is_completed = data.get('is_completed', schedule.is_completed)
            schedule.save()
            
            messages.success(request, 'Jadwal posyandu berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    
    # Prepare schedule data for template
    schedule_data = {
        'id': schedule.id,
        'title': schedule.title or '',
        'activity_type': schedule.activity_type or '',
        'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d') if schedule.schedule_date else '',
        'start_time': schedule.start_time.strftime('%H:%M') if schedule.start_time else '',
        'end_time': schedule.end_time.strftime('%H:%M') if schedule.end_time else '',
        'location_id': schedule.location.id if schedule.location else '',
        'max_participants': schedule.target_participants or 0,
        'organizer': schedule.created_by.get_full_name() if schedule.created_by else '',
        'status': 'upcoming' if schedule.schedule_date and schedule.schedule_date > timezone.now().date() and not schedule.is_completed else
                 'ongoing' if schedule.schedule_date and schedule.schedule_date == timezone.now().date() and not schedule.is_completed else
                 'completed' if schedule.is_completed else 'cancelled',
        'description': schedule.description or '',
        'notes': schedule.notes or '',
        'is_edit': True
    }
    
    import json
    context = {
        'schedule': schedule,
        'schedule_data': json.dumps(schedule_data),
        'locations': locations,
        'page_title': f'Edit Jadwal Posyandu - {schedule.title}',
        'page_subtitle': 'Edit jadwal posyandu'
    }
    return render(request, 'admin_panel/posyandu/schedules_form.html', context)


@login_required
def admin_panel_health_record_detail(request, record_id):
    """Detail rekam kesehatan"""
    record = get_object_or_404(HealthRecord, id=record_id)
    
    context = {
        'record': record,
        'page_title': f'Detail Rekam Kesehatan - {record.patient.nama}',
        'page_subtitle': 'Detail rekam kesehatan'
    }
    return render(request, 'admin_panel/posyandu/health_records_detail.html', context)


@login_required
def admin_panel_immunization_detail(request, immunization_id):
    """Detail data imunisasi"""
    immunization = get_object_or_404(Immunization, id=immunization_id)
    
    context = {
        'immunization': immunization,
        'page_title': f'Detail Data Imunisasi - {immunization.patient.nama}',
        'page_subtitle': 'Detail data imunisasi'
    }
    return render(request, 'admin_panel/posyandu/immunization_detail.html', context)


@login_required
def admin_panel_nutrition_detail(request, nutrition_id):
    """Detail data gizi"""
    nutrition = get_object_or_404(NutritionData, id=nutrition_id)
    
    context = {
        'nutrition': nutrition,
        'page_title': f'Detail Data Gizi - {nutrition.patient.nama}',
        'page_subtitle': 'Detail data gizi'
    }
    return render(request, 'admin_panel/posyandu/nutrition_detail.html', context)


@login_required
def admin_panel_kader_detail(request, kader_id):
    """Detail kader posyandu"""
    kader = get_object_or_404(PosyanduKader, id=kader_id)
    
    context = {
        'kader': kader,
        'page_title': f'Detail Kader Posyandu - {kader.penduduk.nama}',
        'page_subtitle': 'Detail kader posyandu'
    }
    return render(request, 'admin_panel/posyandu/kader_detail.html', context)


@login_required
def admin_panel_ibu_hamil_detail(request, ibu_hamil_id):
    """Detail data ibu hamil"""
    ibu_hamil = get_object_or_404(IbuHamil, id=ibu_hamil_id)
    
    context = {
        'ibu_hamil': ibu_hamil,
        'page_title': f'Detail Ibu Hamil - {ibu_hamil.penduduk.nama if ibu_hamil.penduduk else "Unknown"}',
        'page_subtitle': 'Informasi lengkap data ibu hamil'
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil_detail.html', context)




@login_required
def admin_panel_schedule_detail(request, schedule_id):
    """Detail jadwal posyandu"""
    schedule = get_object_or_404(PosyanduSchedule, id=schedule_id)
    
    context = {
        'schedule': schedule,
        'page_title': f'Detail Jadwal Posyandu - {schedule.title}',
        'page_subtitle': 'Detail jadwal posyandu'
    }
    return render(request, 'admin_panel/posyandu/schedules_detail.html', context)

# Additional Admin Panel Views

@login_required
def admin_panel_health_record_create(request):
    """Create rekam kesehatan baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = HealthRecord.objects.create(
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
            messages.success(request, 'Rekam kesehatan berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': record.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'locations': locations,
        'page_title': 'Tambah Rekam Kesehatan',
        'page_subtitle': 'Tambah rekam kesehatan baru'
    }
    return render(request, 'admin_panel/posyandu/health_records_form.html', context)


@login_required
def admin_panel_health_record_update(request, record_id):
    """Update rekam kesehatan"""
    record = get_object_or_404(HealthRecord, id=record_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record.patient_id = data.get('patient_id', record.patient_id)
            record.posyandu_id = data.get('posyandu_id', record.posyandu_id)
            record.patient_type = data.get('patient_type', record.patient_type)
            record.visit_date = data.get('visit_date', record.visit_date)
            record.weight = data.get('weight', record.weight)
            record.height = data.get('height', record.height)
            record.blood_pressure = data.get('blood_pressure', record.blood_pressure)
            record.temperature = data.get('temperature', record.temperature)
            record.complaints = data.get('complaints', record.complaints)
            record.diagnosis = data.get('diagnosis', record.diagnosis)
            record.treatment = data.get('treatment', record.treatment)
            record.next_visit = data.get('next_visit', record.next_visit)
            record.save()
            
            messages.success(request, 'Rekam kesehatan berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'record': record,
        'locations': locations,
        'page_title': f'Edit Rekam Kesehatan - {record.patient.nama}',
        'page_subtitle': 'Edit rekam kesehatan'
    }
    return render(request, 'admin_panel/posyandu/health_records_form.html', context)


@login_required
def admin_panel_immunization_create(request):
    """Create data imunisasi baru"""
    if request.method == 'POST':
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
            messages.success(request, 'Data imunisasi berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': immunization.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'locations': locations,
        'page_title': 'Tambah Data Imunisasi',
        'page_subtitle': 'Tambah data imunisasi baru'
    }
    return render(request, 'admin_panel/posyandu/immunizations.html', context)


@login_required
def admin_panel_immunization_update(request, immunization_id):
    """Update data imunisasi"""
    immunization = get_object_or_404(Immunization, id=immunization_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
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
            
            messages.success(request, 'Data imunisasi berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'immunization': immunization,
        'locations': locations,
        'page_title': f'Edit Data Imunisasi - {immunization.patient.nama}',
        'page_subtitle': 'Edit data imunisasi'
    }
    return render(request, 'admin_panel/posyandu/immunizations.html', context)


@login_required
def admin_panel_nutrition_create(request):
    """Create data gizi baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nutrition = NutritionData.objects.create(
                patient_id=data.get('patient_id'),
                posyandu_id=data.get('posyandu_id'),
                tanggal_ukur=data.get('tanggal_ukur'),
                age_months=data.get('age_months'),
                weight=data.get('weight'),
                height=data.get('height'),
                head_circumference=data.get('head_circumference'),
                arm_circumference=data.get('arm_circumference'),
                nutrition_status=data.get('nutrition_status'),
                vitamin_a_given=data.get('vitamin_a_given', False),
                iron_supplement_given=data.get('iron_supplement_given', False),
                notes=data.get('notes'),
                recorded_by=request.user
            )
            messages.success(request, 'Data gizi berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': nutrition.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'locations': locations,
        'page_title': 'Tambah Data Gizi',
        'page_subtitle': 'Tambah data gizi baru'
    }
    return render(request, 'admin_panel/posyandu/nutrition_data.html', context)


@login_required
def admin_panel_nutrition_update(request, nutrition_id):
    """Update data gizi"""
    nutrition = get_object_or_404(NutritionData, id=nutrition_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nutrition.patient_id = data.get('patient_id', nutrition.patient_id)
            nutrition.posyandu_id = data.get('posyandu_id', nutrition.posyandu_id)
            nutrition.measurement_date = data.get('measurement_date', nutrition.measurement_date)
            nutrition.age_months = data.get('age_months', nutrition.age_months)
            nutrition.weight = data.get('weight', nutrition.weight)
            nutrition.height = data.get('height', nutrition.height)
            nutrition.head_circumference = data.get('head_circumference', nutrition.head_circumference)
            nutrition.arm_circumference = data.get('arm_circumference', nutrition.arm_circumference)
            nutrition.nutrition_status = data.get('nutrition_status', nutrition.nutrition_status)
            nutrition.vitamin_a_given = data.get('vitamin_a_given', nutrition.vitamin_a_given)
            nutrition.iron_supplement_given = data.get('iron_supplement_given', nutrition.iron_supplement_given)
            nutrition.notes = data.get('notes', nutrition.notes)
            nutrition.save()
            
            messages.success(request, 'Data gizi berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'nutrition': nutrition,
        'locations': locations,
        'page_title': f'Edit Data Gizi - {nutrition.patient.nama}',
        'page_subtitle': 'Edit data gizi'
    }
    return render(request, 'admin_panel/posyandu/nutrition_data.html', context)


@login_required
def admin_panel_kader_create(request):
    """Create kader posyandu baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kader = PosyanduKader.objects.create(
                penduduk_id=data.get('penduduk_id'),
                posyandu_id=data.get('posyandu_id'),
                jabatan=data.get('jabatan'),
                nomor_hp=data.get('nomor_hp'),
                tanggal_mulai=data.get('tanggal_mulai'),
                tanggal_selesai=data.get('tanggal_selesai'),
                status=data.get('status', 'aktif'),
                keterangan=data.get('keterangan')
            )
            messages.success(request, 'Kader posyandu berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': kader.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True).order_by('name')
    context = {
        'posyandu_locations': posyandu_locations,
        'page_title': 'Tambah Kader Posyandu',
        'page_subtitle': 'Tambah kader posyandu baru'
    }
    return render(request, 'admin_panel/posyandu/kader_form.html', context)


@login_required
def admin_panel_kader_update(request, kader_id):
    """Update kader posyandu"""
    kader = get_object_or_404(PosyanduKader, id=kader_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kader.penduduk_id = data.get('penduduk_id', kader.penduduk_id)
            kader.posyandu_id = data.get('posyandu_id', kader.posyandu_id)
            kader.jabatan = data.get('jabatan', kader.jabatan)
            kader.nomor_hp = data.get('nomor_hp', kader.nomor_hp)
            kader.tanggal_mulai = data.get('tanggal_mulai', kader.tanggal_mulai)
            kader.tanggal_selesai = data.get('tanggal_selesai', kader.tanggal_selesai)
            kader.status = data.get('status', kader.status)
            kader.keterangan = data.get('keterangan', kader.keterangan)
            kader.save()
            
            messages.success(request, 'Kader posyandu berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True).order_by('name')
    context = {
        'kader': kader,
        'posyandu_locations': posyandu_locations,
        'page_title': f'Edit Kader Posyandu - {kader.penduduk.nama}',
        'page_subtitle': 'Edit kader posyandu'
    }
    return render(request, 'admin_panel/posyandu/kader_form.html', context)


@login_required
def admin_panel_ibu_hamil_create(request):
    """Create data ibu hamil baru"""
    context = {
        'page_title': 'Tambah Data Ibu Hamil',
        'page_subtitle': 'Form tambah data ibu hamil baru'
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil_form.html', context)


@login_required
def admin_panel_ibu_hamil_update(request, ibu_hamil_id):
    """Update data ibu hamil"""
    ibu_hamil = get_object_or_404(IbuHamil, id=ibu_hamil_id)
    
    context = {
        'ibu_hamil': ibu_hamil,
        'page_title': f'Edit Data Ibu Hamil - {ibu_hamil.penduduk.nama if ibu_hamil.penduduk else "Unknown"}',
        'page_subtitle': 'Form edit data ibu hamil'
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil_form.html', context)


@login_required
def admin_panel_stunting_create(request):
    """Create data stunting baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stunting = StuntingData.objects.create(
                balita_id=data.get('balita_id'),
                posyandu_id=data.get('posyandu_id'),
                tanggal_ukur=data.get('tanggal_ukur'),
                usia_bulan=data.get('usia_bulan'),
                tinggi_badan=data.get('tinggi_badan'),
                berat_badan=data.get('berat_badan'),
                z_score_tb_u=data.get('z_score_tb_u'),
                z_score_bb_u=data.get('z_score_bb_u'),
                z_score_bb_tb=data.get('z_score_bb_tb'),
                status_stunting=data.get('status_stunting'),
                asi_eksklusif=data.get('asi_eksklusif', False),
                riwayat_bblr=data.get('riwayat_bblr', False),
                riwayat_penyakit=data.get('riwayat_penyakit'),
                intervensi_diberikan=data.get('intervensi_diberikan'),
                hasil_intervensi=data.get('hasil_intervensi'),
                follow_up_date=data.get('follow_up_date'),
                keterangan=data.get('keterangan'),
                recorded_by=request.user
            )
            messages.success(request, 'Data stunting berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': stunting.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'locations': locations,
        'page_title': 'Tambah Data Stunting',
        'page_subtitle': 'Tambah data stunting baru'
    }
    return render(request, 'admin_panel/posyandu/stunting_data.html', context)


@login_required
def admin_panel_stunting_update(request, stunting_id):
    """Update data stunting"""
    stunting = get_object_or_404(StuntingData, id=stunting_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stunting.balita_id = data.get('balita_id', stunting.balita_id)
            stunting.posyandu_id = data.get('posyandu_id', stunting.posyandu_id)
            stunting.tanggal_ukur = data.get('tanggal_ukur', stunting.tanggal_ukur)
            stunting.usia_bulan = data.get('usia_bulan', stunting.usia_bulan)
            stunting.tinggi_badan = data.get('tinggi_badan', stunting.tinggi_badan)
            stunting.berat_badan = data.get('berat_badan', stunting.berat_badan)
            stunting.z_score_tb_u = data.get('z_score_tb_u', stunting.z_score_tb_u)
            stunting.z_score_bb_u = data.get('z_score_bb_u', stunting.z_score_bb_u)
            stunting.z_score_bb_tb = data.get('z_score_bb_tb', stunting.z_score_bb_tb)
            stunting.status_stunting = data.get('status_stunting', stunting.status_stunting)
            stunting.asi_eksklusif = data.get('asi_eksklusif', stunting.asi_eksklusif)
            stunting.riwayat_bblr = data.get('riwayat_bblr', stunting.riwayat_bblr)
            stunting.riwayat_penyakit = data.get('riwayat_penyakit', stunting.riwayat_penyakit)
            stunting.intervensi_diberikan = data.get('intervensi_diberikan', stunting.intervensi_diberikan)
            stunting.hasil_intervensi = data.get('hasil_intervensi', stunting.hasil_intervensi)
            stunting.follow_up_date = data.get('follow_up_date', stunting.follow_up_date)
            stunting.keterangan = data.get('keterangan', stunting.keterangan)
            stunting.save()
            
            messages.success(request, 'Data stunting berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'stunting': stunting,
        'locations': locations,
        'page_title': f'Edit Data Stunting - {stunting.balita.nama}',
        'page_subtitle': 'Edit data stunting'
    }
    return render(request, 'admin_panel/posyandu/stunting_data.html', context)


@login_required
def admin_panel_reports(request):
    """Laporan dan analisis data posyandu"""
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Default to current month if no dates provided
    if not start_date:
        start_date = timezone.now().replace(day=1).date()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get statistics
    total_locations = PosyanduLocation.objects.filter(is_active=True).count()
    total_schedules = PosyanduSchedule.objects.filter(
        schedule_date__range=[start_date, end_date]
    ).count()
    total_health_records = HealthRecord.objects.filter(
        visit_date__range=[start_date, end_date]
    ).count()
    total_immunizations = Immunization.objects.filter(
        immunization_date__range=[start_date, end_date]
    ).count()
    total_nutrition = NutritionData.objects.filter(
        measurement_date__range=[start_date, end_date]
    ).count()
    total_kaders = PosyanduKader.objects.filter(status='aktif').count()
    total_ibu_hamil = IbuHamil.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).count()
    total_stunting = StuntingData.objects.filter(
        tanggal_ukur__range=[start_date, end_date]
    ).count()
    
    # Get location-wise statistics
    location_stats = PosyanduLocation.objects.annotate(
        health_record_count=Count('healthrecord', filter=Q(healthrecord__visit_date__range=[start_date, end_date])),
        immunization_count=Count('immunization', filter=Q(immunization__immunization_date__range=[start_date, end_date])),
        nutrition_count=Count('nutritiondata', filter=Q(nutritiondata__measurement_date__range=[start_date, end_date])),
        stunting_count=Count('stuntingdata', filter=Q(stuntingdata__tanggal_ukur__range=[start_date, end_date]))
    ).filter(is_active=True)
    
    # Get monthly trends
    monthly_stats = []
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        month_end = (current_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        if month_end > end_date:
            month_end = end_date
            
        monthly_data = {
            'month': current_date.strftime('%Y-%m'),
            'month_name': current_date.strftime('%B %Y'),
            'health_records': HealthRecord.objects.filter(
                visit_date__range=[current_date, month_end]
            ).count(),
            'immunizations': Immunization.objects.filter(
                immunization_date__range=[current_date, month_end]
            ).count(),
            'nutrition': NutritionData.objects.filter(
                measurement_date__range=[current_date, month_end]
            ).count(),
            'stunting': StuntingData.objects.filter(
                tanggal_ukur__range=[current_date, month_end]
            ).count()
        }
        monthly_stats.append(monthly_data)
        current_date = (current_date + timedelta(days=32)).replace(day=1)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_locations': total_locations,
        'total_schedules': total_schedules,
        'total_health_records': total_health_records,
        'total_immunizations': total_immunizations,
        'total_nutrition': total_nutrition,
        'total_kaders': total_kaders,
        'total_ibu_hamil': total_ibu_hamil,
        'total_stunting': total_stunting,
        'location_stats': location_stats,
        'monthly_stats': monthly_stats,
        'page_title': 'Laporan Posyandu',
        'page_subtitle': 'Laporan dan analisis data posyandu'
    }
    return render(request, 'admin_panel/posyandu/reports.html', context)


@login_required
def admin_panel_export_health_records(request):
    """Export data rekam kesehatan ke CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="health_records.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nama Balita', 'Posyandu', 'Tanggal Kunjungan', 'Berat Badan', 
        'Tinggi Badan', 'Lingkar Kepala', 'Status Gizi', 'Keterangan'
    ])
    
    health_records = HealthRecord.objects.select_related('patient', 'posyandu').all()
    for record in health_records:
        writer.writerow([
            record.id,
            record.patient.nama,
            record.posyandu.name,
            record.visit_date.strftime('%Y-%m-%d'),
            record.weight,
            record.height,
            record.blood_pressure,
            record.diagnosis,
            record.notes
        ])
    
    return response


@login_required
def admin_panel_export_immunizations(request):
    """Export data imunisasi ke CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="immunizations.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nama Balita', 'Posyandu', 'Tanggal Imunisasi', 'Jenis Imunisasi', 
        'Usia (Bulan)', 'Berat Badan', 'Tinggi Badan', 'Keterangan'
    ])
    
    immunizations = Immunization.objects.select_related('patient', 'posyandu').all()
    for immunization in immunizations:
        writer.writerow([
            immunization.id,
            immunization.patient.nama,
            immunization.posyandu.name,
            immunization.immunization_date.strftime('%Y-%m-%d'),
            immunization.vaccine_type,
            immunization.batch_number,
            immunization.health_worker,
            immunization.status,
            immunization.notes
        ])
    
    return response


@login_required
def admin_panel_api_statistics(request):
    """API endpoint untuk mendapatkan statistik posyandu"""
    stats = {
        'total_locations': PosyanduLocation.objects.filter(is_active=True).count(),
        'total_schedules': PosyanduSchedule.objects.count(),
        'total_health_records': HealthRecord.objects.count(),
        'total_immunizations': Immunization.objects.count(),
        'total_nutrition': NutritionData.objects.count(),
        'total_kaders': PosyanduKader.objects.filter(status='aktif').count(),
        'total_ibu_hamil': IbuHamil.objects.count(),
        'total_stunting': StuntingData.objects.count()
    }
    return JsonResponse(stats)


@login_required
def admin_panel_api_search_residents(request):
    """API endpoint untuk mencari penduduk"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    residents = Penduduk.objects.filter(
        Q(name__icontains=query) | Q(nik__icontains=query)
    ).values('id', 'name', 'nik', 'tanggal_lahir')[:10]
    
    return JsonResponse(list(residents), safe=False)


@login_required
def admin_panel_api_monthly_stats(request):
    """API endpoint untuk mendapatkan statistik bulanan"""
    year = request.GET.get('year', timezone.now().year)
    
    monthly_stats = []
    for month in range(1, 13):
        month_start = datetime(int(year), month, 1).date()
        if month == 12:
            month_end = datetime(int(year) + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(int(year), month + 1, 1).date() - timedelta(days=1)
        
        stats = {
            'month': month,
            'month_name': month_start.strftime('%B'),
            'health_records': HealthRecord.objects.filter(
                visit_date__range=[month_start, month_end]
            ).count(),
            'immunizations': Immunization.objects.filter(
                immunization_date__range=[month_start, month_end]
            ).count(),
            'nutrition': NutritionData.objects.filter(
                measurement_date__range=[month_start, month_end]
            ).count(),
            'stunting': StuntingData.objects.filter(
                tanggal_ukur__range=[month_start, month_end]
            ).count()
        }
        monthly_stats.append(stats)
    
    return JsonResponse(monthly_stats, safe=False)

# Detail Views

@login_required
def admin_panel_health_record_detail(request, record_id):
    """Detail rekam kesehatan"""
    record = get_object_or_404(HealthRecord, id=record_id)
    context = {
        'record': record,
        'page_title': f'Detail Rekam Kesehatan - {record.patient.nama}',
        'page_subtitle': 'Detail rekam kesehatan'
    }
    return render(request, 'admin_panel/posyandu/health_records_detail.html', context)


@login_required
def admin_panel_immunization_detail(request, immunization_id):
    """Detail imunisasi"""
    immunization = get_object_or_404(Immunization, id=immunization_id)
    context = {
        'immunization': immunization,
        'page_title': f'Detail Imunisasi - {immunization.patient.nama}',
        'page_subtitle': 'Detail imunisasi'
    }
    return render(request, 'admin_panel/posyandu/immunization_detail.html', context)


@login_required
def admin_panel_nutrition_detail(request, nutrition_id):
    """Detail data gizi"""
    nutrition = get_object_or_404(NutritionData, id=nutrition_id)
    context = {
        'nutrition': nutrition,
        'page_title': f'Detail Data Gizi - {nutrition.patient.nama}',
        'page_subtitle': 'Detail data gizi'
    }
    return render(request, 'admin_panel/posyandu/nutrition_detail.html', context)


@login_required
def admin_panel_kader_detail(request, kader_id):
    """Detail kader posyandu"""
    kader = get_object_or_404(PosyanduKader, id=kader_id)
    context = {
        'kader': kader,
        'page_title': f'Detail Kader - {kader.penduduk.nama}',
        'page_subtitle': 'Detail kader posyandu'
    }
    return render(request, 'admin_panel/posyandu/kader_detail.html', context)


@login_required
def admin_panel_ibu_hamil_detail(request, ibu_hamil_id):
    """Detail data ibu hamil"""
    ibu_hamil = get_object_or_404(IbuHamil, id=ibu_hamil_id)
    context = {
        'ibu_hamil': ibu_hamil,
        'page_title': f'Detail Ibu Hamil - {ibu_hamil.penduduk.nama}',
        'page_subtitle': 'Detail data ibu hamil'
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil_detail.html', context)




@login_required
def admin_panel_schedule_detail(request, schedule_id):
    """Detail jadwal posyandu"""
    schedule = get_object_or_404(PosyanduSchedule, id=schedule_id)
    context = {
        'schedule': schedule,
        'page_title': f'Detail Jadwal - {schedule.location.name}',
        'page_subtitle': 'Detail jadwal posyandu'
    }
    return render(request, 'admin_panel/posyandu/schedules_detail.html', context)

# Health Record Management Views

@login_required
def admin_panel_health_record_list(request):
    """List semua rekam kesehatan"""
    search_query = request.GET.get('search', '')
    location_filter = request.GET.get('location', '')
    date_filter = request.GET.get('date', '')
    
    records = HealthRecord.objects.select_related('patient', 'posyandu')
    
    if search_query:
        records = records.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__nik__icontains=search_query) |
            Q(diagnosis__icontains=search_query)
        )
    
    if location_filter:
        records = records.filter(posyandu_id=location_filter)
    
    if date_filter:
        records = records.filter(visit_date=date_filter)
    
    records = records.order_by('-visit_date')
    
    # Pagination
    paginator = Paginator(records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    locations = PosyanduLocation.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'locations': locations,
        'search_query': search_query,
        'location_filter': location_filter,
        'date_filter': date_filter,
    }
    return render(request, 'admin_panel/posyandu/health_records.html', context)


@login_required
def admin_panel_health_record_create(request):
    """Create rekam kesehatan baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record = HealthRecord.objects.create(
                patient_id=data.get('patient_id'),
                posyandu_id=data.get('posyandu_id'),
                patient_type=data.get('patient_type'),
                visit_date=data.get('visit_date'),
                weight=data.get('weight'),
                height=data.get('height'),
                blood_pressure=data.get('blood_pressure', ''),
                temperature=data.get('temperature'),
                complaints=data.get('complaints', ''),
                diagnosis=data.get('diagnosis', ''),
                treatment=data.get('treatment', ''),
                next_visit=data.get('next_visit'),
                recorded_by=request.user
            )
            messages.success(request, 'Rekam kesehatan berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': record.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - render form
    locations = PosyanduLocation.objects.filter(is_active=True)
    context = {
        'locations': locations,
        'page_title': 'Tambah Rekam Kesehatan',
        'page_subtitle': 'Form tambah rekam kesehatan baru'
    }
    return render(request, 'admin_panel/posyandu/health_records_form.html', context)


@login_required
def admin_panel_health_record_detail(request, record_id):
    """Detail rekam kesehatan"""
    record = get_object_or_404(HealthRecord, id=record_id)
    
    context = {
        'record': record,
        'page_title': f'Detail Rekam Kesehatan - {record.patient.nama}',
        'page_subtitle': 'Detail rekam kesehatan pasien'
    }
    return render(request, 'admin_panel/posyandu/health_records_detail.html', context)


@login_required
def admin_panel_health_record_update(request, record_id):
    """Update rekam kesehatan"""
    record = get_object_or_404(HealthRecord, id=record_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record.patient_id = data.get('patient_id', record.patient_id)
            record.posyandu_id = data.get('posyandu_id', record.posyandu_id)
            record.patient_type = data.get('patient_type', record.patient_type)
            record.visit_date = data.get('visit_date', record.visit_date)
            record.weight = data.get('weight', record.weight)
            record.height = data.get('height', record.height)
            record.blood_pressure = data.get('blood_pressure', record.blood_pressure)
            record.temperature = data.get('temperature', record.temperature)
            record.complaints = data.get('complaints', record.complaints)
            record.diagnosis = data.get('diagnosis', record.diagnosis)
            record.treatment = data.get('treatment', record.treatment)
            record.next_visit = data.get('next_visit', record.next_visit)
            record.save()
            
            messages.success(request, 'Rekam kesehatan berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - render form
    locations = PosyanduLocation.objects.filter(is_active=True)
    
    context = {
        'record': record,
        'locations': locations,
        'page_title': f'Edit Rekam Kesehatan - {record.patient.nama}',
        'page_subtitle': 'Form edit rekam kesehatan'
    }
    return render(request, 'admin_panel/posyandu/health_records_form.html', context)


@login_required
def admin_panel_immunization_list(request):
    """List semua data imunisasi"""
    search_query = request.GET.get('search', '')
    vaccine_filter = request.GET.get('vaccine', '')
    date_filter = request.GET.get('date', '')
    
    immunizations = Immunization.objects.select_related('patient')
    
    if search_query:
        immunizations = immunizations.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__nik__icontains=search_query) |
            Q(vaccine_type__icontains=search_query)
        )
    
    if vaccine_filter:
        immunizations = immunizations.filter(vaccine_type__icontains=vaccine_filter)
    
    if date_filter:
        immunizations = immunizations.filter(immunization_date=date_filter)
    
    immunizations = immunizations.order_by('-immunization_date')
    
    # Pagination
    paginator = Paginator(immunizations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique vaccine names for filter
    vaccine_types = Immunization.objects.values_list('vaccine_type', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'vaccine_types': vaccine_types,
        'search_query': search_query,
        'vaccine_filter': vaccine_filter,
        'date_filter': date_filter,
    }
    return render(request, 'admin_panel/posyandu/immunizations.html', context)


@login_required
def admin_panel_immunization_create(request):
    """Create data imunisasi baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            immunization = Immunization.objects.create(
                patient_id=data.get('patient_id'),
                vaccine_type=data.get('vaccine_type'),
                immunization_date=data.get('immunization_date'),
                batch_number=data.get('batch_number', ''),
                vaccinator=data.get('vaccinator', ''),
                notes=data.get('notes', '')
            )
            messages.success(request, 'Data imunisasi berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': immunization.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    context = {}
    return render(request, 'admin_panel/posyandu/immunizations.html', context)


@login_required
def admin_panel_immunization_detail(request, immunization_id):
    """Detail data imunisasi"""
    immunization = get_object_or_404(Immunization, id=immunization_id)
    
    context = {
        'immunization': immunization,
    }
    return render(request, 'admin_panel/posyandu/immunization_detail.html', context)


@login_required
def admin_panel_immunization_update(request, immunization_id):
    """Update data imunisasi"""
    immunization = get_object_or_404(Immunization, id=immunization_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            immunization.patient_id = data.get('patient_id', immunization.patient_id)
            immunization.vaccine_type = data.get('vaccine_type', immunization.vaccine_type)
            immunization.immunization_date = data.get('immunization_date', immunization.immunization_date)
            immunization.batch_number = data.get('batch_number', immunization.batch_number)
            immunization.vaccinator = data.get('vaccinator', immunization.vaccinator)
            immunization.notes = data.get('notes', immunization.notes)
            immunization.save()
            
            messages.success(request, 'Data imunisasi berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    context = {
        'immunization': immunization,
    }
    return render(request, 'admin_panel/posyandu/immunizations.html', context)


@login_required
def admin_panel_nutrition_list(request):
    """List semua data gizi"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    nutrition_data = NutritionData.objects.select_related('patient')
    
    if search_query:
        nutrition_data = nutrition_data.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__nik__icontains=search_query)
        )
    
    if status_filter:
        nutrition_data = nutrition_data.filter(status_stunting=status_filter)
    
    if date_filter:
        nutrition_data = nutrition_data.filter(measurement_date=date_filter)
    
    nutrition_data = nutrition_data.order_by('-measurement_date')
    
    # Pagination
    paginator = Paginator(nutrition_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    return render(request, 'admin_panel/posyandu/nutrition_data.html', context)


@login_required
def admin_panel_nutrition_create(request):
    """Create data gizi baru"""
    context = {
        'page_title': 'Tambah Data Gizi',
        'page_subtitle': 'Form tambah data gizi baru'
    }
    return render(request, 'admin_panel/posyandu/nutrition_data_form.html', context)


@login_required
def admin_panel_nutrition_detail(request, nutrition_id):
    """Detail data gizi"""
    nutrition = get_object_or_404(NutritionData, id=nutrition_id)
    
    context = {
        'nutrition': nutrition,
    }
    return render(request, 'admin_panel/posyandu/nutrition_detail.html', context)


@login_required
def admin_panel_nutrition_update(request, nutrition_id):
    """Update data gizi"""
    nutrition = get_object_or_404(NutritionData, id=nutrition_id)
    
    context = {
        'nutrition': nutrition,
        'page_title': f'Edit Data Gizi - {nutrition.patient.nama if nutrition.patient else "Unknown"}',
        'page_subtitle': 'Form edit data gizi'
    }
    return render(request, 'admin_panel/posyandu/nutrition_data_form.html', context)

@login_required
def admin_panel_immunization_create(request):
    """Create imunisasi baru"""
    context = {
        'page_title': 'Tambah Data Imunisasi',
        'page_subtitle': 'Form tambah data imunisasi baru'
    }
    return render(request, 'admin_panel/posyandu/immunization_form.html', context)

@login_required
def admin_panel_immunization_update(request, immunization_id):
    """Update data imunisasi"""
    immunization = get_object_or_404(Immunization, id=immunization_id)
    
    context = {
        'immunization': immunization,
        'page_title': f'Edit Data Imunisasi - {immunization.patient.name if immunization.patient else "Unknown"}',
        'page_subtitle': 'Form edit data imunisasi'
    }
    return render(request, 'admin_panel/posyandu/immunization_form.html', context)

@login_required
def admin_panel_immunization_detail(request, immunization_id):
    """Detail data imunisasi"""
    immunization = get_object_or_404(Immunization, id=immunization_id)
    
    context = {
        'immunization': immunization,
        'page_title': f'Detail Imunisasi - {immunization.patient.name if immunization.patient else "Unknown"}',
        'page_subtitle': 'Informasi lengkap data imunisasi'
    }
    return render(request, 'admin_panel/posyandu/immunization_detail.html', context)


@login_required
def admin_panel_kader_list(request):
    """List semua kader posyandu"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    kaders = PosyanduKader.objects.select_related('penduduk')
    
    if search_query:
        kaders = kaders.filter(
            Q(penduduk__name__icontains=search_query) |
            Q(nomor_hp__icontains=search_query) |
            Q(penduduk__address__icontains=search_query)
        )
    
    if status_filter:
        kaders = kaders.filter(status=status_filter)
    
    kaders = kaders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(kaders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_panel/posyandu/kaders.html', context)


@login_required
def admin_panel_kader_create(request):
    """Create kader posyandu baru"""
    if request.method == 'POST':
        try:
            # Handle form data instead of JSON
            penduduk_id = request.POST.get('penduduk_id')
            posyandu_id = request.POST.get('posyandu_id')
            jabatan = request.POST.get('jabatan')
            nomor_hp = request.POST.get('nomor_hp', '')
            tanggal_mulai = request.POST.get('tanggal_mulai')
            tanggal_selesai = request.POST.get('tanggal_selesai')
            status = request.POST.get('status', 'aktif')
            keterangan = request.POST.get('keterangan', '')
            
            # Validate required fields
            if not penduduk_id:
                messages.error(request, 'Pilih penduduk terlebih dahulu!')
                return redirect('posyandu:kader_create')
            
            if not posyandu_id:
                messages.error(request, 'Pilih lokasi posyandu terlebih dahulu!')
                return redirect('posyandu:kader_create')
            
            if not jabatan:
                messages.error(request, 'Pilih jabatan terlebih dahulu!')
                return redirect('posyandu:kader_create')
            
            if not tanggal_mulai:
                messages.error(request, 'Isi tanggal mulai tugas!')
                return redirect('posyandu:kader_create')
            
            kader = PosyanduKader.objects.create(
                penduduk_id=penduduk_id,
                posyandu_id=posyandu_id,
                jabatan=jabatan,
                nomor_hp=nomor_hp,
                tanggal_mulai=tanggal_mulai,
                tanggal_selesai=tanggal_selesai if tanggal_selesai else None,
                status=status,
                keterangan=keterangan
            )
            messages.success(request, 'Kader posyandu berhasil ditambahkan!')
            return redirect('posyandu:kaders')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('posyandu:kader_create')
    
    # Get active posyandu locations for dropdown
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True).order_by('name')
    
    context = {
        'posyandu_locations': posyandu_locations,
        'page_title': 'Tambah Kader Posyandu',
        'page_subtitle': 'Tambah kader posyandu baru'
    }
    return render(request, 'admin_panel/posyandu/kader_form.html', context)


@login_required
def admin_panel_kader_detail(request, kader_id):
    """Detail kader posyandu"""
    kader = get_object_or_404(PosyanduKader, id=kader_id)
    schedules = PosyanduSchedule.objects.filter(location=kader.posyandu).order_by('-schedule_date')[:10]
    
    context = {
        'kader': kader,
        'schedules': schedules,
    }
    return render(request, 'admin_panel/posyandu/kader_detail.html', context)


@login_required
def admin_panel_kader_update(request, kader_id):
    """Update kader posyandu"""
    kader = get_object_or_404(PosyanduKader, id=kader_id)
    
    if request.method == 'POST':
        try:
            # Handle form data instead of JSON
            penduduk_id = request.POST.get('penduduk_id')
            posyandu_id = request.POST.get('posyandu_id')
            jabatan = request.POST.get('jabatan')
            nomor_hp = request.POST.get('nomor_hp', '')
            tanggal_mulai = request.POST.get('tanggal_mulai')
            tanggal_selesai = request.POST.get('tanggal_selesai')
            status = request.POST.get('status', 'aktif')
            keterangan = request.POST.get('keterangan', '')
            
            # Validate required fields
            if not penduduk_id:
                messages.error(request, 'Pilih penduduk terlebih dahulu!')
                return redirect('posyandu:kader_update', kader_id=kader_id)
            
            if not posyandu_id:
                messages.error(request, 'Pilih lokasi posyandu terlebih dahulu!')
                return redirect('posyandu:kader_update', kader_id=kader_id)
            
            if not jabatan:
                messages.error(request, 'Pilih jabatan terlebih dahulu!')
                return redirect('posyandu:kader_update', kader_id=kader_id)
            
            if not tanggal_mulai:
                messages.error(request, 'Isi tanggal mulai tugas!')
                return redirect('posyandu:kader_update', kader_id=kader_id)
            
            kader.penduduk_id = penduduk_id
            kader.posyandu_id = posyandu_id
            kader.jabatan = jabatan
            kader.nomor_hp = nomor_hp
            kader.tanggal_mulai = tanggal_mulai
            kader.tanggal_selesai = tanggal_selesai if tanggal_selesai else None
            kader.status = status
            kader.keterangan = keterangan
            kader.save()
            
            messages.success(request, 'Kader posyandu berhasil diperbarui!')
            return redirect('posyandu:kaders')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('posyandu:kader_update', kader_id=kader_id)
    
    # Get active posyandu locations for dropdown
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True).order_by('name')
    
    context = {
        'kader': kader,
        'posyandu_locations': posyandu_locations,
        'page_title': f'Edit Kader Posyandu - {kader.penduduk.nama}',
        'page_subtitle': 'Edit informasi kader posyandu'
    }
    return render(request, 'admin_panel/posyandu/kader_form.html', context)


@login_required
def admin_panel_ibu_hamil_list(request):
    """List semua data ibu hamil"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    ibu_hamil = IbuHamil.objects.select_related('penduduk')
    
    if search_query:
        ibu_hamil = ibu_hamil.filter(
            Q(penduduk__name__icontains=search_query) |
            Q(penduduk__nik__icontains=search_query) |
            Q(husband_name__icontains=search_query)
        )
    
    if status_filter:
        ibu_hamil = ibu_hamil.filter(pregnancy_status=status_filter)
    
    ibu_hamil = ibu_hamil.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(ibu_hamil, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil.html', context)


@login_required
def admin_panel_ibu_hamil_create(request):
    """Create data ibu hamil baru"""
    context = {
        'page_title': 'Tambah Data Ibu Hamil',
        'page_subtitle': 'Form tambah data ibu hamil baru'
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil_form.html', context)


@login_required
def admin_panel_ibu_hamil_detail(request, ibu_hamil_id):
    """Detail data ibu hamil"""
    ibu_hamil = get_object_or_404(IbuHamil, id=ibu_hamil_id)
    
    context = {
        'ibu_hamil': ibu_hamil,
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil_detail.html', context)


@login_required
def admin_panel_ibu_hamil_update(request, ibu_hamil_id):
    """Update data ibu hamil"""
    ibu_hamil = get_object_or_404(IbuHamil, id=ibu_hamil_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ibu_hamil.penduduk_id = data.get('penduduk_id', ibu_hamil.penduduk_id)
            ibu_hamil.tanggal_hpht = data.get('tanggal_hpht', ibu_hamil.tanggal_hpht)
            ibu_hamil.usia_kehamilan = data.get('usia_kehamilan', ibu_hamil.usia_kehamilan)
            ibu_hamil.tanggal_perkiraan_lahir = data.get('tanggal_perkiraan_lahir', ibu_hamil.tanggal_perkiraan_lahir)
            ibu_hamil.riwayat_kehamilan = data.get('riwayat_kehamilan', ibu_hamil.riwayat_kehamilan)
            ibu_hamil.berat_badan_sebelum_hamil = data.get('berat_badan_sebelum_hamil', ibu_hamil.berat_badan_sebelum_hamil)
            ibu_hamil.tinggi_badan = data.get('tinggi_badan', ibu_hamil.tinggi_badan)
            ibu_hamil.golongan_darah = data.get('golongan_darah', ibu_hamil.golongan_darah)
            ibu_hamil.riwayat_penyakit = data.get('riwayat_penyakit', ibu_hamil.riwayat_penyakit)
            ibu_hamil.risiko_kehamilan = data.get('risiko_kehamilan', ibu_hamil.risiko_kehamilan)
            ibu_hamil.nomor_buku_kia = data.get('nomor_buku_kia', ibu_hamil.nomor_buku_kia)
            ibu_hamil.status_aktif = data.get('status_aktif', ibu_hamil.status_aktif)
            ibu_hamil.keterangan = data.get('keterangan', ibu_hamil.keterangan)
            ibu_hamil.save()
            
            messages.success(request, 'Data ibu hamil berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    context = {
        'ibu_hamil': ibu_hamil,
        'page_title': f'Edit Data Ibu Hamil - {ibu_hamil.penduduk.nama if ibu_hamil.penduduk else "Unknown"}',
        'page_subtitle': 'Form edit data ibu hamil'
    }
    return render(request, 'admin_panel/posyandu/ibu_hamil_form.html', context)


@login_required
def admin_panel_stunting_list(request):
    """List semua data stunting"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    stunting_data = StuntingData.objects.select_related('balita')
    
    if search_query:
        stunting_data = stunting_data.filter(
            Q(balita__nama__icontains=search_query) |
            Q(balita__nik__icontains=search_query)
        )
    
    if status_filter:
        stunting_data = stunting_data.filter(status_stunting=status_filter)
    
    stunting_data = stunting_data.order_by('-tanggal_ukur')
    
    # Pagination
    paginator = Paginator(stunting_data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_panel/posyandu/stunting_data.html', context)


@login_required
def admin_panel_stunting_create(request):
    """Create data stunting baru"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stunting = StuntingData.objects.create(
                balita_id=data.get('balita_id'),
                tanggal_ukur=data.get('tanggal_ukur'),
                tinggi_badan=data.get('tinggi_badan'),
                usia_bulan=data.get('usia_bulan'),
                z_score_tb_u=data.get('z_score_tb_u'),
                z_score_bb_u=data.get('z_score_bb_u'),
                z_score_bb_tb=data.get('z_score_bb_tb'),
                status_stunting=data.get('status_stunting'),
                asi_eksklusif=data.get('asi_eksklusif', False),
                riwayat_bblr=data.get('riwayat_bblr', False),
                riwayat_penyakit=data.get('riwayat_penyakit', ''),
                intervensi_diberikan=data.get('intervensi_diberikan', ''),
                hasil_intervensi=data.get('hasil_intervensi', ''),
                follow_up_date=data.get('follow_up_date'),
                keterangan=data.get('keterangan', '')
            )
            messages.success(request, 'Data stunting berhasil ditambahkan!')
            return JsonResponse({'success': True, 'id': stunting.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    context = {
        'page_title': 'Tambah Data Stunting',
        'page_subtitle': 'Form tambah data stunting baru'
    }
    return render(request, 'admin_panel/posyandu/stunting_data_form.html', context)


@login_required
def admin_panel_stunting_detail(request, stunting_id):
    """Detail data stunting"""
    stunting = get_object_or_404(StuntingData, id=stunting_id)
    
    context = {
        'stunting': stunting,
        'page_title': f'Detail Data Stunting - {stunting.balita.nama if stunting.balita else "Unknown"}',
        'page_subtitle': 'Detail data stunting'
    }
    return render(request, 'admin_panel/posyandu/stunting_detail.html', context)


@login_required
def admin_panel_stunting_update(request, stunting_id):
    """Update data stunting"""
    stunting = get_object_or_404(StuntingData, id=stunting_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stunting.balita_id = data.get('balita_id', stunting.balita_id)
            stunting.tanggal_ukur = data.get('tanggal_ukur', stunting.tanggal_ukur)
            stunting.tinggi_badan = data.get('tinggi_badan', stunting.tinggi_badan)
            stunting.usia_bulan = data.get('usia_bulan', stunting.usia_bulan)
            stunting.z_score_tb_u = data.get('z_score_tb_u', stunting.z_score_tb_u)
            stunting.z_score_bb_u = data.get('z_score_bb_u', stunting.z_score_bb_u)
            stunting.z_score_bb_tb = data.get('z_score_bb_tb', stunting.z_score_bb_tb)
            stunting.status_stunting = data.get('status_stunting', stunting.status_stunting)
            stunting.asi_eksklusif = data.get('asi_eksklusif', stunting.asi_eksklusif)
            stunting.riwayat_bblr = data.get('riwayat_bblr', stunting.riwayat_bblr)
            stunting.riwayat_penyakit = data.get('riwayat_penyakit', stunting.riwayat_penyakit)
            stunting.intervensi_diberikan = data.get('intervensi_diberikan', stunting.intervensi_diberikan)
            stunting.hasil_intervensi = data.get('hasil_intervensi', stunting.hasil_intervensi)
            stunting.follow_up_date = data.get('follow_up_date', stunting.follow_up_date)
            stunting.keterangan = data.get('keterangan', stunting.keterangan)
            stunting.save()
            
            messages.success(request, 'Data stunting berhasil diperbarui!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    context = {
        'stunting': stunting,
        'page_title': f'Edit Data Stunting - {stunting.balita.nama if stunting.balita else "Unknown"}',
        'page_subtitle': 'Form edit data stunting'
    }
    return render(request, 'admin_panel/posyandu/stunting_data_form.html', context)


@login_required
def admin_panel_reports(request):
    """Laporan dan analitik posyandu"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    # Date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Health records statistics
    health_records = HealthRecord.objects.filter(
        visit_date__range=[start_date, end_date]
    )
    
    # Immunization statistics
    immunizations = Immunization.objects.filter(
        immunization_date__range=[start_date, end_date]
    )
    
    # Nutrition statistics
    nutrition_data = NutritionData.objects.filter(
        measurement_date__range=[start_date, end_date]
    )
    
    # Stunting statistics
    stunting_data = StuntingData.objects.filter(
        tanggal_ukur__range=[start_date, end_date]
    )
    
    # Statistics by location
    location_stats = PosyanduLocation.objects.annotate(
        health_record_count=Count('healthrecord'),
        schedule_count=Count('schedules')
    )
    
    # Monthly trends
    monthly_health_records = []
    monthly_immunizations = []
    for i in range(12):
        month_start = datetime.now().replace(day=1, month=i+1 if i < 12 else 12)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        health_count = HealthRecord.objects.filter(
            visit_date__range=[month_start, month_end]
        ).count()
        
        immunization_count = Immunization.objects.filter(
            immunization_date__range=[month_start, month_end]
        ).count()
        
        monthly_health_records.append(health_count)
        monthly_immunizations.append(immunization_count)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'health_records_count': health_records.count(),
        'immunizations_count': immunizations.count(),
        'nutrition_data_count': nutrition_data.count(),
        'stunting_data_count': stunting_data.count(),
        'location_stats': location_stats,
        'monthly_health_records': monthly_health_records,
        'monthly_immunizations': monthly_immunizations,
        'avg_weight': nutrition_data.aggregate(Avg('weight'))['weight__avg'] or 0,
        'avg_height': nutrition_data.aggregate(Avg('height'))['height__avg'] or 0,
        'stunting_count': stunting_data.filter(status_stunting='stunting').count(),
    }
    return render(request, 'admin_panel/posyandu/reports.html', context)

# Export Data Views

@login_required
def admin_panel_export_health_records(request):
    """Export data rekam kesehatan ke CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="health_records.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nama Pasien', 'NIK', 'Lokasi', 'Tanggal Pemeriksaan',
        'Berat Badan', 'Tinggi Badan', 'Tekanan Darah', 'Suhu',
        'Diagnosis', 'Pengobatan', 'Catatan'
    ])
    
    records = HealthRecord.objects.select_related('patient', 'posyandu')
    for record in records:
        writer.writerow([
            record.id,
            record.patient.nama,
            record.patient.nik,
            record.posyandu.name,
            record.visit_date,
            record.weight,
            record.height,
            record.blood_pressure,
            record.temperature,
            record.diagnosis,
            record.treatment,
            record.notes
        ])
    
    return response


@login_required
def admin_panel_export_immunizations(request):
    """Export data imunisasi ke CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="immunizations.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nama Pasien', 'NIK', 'Nama Vaksin', 'Tanggal Vaksinasi',
        'Nomor Batch', 'Petugas Vaksin', 'Catatan'
    ])
    
    immunizations = Immunization.objects.select_related('patient')
    for immunization in immunizations:
        writer.writerow([
            immunization.id,
            immunization.patient.nama,
            immunization.patient.nik,
            immunization.vaccine_type,
            immunization.immunization_date,
            immunization.batch_number,
            immunization.vaccinator,
            immunization.notes
        ])
    
    return response


@login_required
def admin_panel_export_nutrition_data(request):
    """Export data gizi ke CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="nutrition_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nama Anak', 'NIK', 'Tanggal Pengukuran',
        'Berat Badan', 'Tinggi Badan', 'Lingkar Kepala', 'Lingkar Lengan',
        'Status Gizi', 'Catatan'
    ])
    
    nutrition_data = NutritionData.objects.select_related('patient')
    for nutrition in nutrition_data:
        writer.writerow([
            nutrition.id,
            nutrition.patient.nama,
            nutrition.patient.nik,
            nutrition.measurement_date,
            nutrition.weight,
            nutrition.height,
            nutrition.head_circumference,
            nutrition.arm_circumference,
            nutrition.status,
            nutrition.notes
        ])
    
    return response


def admin_panel_export_stunting_data(request):
    """Export data stunting ke CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stunting_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nama Anak', 'NIK', 'Tanggal Ukur', 'Usia (Bulan)',
        'Tinggi Badan', 'Berat Badan', 'Z-Score TB/U', 'Z-Score BB/U', 'Z-Score BB/TB',
        'Status Stunting', 'ASI Eksklusif', 'Riwayat BBLR', 'Riwayat Penyakit',
        'Intervensi', 'Hasil Intervensi', 'Follow Up', 'Keterangan'
    ])
    
    stunting_data = StuntingData.objects.select_related('balita')
    for stunting in stunting_data:
        writer.writerow([
            stunting.id,
            stunting.balita.nama if stunting.balita else '-',
            stunting.balita.nik if stunting.balita else '-',
            stunting.tanggal_ukur,
            stunting.usia_bulan,
            stunting.tinggi_badan,
            stunting.berat_badan,
            stunting.z_score_tb_u,
            stunting.z_score_bb_u,
            stunting.z_score_bb_tb,
            stunting.get_status_stunting_display(),
            'Ya' if stunting.asi_eksklusif else 'Tidak',
            'Ya' if stunting.riwayat_bblr else 'Tidak',
            stunting.riwayat_penyakit,
            stunting.get_intervensi_diberikan_display() if stunting.intervensi_diberikan else '-',
            stunting.hasil_intervensi,
            stunting.follow_up_date,
            stunting.keterangan
        ])
    
    return response

# Bulk Operations

@login_required
def admin_panel_api_statistics(request):
    """API endpoint untuk statistik posyandu"""
    from django.db.models import Count, Avg
    
    stats = {
        'total_locations': PosyanduLocation.objects.count(),
        'active_locations': PosyanduLocation.objects.filter(is_active=True).count(),
        'total_schedules': PosyanduSchedule.objects.count(),
        'total_health_records': HealthRecord.objects.count(),
        'total_immunizations': Immunization.objects.count(),
        'total_nutrition_data': NutritionData.objects.count(),
        'total_kaders': PosyanduKader.objects.count(),
        'total_ibu_hamil': IbuHamil.objects.count(),
        'total_stunting_data': StuntingData.objects.count(),
        'avg_weight': NutritionData.objects.aggregate(Avg('weight'))['weight__avg'] or 0,
        'avg_height': NutritionData.objects.aggregate(Avg('height'))['height__avg'] or 0,
        'stunting_count': StuntingData.objects.filter(status_stunting='stunting').count(),
    }
    
    return JsonResponse(stats)


@login_required
def admin_panel_api_search_residents(request):
    """API endpoint untuk pencarian penduduk"""
    # from references.models import Penduduk  # COMMENTED OUT - references app disabled
# Using letters app models instead
    try:
        from letters.models import Penduduk
    except ImportError:
        Penduduk = None
    
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'residents': []})
    
    residents = Penduduk.objects.filter(
        Q(name__icontains=query) |
        Q(nik__icontains=query)
    )[:10]
    
    data = [{
        'id': resident.id,
        'nama': resident.name,
        'nik': resident.nik,
        'tanggal_lahir': resident.birth_date.strftime('%Y-%m-%d') if resident.birth_date else None,
        'jenis_kelamin': resident.gender
    } for resident in residents]
    
    return JsonResponse({'residents': data})


@login_required
def admin_panel_api_monthly_stats(request):
    """API endpoint untuk statistik bulanan"""
    from datetime import datetime, timedelta
    
    year = int(request.GET.get('year', datetime.now().year))
    
    monthly_data = []
    for month in range(1, 13):
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        health_records = HealthRecord.objects.filter(
            visit_date__range=[month_start, month_end]
        ).count()
        
        immunizations = Immunization.objects.filter(
            immunization_date__range=[month_start, month_end]
        ).count()
        
        nutrition_data = NutritionData.objects.filter(
            measurement_date__range=[month_start, month_end]
        ).count()
        
        monthly_data.append({
            'month': month,
            'month_name': month_start.strftime('%B'),
            'health_records': health_records,
            'immunizations': immunizations,
            'nutrition_data': nutrition_data
        })
    
    return JsonResponse({'monthly_data': monthly_data})


@csrf_exempt
@require_http_methods(["GET"])
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
        five_years_ago = date.today() - timedelta(days=5*365)
        total_balita = Penduduk.objects.filter(
            birth_date__gte=five_years_ago,
            is_active=True
        ).count()
        
        # Nutrition statistics
        balita_sehat = NutritionData.objects.filter(
            nutrition_status='normal'
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
        
        if age_min:
            birth_date_max = timezone.now().date() - timedelta(days=int(age_min) * 365)
            residents = residents.filter(birth_date__lte=birth_date_max)
        
        if age_max:
            birth_date_min = timezone.now().date() - timedelta(days=int(age_max) * 365)
            residents = residents.filter(birth_date__gte=birth_date_min)
        
        if gender:
            residents = residents.filter(gender=gender)
        
        residents = residents.order_by('name')[:50]  # Limit to 50 results
        
        data = {
            'results': [
                {
                    'id': resident.id,
                    'nik': resident.nik,
                    'name': resident.name,
                    'birth_date': resident.birth_date.strftime('%Y-%m-%d') if resident.birth_date else None,
                    'gender': resident.get_gender_display(),
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

@login_required
def admin_panel_schedule_delete(request, schedule_id):
    """Hapus jadwal posyandu"""
    schedule = get_object_or_404(PosyanduSchedule, id=schedule_id)
    
    if request.method == 'POST':
        try:
            schedule.delete()
            messages.success(request, 'Jadwal posyandu berhasil dihapus!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def admin_panel_health_record_delete(request, record_id):
    """Hapus rekam kesehatan"""
    record = get_object_or_404(HealthRecord, id=record_id)
    
    if request.method == 'POST':
        try:
            record.delete()
            messages.success(request, 'Rekam kesehatan berhasil dihapus!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def admin_panel_immunization_delete(request, immunization_id):
    """Hapus data imunisasi"""
    immunization = get_object_or_404(Immunization, id=immunization_id)
    
    if request.method == 'POST':
        try:
            immunization.delete()
            messages.success(request, 'Data imunisasi berhasil dihapus!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def admin_panel_nutrition_delete(request, nutrition_id):
    """Hapus data gizi"""
    nutrition = get_object_or_404(NutritionData, id=nutrition_id)
    
    if request.method == 'POST':
        try:
            nutrition.delete()
            messages.success(request, 'Data gizi berhasil dihapus!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def admin_panel_kader_delete(request, kader_id):
    """Hapus data kader"""
    kader = get_object_or_404(PosyanduKader, id=kader_id)
    
    if request.method == 'POST':
        try:
            kader.delete()
            messages.success(request, 'Data kader berhasil dihapus!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def admin_panel_ibu_hamil_delete(request, ibu_hamil_id):
    """Hapus data ibu hamil"""
    ibu_hamil = get_object_or_404(IbuHamil, id=ibu_hamil_id)
    
    if request.method == 'POST':
        try:
            ibu_hamil.delete()
            messages.success(request, 'Data ibu hamil berhasil dihapus!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@login_required
def admin_panel_stunting_delete(request, stunting_id):
    """Hapus data stunting"""
    stunting = get_object_or_404(StuntingData, id=stunting_id)
    
    if request.method == 'POST':
        try:
            stunting.delete()
            messages.success(request, 'Data stunting berhasil dihapus!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

