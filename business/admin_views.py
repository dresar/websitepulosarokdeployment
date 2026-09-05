from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta

from .models import (
    Business, BusinessCategory, BusinessOwner, BusinessProduct, 
    BusinessFinance, UKM, Koperasi, BUMG, Aset, LayananJasa, BusinessPageHeader,
    JenisKoperasi
)
from .forms import UKMForm, KoperasiForm, BUMGForm, LayananJasaForm, BusinessForm

# Import Penduduk from references app
try:
    from references.models import Penduduk
except ImportError:
    try:
        from letters.models import Penduduk
    except ImportError:
        Penduduk = None

# Helper functions
def is_admin(user):
    return user.is_staff or user.is_superuser

def get_business_statistics():
    """Get business statistics for dashboard"""
    stats = {
        'total_businesses': Business.objects.filter(status='approved').count(),
        'total_umkm': UKM.objects.filter(status='aktif').count(),
        'total_koperasi': Koperasi.objects.filter(status='aktif').count(),
        'total_bumg': BUMG.objects.filter(status='aktif').count(),
        'total_layanan': LayananJasa.objects.filter(status='aktif').count(),
        'pending_approvals': Business.objects.filter(status='pending').count(),
    }
    return stats

# Business Dashboard
@login_required
@user_passes_test(is_admin)
def business_dashboard(request):
    """Business dashboard view"""
    stats = get_business_statistics()
    
    # Get recent data
    recent_ukm = UKM.objects.filter(status='aktif').order_by('-created_at')[:5]
    
    # Monthly statistics
    now = timezone.now()
    monthly_registrations = UKM.objects.filter(created_at__month=now.month, created_at__year=now.year).count()
    monthly_approvals = UKM.objects.filter(status='aktif', updated_at__month=now.month, updated_at__year=now.year).count()
    
    return render(request, 'admin_panel/business/dashboard.html', {
        'total_umkm': stats['total_umkm'],
        'total_koperasi': stats['total_koperasi'],
        'total_bumg': stats['total_bumg'],
        'total_layanan': stats['total_layanan'],
        'active_ukm': stats['total_umkm'],
        'active_koperasi': stats['total_koperasi'],
        'active_bumg': stats['total_bumg'],
        'active_layanan': stats['total_layanan'],
        'total_businesses': stats['total_businesses'],
        'approved_businesses': stats['total_businesses'],
        'pending_businesses': stats['pending_approvals'],
        'total_employees': 0,  # Calculate from all businesses
        'recent_ukm': recent_ukm,
        'monthly_registrations': monthly_registrations,
        'monthly_approvals': monthly_approvals,
        'recent_registrations': UKM.objects.filter(created_at__gte=now - timedelta(days=7)).count(),
        'total_categories': BusinessCategory.objects.count()
    })

# UMKM Admin Views
@login_required
@user_passes_test(is_admin)
def admin_ukm_list(request):
    """Admin UMKM list view"""
    search = request.GET.get('search', '')
    umkm_list = UKM.objects.all().order_by('-created_at')
    
    if search:
        umkm_list = umkm_list.filter(
            Q(nama_usaha__icontains=search) |
            Q(pemilik__icontains=search) |
            Q(jenis_usaha__icontains=search)
        )
    
    paginator = Paginator(umkm_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/business/umkm_list.html', {
        'page_obj': page_obj,
        'search': search
    })

@login_required
@user_passes_test(is_admin)
def umkm_create(request):
    """Create UMKM view"""
    if request.method == 'POST':
        form = UKMForm(request.POST)
        if form.is_valid():
            try:
                ukm = form.save()
                return JsonResponse({'success': True, 'message': 'UMKM berhasil ditambahkan!'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
        else:
            return JsonResponse({'success': False, 'message': 'Form tidak valid. Silakan periksa kembali.', 'errors': form.errors}, status=400)
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = UKMForm()
            return JsonResponse({'form_data': form.initial})
        else:
            form = UKMForm()
            return render(request, 'admin_panel/business/umkm_form.html', {
                'form': form,
        'is_edit': False
    })

@login_required
@user_passes_test(is_admin)
def umkm_detail(request, umkm_id):
    """UMKM detail view"""
    ukm = get_object_or_404(UKM, id=umkm_id)
    return render(request, 'admin_panel/business/umkm_detail.html', {
        'umkm': ukm
    })

@login_required
@user_passes_test(is_admin)
def umkm_edit(request, umkm_id):
    """Edit UMKM view"""
    ukm = get_object_or_404(UKM, id=umkm_id)
    
    if request.method == 'POST':
        form = UKMForm(request.POST, instance=ukm)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'UMKM berhasil diperbarui!')
                return redirect('admin_panel:umkm_detail', umkm_id=umkm.id)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa kembali.')
    else:
        form = UKMForm(instance=ukm)
    
    return render(request, 'admin_panel/business/umkm_form.html', {
        'form': form,
        'umkm': ukm,
        'is_edit': True
    })

@login_required
@user_passes_test(is_admin)
def umkm_delete(request, umkm_id):
    """Delete UMKM view"""
    ukm = get_object_or_404(UKM, id=umkm_id)
    if request.method == 'POST':
        ukm.delete()
        messages.success(request, 'UMKM berhasil dihapus!')
        return redirect('admin_panel:umkm_list')
    return render(request, 'admin_panel/business/umkm_delete_confirm.html', {
        'umkm': ukm
    })

# Koperasi Admin Views
@login_required
@user_passes_test(is_admin)
def koperasi_list(request):
    """Admin Koperasi list view"""
    search = request.GET.get('search', '')
    koperasi_list = Koperasi.objects.all().order_by('-created_at')
    
    if search:
        koperasi_list = koperasi_list.filter(
            Q(nama_koperasi__icontains=search) |
            Q(ketua__icontains=search) |
            Q(sekretaris__icontains=search)
        )
    
    paginator = Paginator(koperasi_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/business/koperasi_admin.html', {
        'page_obj': page_obj,
        'search': search
    })

@login_required
@user_passes_test(is_admin)
def koperasi_create(request):
    """Create Koperasi view"""
    if request.method == 'POST':
        form = KoperasiForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Koperasi berhasil ditambahkan!')
                return redirect('admin_panel:koperasi_list')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa kembali input Anda.')
    else:
        form = KoperasiForm()
    
    return render(request, 'admin_panel/business/koperasi_form.html', {
        'form': form,
        'is_edit': False
    })

@login_required
@user_passes_test(is_admin)
def koperasi_detail(request, koperasi_id):
    """Koperasi detail view"""
    koperasi = get_object_or_404(Koperasi, id=koperasi_id)
    return render(request, 'admin_panel/business/koperasi_detail.html', {
        'koperasi': koperasi
    })

@login_required
@user_passes_test(is_admin)
def koperasi_edit(request, koperasi_id):
    """Edit Koperasi view"""
    koperasi = get_object_or_404(Koperasi, id=koperasi_id)
    
    if request.method == 'POST':
        form = KoperasiForm(request.POST, instance=koperasi)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Koperasi berhasil diperbarui!')
                return redirect('admin_panel:koperasi_detail', koperasi_id=koperasi.id)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa kembali input Anda.')
    else:
        form = KoperasiForm(instance=koperasi)
    
    return render(request, 'admin_panel/business/koperasi_form.html', {
        'form': form,
        'koperasi': koperasi,
        'is_edit': True
    })

@login_required
@user_passes_test(is_admin)
def koperasi_delete(request, koperasi_id):
    """Delete Koperasi view"""
    koperasi = get_object_or_404(Koperasi, id=koperasi_id)
    if request.method == 'POST':
        koperasi.delete()
        messages.success(request, 'Koperasi berhasil dihapus!')
        return redirect('admin_panel:koperasi_list')
    return render(request, 'admin_panel/business/koperasi_delete_confirm.html', {
        'koperasi': koperasi
    })

# BUMG Admin Views
@login_required
@user_passes_test(is_admin)
def bumg_list(request):
    """Admin BUMG list view"""
    search = request.GET.get('search', '')
    bumg_list = BUMG.objects.all().order_by('-created_at')
    
    if search:
        bumg_list = bumg_list.filter(
            Q(nama__icontains=search) |
            Q(direktur__icontains=search) |
            Q(bidang_usaha__icontains=search)
        )
    
    paginator = Paginator(bumg_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/business/bumg_admin.html', {
        'page_obj': page_obj,
        'search': search
    })

@login_required
@user_passes_test(is_admin)
def bumg_create(request):
    """Create BUMG view"""
    if request.method == 'POST':
        form = BUMGForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'BUMG berhasil ditambahkan!')
                return redirect('admin_panel:bumg_list')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa kembali input Anda.')
    else:
        form = BUMGForm()
    
    return render(request, 'admin_panel/business/bumg_form.html', {
        'form': form,
        'is_edit': False
    })

@login_required
@user_passes_test(is_admin)
def bumg_detail(request, bumg_id):
    """BUMG detail view"""
    bumg = get_object_or_404(BUMG, id=bumg_id)
    return render(request, 'admin_panel/business/bumg_detail.html', {
        'bumg': bumg
    })

@login_required
@user_passes_test(is_admin)
def bumg_edit(request, bumg_id):
    """Edit BUMG view"""
    bumg = get_object_or_404(BUMG, id=bumg_id)
    
    if request.method == 'POST':
        form = BUMGForm(request.POST, instance=bumg)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'BUMG berhasil diperbarui!')
                return redirect('admin_panel:bumg_detail', bumg_id=bumg.id)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa kembali input Anda.')
    else:
        form = BUMGForm(instance=bumg)
    
    return render(request, 'admin_panel/business/bumg_form.html', {
        'form': form,
        'bumg': bumg,
        'is_edit': True
    })

@login_required
@user_passes_test(is_admin)
def bumg_delete(request, bumg_id):
    """Delete BUMG view"""
    bumg = get_object_or_404(BUMG, id=bumg_id)
    if request.method == 'POST':
        bumg.delete()
        messages.success(request, 'BUMG berhasil dihapus!')
        return redirect('admin_panel:bumg_list')
    return render(request, 'admin_panel/business/bumg_delete_confirm.html', {
        'bumg': bumg
    })

# Layanan Jasa Admin Views
@login_required
@user_passes_test(is_admin)
def admin_layanan_jasa_list(request):
    """Admin Layanan Jasa list view"""
    search = request.GET.get('search', '')
    layanan_list = LayananJasa.objects.all().order_by('-created_at')
    
    if search:
        layanan_list = layanan_list.filter(
            Q(nama__icontains=search) |
            Q(penyedia__icontains=search) |
            Q(kategori__icontains=search)
        )
    
    paginator = Paginator(layanan_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/business/layanan_jasa.html', {
        'page_obj': page_obj,
        'search': search
    })

@login_required
@user_passes_test(is_admin)
def layanan_jasa_create(request):
    """Create Layanan Jasa view"""
    if request.method == 'POST':
        form = LayananJasaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Layanan Jasa berhasil ditambahkan!')
                return redirect('admin_panel:layanan_jasa_list')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa kembali input Anda.')
    else:
        form = LayananJasaForm()
    
    return render(request, 'admin_panel/business/layanan_jasa_form.html', {
        'form': form,
        'is_edit': False
    })

@login_required
@user_passes_test(is_admin)
def layanan_jasa_detail(request, layanan_id):
    """Layanan Jasa detail view"""
    layanan = get_object_or_404(LayananJasa, id=layanan_id)
    return render(request, 'admin_panel/business/layanan_jasa_detail.html', {
        'layanan': layanan
    })

@login_required
@user_passes_test(is_admin)
def layanan_jasa_edit(request, layanan_id):
    """Edit Layanan Jasa view"""
    layanan = get_object_or_404(LayananJasa, id=layanan_id)
    
    if request.method == 'POST':
        form = LayananJasaForm(request.POST, instance=layanan)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Layanan Jasa berhasil diperbarui!')
                return redirect('admin_panel:layanan_jasa_detail', layanan_id=layanan.id)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa kembali input Anda.')
    else:
        form = LayananJasaForm(instance=layanan)
    
    return render(request, 'admin_panel/business/layanan_jasa_form.html', {
        'form': form,
        'layanan': layanan,
        'is_edit': True
    })

@login_required
@user_passes_test(is_admin)
def layanan_jasa_delete(request, layanan_id):
    """Delete Layanan Jasa view"""
    layanan = get_object_or_404(LayananJasa, id=layanan_id)
    if request.method == 'POST':
        layanan.delete()
        messages.success(request, 'Layanan Jasa berhasil dihapus!')
        return redirect('admin_panel:layanan_jasa_list')
    return render(request, 'admin_panel/business/layanan_jasa_delete_confirm.html', {
        'layanan': layanan
    })

# Business Categories Admin Views
@login_required
@user_passes_test(is_admin)
def business_categories_list(request):
    """Business Categories list view"""
    categories = BusinessCategory.objects.all().order_by('name')
    return render(request, 'admin_panel/business/categories.html', {
        'categories': categories
    })

@login_required
@user_passes_test(is_admin)
def business_category_create(request):
    """Create Business Category view"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        
        if name:
            try:
                BusinessCategory.objects.create(
                    name=name,
                    description=description,
                    is_active=is_active
                )
                messages.success(request, 'Kategori berhasil ditambahkan!')
                return redirect('admin_panel:business_categories_list')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Nama kategori harus diisi!')
    
    return render(request, 'admin_panel/business/category_form.html', {
        'is_edit': False
    })

@login_required
@user_passes_test(is_admin)
def business_category_detail(request, category_id):
    """Business Category detail view"""
    category = get_object_or_404(BusinessCategory, id=category_id)
    return render(request, 'admin_panel/business/category_detail.html', {
        'category': category
    })

@login_required
@user_passes_test(is_admin)
def business_category_edit(request, category_id):
    """Edit Business Category view"""
    category = get_object_or_404(BusinessCategory, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        
        if name:
            try:
                category.name = name
                category.description = description
                category.is_active = is_active
                category.save()
                messages.success(request, 'Kategori berhasil diperbarui!')
                return redirect('admin_panel:business_category_detail', category_id=category.id)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Nama kategori harus diisi!')
    
    return render(request, 'admin_panel/business/category_form.html', {
        'category': category,
        'is_edit': True
    })

@login_required
@user_passes_test(is_admin)
def business_category_delete(request, category_id):
    """Delete Business Category view"""
    category = get_object_or_404(BusinessCategory, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Kategori berhasil dihapus!')
        return redirect('admin_panel:business_categories_list')
    return render(request, 'admin_panel/business/category_delete_confirm.html', {
        'category': category
    })

# Business Admin Views
@login_required
@user_passes_test(is_admin)
def business_list_admin(request):
    """Admin Business list view"""
    search = request.GET.get('search', '')
    business_list = Business.objects.all().order_by('-created_at')
    
    if search:
        business_list = business_list.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(address__icontains=search)
        )
    
    paginator = Paginator(business_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/business/business_list.html', {
        'page_obj': page_obj,
        'search': search
    })

@login_required
@user_passes_test(is_admin)
def business_create(request):
    """Create Business view"""
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        business_type = request.POST.get('business_type')
        description = request.POST.get('description')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        website = request.POST.get('website')
        category_id = request.POST.get('category')
        status = request.POST.get('status', 'pending')
        
        try:
            business = Business.objects.create(
                name=name,
                business_type=business_type,
                description=description,
                address=address,
                phone=phone,
                email=email,
                website=website,
                category_id=category_id,
                status=status
            )
            messages.success(request, 'Bisnis berhasil ditambahkan!')
            return redirect('admin_panel:business_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    categories = BusinessCategory.objects.filter(is_active=True)
    return render(request, 'admin_panel/business/business_form.html', {
        'categories': categories,
        'is_edit': False
    })

@login_required
@user_passes_test(is_admin)
def business_detail_admin(request, business_id):
    """Business detail view"""
    business = get_object_or_404(Business, id=business_id)
    return render(request, 'admin_panel/business/business_detail.html', {
        'business': business
    })

@login_required
@user_passes_test(is_admin)
def business_edit(request, business_id):
    """Edit Business view"""
    business = get_object_or_404(Business, id=business_id)
    
    if request.method == 'POST':
        # Handle form submission
        business.name = request.POST.get('name')
        business.business_type = request.POST.get('business_type')
        business.description = request.POST.get('description')
        business.address = request.POST.get('address')
        business.phone = request.POST.get('phone')
        business.email = request.POST.get('email')
        business.website = request.POST.get('website')
        business.category_id = request.POST.get('category')
        business.status = request.POST.get('status')
        
        try:
            business.save()
            messages.success(request, 'Bisnis berhasil diperbarui!')
            return redirect('admin_panel:business_detail', business_id=business.id)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    categories = BusinessCategory.objects.filter(is_active=True)
    return render(request, 'admin_panel/business/business_form.html', {
        'business': business,
        'categories': categories,
        'is_edit': True
    })

@login_required
@user_passes_test(is_admin)
def business_delete(request, business_id):
    """Delete Business view"""
    business = get_object_or_404(Business, id=business_id)
    if request.method == 'POST':
        business.delete()
        messages.success(request, 'Bisnis berhasil dihapus!')
        return redirect('admin_panel:business_list')
    return render(request, 'admin_panel/business/business_delete_confirm.html', {
        'business': business
    })
