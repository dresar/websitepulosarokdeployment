from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import PatientType


# Patient Type Management Views
@login_required
def admin_panel_patient_types(request):
    """List all patient types"""
    try:
        patient_types = PatientType.objects.all().order_by('name')
        
        # Pagination
        paginator = Paginator(patient_types, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_title': 'Jenis Pasien',
            'page_subtitle': 'Kelola jenis pasien posyandu',
            'patient_types': page_obj,
            'total_count': patient_types.count()
        }
        
        return render(request, 'admin_panel/posyandu/patient_types.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading patient types: {str(e)}')
        return render(request, 'admin_panel/posyandu/patient_types.html', {
            'page_title': 'Jenis Pasien',
            'page_subtitle': 'Kelola jenis pasien posyandu',
            'patient_types': [],
            'total_count': 0
        })


@login_required
def admin_panel_patient_type_create(request):
    """Create new patient type"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()
            description = request.POST.get('description', '').strip()
            age_min = request.POST.get('age_min')
            age_max = request.POST.get('age_max')
            is_active = request.POST.get('is_active') == 'on'
            
            # Validation
            if not name or not code:
                messages.error(request, 'Nama dan kode jenis pasien harus diisi!')
                return render(request, 'admin_panel/posyandu/patient_type_form.html', {
                    'page_title': 'Tambah Jenis Pasien',
                    'page_subtitle': 'Tambah jenis pasien baru',
                    'form_data': request.POST
                })
            
            # Check if code already exists
            if PatientType.objects.filter(code=code).exists():
                messages.error(request, 'Kode jenis pasien sudah digunakan!')
                return render(request, 'admin_panel/posyandu/patient_type_form.html', {
                    'page_title': 'Tambah Jenis Pasien',
                    'page_subtitle': 'Tambah jenis pasien baru',
                    'form_data': request.POST
                })
            
            # Validate age range
            if age_min and age_max and int(age_min) > int(age_max):
                messages.error(request, 'Usia minimum tidak boleh lebih besar dari usia maksimum!')
                return render(request, 'admin_panel/posyandu/patient_type_form.html', {
                    'page_title': 'Tambah Jenis Pasien',
                    'page_subtitle': 'Tambah jenis pasien baru',
                    'form_data': request.POST
                })
            
            # Create patient type
            patient_type = PatientType.objects.create(
                name=name,
                code=code,
                description=description,
                age_min=int(age_min) if age_min else None,
                age_max=int(age_max) if age_max else None,
                is_active=is_active
            )
            
            messages.success(request, f'Jenis pasien "{patient_type.name}" berhasil dibuat!')
            return redirect('posyandu:patient_types')
            
        except Exception as e:
            messages.error(request, f'Error creating patient type: {str(e)}')
            return render(request, 'admin_panel/posyandu/patient_type_form.html', {
                'page_title': 'Tambah Jenis Pasien',
                'page_subtitle': 'Tambah jenis pasien baru',
                'form_data': request.POST
            })
    
    context = {
        'page_title': 'Tambah Jenis Pasien',
        'page_subtitle': 'Tambah jenis pasien baru'
    }
    return render(request, 'admin_panel/posyandu/patient_type_form.html', context)


@login_required
def admin_panel_patient_type_update(request, patient_type_id):
    """Update patient type"""
    try:
        patient_type = get_object_or_404(PatientType, id=patient_type_id)
    except PatientType.DoesNotExist:
        messages.error(request, 'Jenis pasien tidak ditemukan!')
        return redirect('posyandu:patient_types')
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()
            description = request.POST.get('description', '').strip()
            age_min = request.POST.get('age_min')
            age_max = request.POST.get('age_max')
            is_active = request.POST.get('is_active') == 'on'
            
            # Validation
            if not name or not code:
                messages.error(request, 'Nama dan kode jenis pasien harus diisi!')
                return render(request, 'admin_panel/posyandu/patient_type_form.html', {
                    'page_title': 'Edit Jenis Pasien',
                    'page_subtitle': f'Edit jenis pasien: {patient_type.name}',
                    'patient_type': patient_type,
                    'form_data': request.POST
                })
            
            # Check if code already exists (excluding current record)
            if PatientType.objects.filter(code=code).exclude(id=patient_type_id).exists():
                messages.error(request, 'Kode jenis pasien sudah digunakan!')
                return render(request, 'admin_panel/posyandu/patient_type_form.html', {
                    'page_title': 'Edit Jenis Pasien',
                    'page_subtitle': f'Edit jenis pasien: {patient_type.name}',
                    'patient_type': patient_type,
                    'form_data': request.POST
                })
            
            # Validate age range
            if age_min and age_max and int(age_min) > int(age_max):
                messages.error(request, 'Usia minimum tidak boleh lebih besar dari usia maksimum!')
                return render(request, 'admin_panel/posyandu/patient_type_form.html', {
                    'page_title': 'Edit Jenis Pasien',
                    'page_subtitle': f'Edit jenis pasien: {patient_type.name}',
                    'patient_type': patient_type,
                    'form_data': request.POST
                })
            
            # Update patient type
            patient_type.name = name
            patient_type.code = code
            patient_type.description = description
            patient_type.age_min = int(age_min) if age_min else None
            patient_type.age_max = int(age_max) if age_max else None
            patient_type.is_active = is_active
            patient_type.save()
            
            messages.success(request, f'Jenis pasien "{patient_type.name}" berhasil diperbarui!')
            return redirect('posyandu:patient_types')
            
        except Exception as e:
            messages.error(request, f'Error updating patient type: {str(e)}')
            return render(request, 'admin_panel/posyandu/patient_type_form.html', {
                'page_title': 'Edit Jenis Pasien',
                'page_subtitle': f'Edit jenis pasien: {patient_type.name}',
                'patient_type': patient_type,
                'form_data': request.POST
            })
    
    context = {
        'page_title': 'Edit Jenis Pasien',
        'page_subtitle': f'Edit jenis pasien: {patient_type.name}',
        'patient_type': patient_type
    }
    return render(request, 'admin_panel/posyandu/patient_type_form.html', context)


@login_required
def admin_panel_patient_type_delete(request, patient_type_id):
    """Delete patient type"""
    try:
        patient_type = get_object_or_404(PatientType, id=patient_type_id)
    except PatientType.DoesNotExist:
        messages.error(request, 'Jenis pasien tidak ditemukan!')
        return redirect('posyandu:patient_types')
    
    if request.method == 'POST':
        try:
            # Check if patient type is used in health records
            from .models import HealthRecord
            health_records_count = HealthRecord.objects.filter(patient_type=patient_type.code).count()
            
            if health_records_count > 0:
                messages.error(request, f'Tidak dapat menghapus jenis pasien ini karena masih digunakan dalam {health_records_count} rekam kesehatan!')
                return redirect('posyandu:patient_types')
            
            patient_type_name = patient_type.name
            patient_type.delete()
            messages.success(request, f'Jenis pasien "{patient_type_name}" berhasil dihapus!')
            return redirect('posyandu:patient_types')
            
        except Exception as e:
            messages.error(request, f'Error deleting patient type: {str(e)}')
            return redirect('posyandu:patient_types')
    
    context = {
        'page_title': 'Hapus Jenis Pasien',
        'page_subtitle': f'Hapus jenis pasien: {patient_type.name}',
        'patient_type': patient_type
    }
    return render(request, 'admin_panel/posyandu/patient_type_delete_confirm.html', context)


@login_required
def admin_panel_patient_type_detail(request, patient_type_id):
    """View patient type details"""
    try:
        patient_type = get_object_or_404(PatientType, id=patient_type_id)
        
        # Get statistics
        from .models import HealthRecord
        health_records_count = HealthRecord.objects.filter(patient_type=patient_type.code).count()
        
        # Get recent health records
        recent_records = HealthRecord.objects.filter(patient_type=patient_type.code).order_by('-visit_date')[:10]
        
        context = {
            'page_title': 'Detail Jenis Pasien',
            'page_subtitle': f'Detail jenis pasien: {patient_type.name}',
            'patient_type': patient_type,
            'health_records_count': health_records_count,
            'recent_records': recent_records
        }
        
        return render(request, 'admin_panel/posyandu/patient_type_detail.html', context)
        
    except PatientType.DoesNotExist:
        messages.error(request, 'Jenis pasien tidak ditemukan!')
        return redirect('posyandu:patient_types')
