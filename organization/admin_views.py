from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import LembagaAdat, PenggerakPKK, Kepemudaan, KarangTaruna
from .forms import PerangkatDesaForm, LembagaAdatForm, PenggerakPKKForm, KepemudaanForm, KarangTarunaForm
from village_profile.models import VillageOfficial
# from references.models import Penduduk  # COMMENTED OUT - references app disabled
# Using letters app models instead
try:
    from letters.models import Penduduk
except ImportError:
    Penduduk = None
import json


# ADMIN PANEL VIEWS - Menggunakan template admin_panel/organization/

@login_required
def admin_organization_list(request):
    """Admin Panel - Halaman utama organisasi dengan daftar semua organisasi"""
    # Hitung statistik untuk setiap organisasi
    stats = {
        'perangkat_desa': VillageOfficial.objects.filter(is_active=True).count(),
        'lembaga_adat': LembagaAdat.objects.filter(status='aktif').count(),
        'pkk': PenggerakPKK.objects.filter(status='aktif').count(),
        'kepemudaan': Kepemudaan.objects.filter(status='aktif').count(),
        'karang_taruna': KarangTaruna.objects.filter(status='aktif').count(),
    }
    
    # Hitung total semua organisasi
    stats['total'] = sum(stats.values())
    
    context = {
        'page_title': 'Dashboard Organisasi - Admin Panel',
        'meta_description': 'Dashboard admin untuk mengelola organisasi dan lembaga di Desa Pulosarok',
        'stats': stats,
        'active_menu': 'organization',
        'active_submenu': 'dashboard'
    }
    return render(request, 'admin_panel/organization/organization_list.html', context)


@login_required
def admin_organization_hierarchy(request):
    """Admin Panel - Hierarchical view of organization structure"""
    context = {
        'page_title': 'Struktur Organisasi - Admin Panel',
        'meta_description': 'Struktur organisasi Desa Pulosarok dalam bentuk hierarki - Admin Panel',
        'active_menu': 'organization',
        'active_submenu': 'hierarchy'
    }
    return render(request, 'admin_panel/organization/organization_hierarchy.html', context)


@login_required
def admin_perangkat_desa_list(request):
    """Admin Panel - Daftar perangkat desa"""
    search_query = request.GET.get('search', '')
    jabatan_filter = request.GET.get('jabatan', '')
    status_filter = request.GET.get('status', 'aktif')
    
    perangkat = VillageOfficial.objects.select_related('penduduk', 'penduduk__dusun').filter(
        is_active=(status_filter == 'aktif')
    )
    
    if search_query:
        perangkat = perangkat.filter(
            Q(name__icontains=search_query) |
            Q(position__icontains=search_query) |
            Q(nik__icontains=search_query)
        )
    
    if jabatan_filter:
        perangkat = perangkat.filter(position=jabatan_filter)
    
    # Get jabatan choices for filter
    jabatan_choices = VillageOfficial.POSITION_CHOICES
    
    context = {
        'page_title': 'Perangkat Desa - Admin Panel',
        'meta_description': 'Kelola perangkat desa dan struktur pemerintahan Desa Pulosarok',
        'perangkat_desa': perangkat,
        'search_query': search_query,
        'jabatan_filter': jabatan_filter,
        'status_filter': status_filter,
        'jabatan_choices': jabatan_choices,
        'total_count': perangkat.count(),
        'active_menu': 'organization',
        'active_submenu': 'perangkat_desa'
    }
    return render(request, 'admin_panel/organization/perangkat_desa.html', context)


@login_required
def admin_lembaga_adat_list(request):
    """Admin Panel - Daftar lembaga adat"""
    search_query = request.GET.get('search', '')
    jenis_filter = request.GET.get('jenis', '')
    status_filter = request.GET.get('status', 'aktif')
    
    lembaga = LembagaAdat.objects.select_related('ketua', 'sekretaris', 'bendahara').filter(
        status=status_filter
    )
    
    if search_query:
        lembaga = lembaga.filter(
            Q(nama_lembaga__icontains=search_query) |
            Q(ketua__name__icontains=search_query) |
            Q(deskripsi__icontains=search_query)
        )
    
    if jenis_filter:
        lembaga = lembaga.filter(jenis_lembaga=jenis_filter)
    
    # Get jenis choices for filter
    jenis_choices = LembagaAdat.JENIS_LEMBAGA_CHOICES
    
    context = {
        'page_title': 'Lembaga Adat - Admin Panel',
        'meta_description': 'Kelola lembaga adat dan budaya di Desa Pulosarok',
        'lembaga_adat': lembaga,
        'search_query': search_query,
        'jenis_filter': jenis_filter,
        'status_filter': status_filter,
        'jenis_choices': jenis_choices,
        'total_count': lembaga.count(),
        'active_menu': 'organization',
        'active_submenu': 'lembaga_adat'
    }
    return render(request, 'admin_panel/organization/lembaga_adat.html', context)


@login_required
def admin_pkk_list(request):
    """Admin Panel - Daftar penggerak PKK"""
    search_query = request.GET.get('search', '')
    jabatan_filter = request.GET.get('jabatan', '')
    status_filter = request.GET.get('status', 'aktif')
    
    pkk = PenggerakPKK.objects.select_related('penduduk', 'penduduk__dusun').filter(
        status=status_filter
    )
    
    if search_query:
        pkk = pkk.filter(
            Q(penduduk__name__icontains=search_query) |
            Q(jabatan__icontains=search_query) |
            Q(keahlian__icontains=search_query)
        )
    
    if jabatan_filter:
        pkk = pkk.filter(jabatan=jabatan_filter)
    
    # Get jabatan choices for filter
    jabatan_choices = PenggerakPKK.JABATAN_PKK_CHOICES
    
    context = {
        'page_title': 'Tim Penggerak PKK - Admin Panel',
        'meta_description': 'Kelola penggerak PKK dan kegiatan pemberdayaan perempuan di Desa Pulosarok',
        'penggerak_pkk': pkk,
        'search_query': search_query,
        'jabatan_filter': jabatan_filter,
        'status_filter': status_filter,
        'jabatan_choices': jabatan_choices,
        'total_count': pkk.count(),
        'active_menu': 'organization',
        'active_submenu': 'pkk'
    }
    return render(request, 'admin_panel/organization/pkk.html', context)


@login_required
def admin_kepemudaan_list(request):
    """Admin Panel - Daftar organisasi kepemudaan"""
    search_query = request.GET.get('search', '')
    jenis_filter = request.GET.get('jenis', '')
    status_filter = request.GET.get('status', 'aktif')
    
    kepemudaan = Kepemudaan.objects.select_related('ketua', 'sekretaris', 'bendahara').filter(
        status=status_filter
    )
    
    if search_query:
        kepemudaan = kepemudaan.filter(
            Q(nama_organisasi__icontains=search_query) |
            Q(ketua__name__icontains=search_query) |
            Q(deskripsi__icontains=search_query)
        )
    
    if jenis_filter:
        kepemudaan = kepemudaan.filter(jenis_organisasi=jenis_filter)
    
    # Get jenis choices for filter
    jenis_choices = Kepemudaan.JENIS_ORGANISASI_CHOICES
    
    context = {
        'page_title': 'Organisasi Kepemudaan - Admin Panel',
        'meta_description': 'Kelola organisasi kepemudaan dan kegiatan pemuda di Desa Pulosarok',
        'organisasi_kepemudaan': kepemudaan,
        'search_query': search_query,
        'jenis_filter': jenis_filter,
        'status_filter': status_filter,
        'jenis_choices': jenis_choices,
        'total_count': kepemudaan.count(),
        'active_menu': 'organization',
        'active_submenu': 'kepemudaan'
    }
    return render(request, 'admin_panel/organization/kepemudaan.html', context)


@login_required
def admin_karang_taruna_list(request):
    """Admin Panel - Daftar anggota Karang Taruna"""
    search_query = request.GET.get('search', '')
    jabatan_filter = request.GET.get('jabatan', '')
    status_filter = request.GET.get('status', 'aktif')
    pengurus_filter = request.GET.get('pengurus', '')
    
    karang_taruna = KarangTaruna.objects.select_related('penduduk', 'penduduk__dusun').filter(
        status=status_filter
    )
    
    if search_query:
        karang_taruna = karang_taruna.filter(
            Q(penduduk__name__icontains=search_query) |
            Q(jabatan__icontains=search_query) |
            Q(nomor_anggota__icontains=search_query) |
            Q(bidang_keahlian__icontains=search_query)
        )
    
    if jabatan_filter:
        karang_taruna = karang_taruna.filter(jabatan=jabatan_filter)
    
    if pengurus_filter == 'inti':
        karang_taruna = karang_taruna.filter(is_pengurus_inti=True)
    elif pengurus_filter == 'biasa':
        karang_taruna = karang_taruna.filter(is_pengurus_inti=False)
    
    # Get jabatan choices for filter
    jabatan_choices = KarangTaruna.JABATAN_CHOICES
    
    context = {
        'page_title': 'Karang Taruna - Admin Panel',
        'meta_description': 'Kelola anggota Karang Taruna dan kegiatan pemuda di Desa Pulosarok',
        'karang_taruna': karang_taruna,
        'search_query': search_query,
        'jabatan_filter': jabatan_filter,
        'status_filter': status_filter,
        'pengurus_filter': pengurus_filter,
        'jabatan_choices': jabatan_choices,
        'total_count': karang_taruna.count(),
        'active_menu': 'organization',
        'active_submenu': 'karang_taruna'
    }
    return render(request, 'admin_panel/organization/karang_taruna.html', context)


# CRUD Operations for Admin Panel

@login_required
def perangkat_desa_detail(request, pk):
    """Detail Perangkat Desa"""
    perangkat = get_object_or_404(VillageOfficial.objects.select_related('penduduk', 'penduduk__dusun'), pk=pk)
    
    context = {
        'page_title': f'{perangkat.name} - {perangkat.get_position_display()}',
        'meta_description': f'Profil {perangkat.name}, {perangkat.get_position_display()} Desa Pulosarok',
        'perangkat': perangkat,
        'active_menu': 'organization',
        'active_submenu': 'perangkat_desa'
    }
    return render(request, 'admin_panel/organization/perangkat_desa_detail.html', context)


@login_required
def perangkat_desa_create(request):
    """Create new Perangkat Desa"""
    if request.method == 'POST':
        form = PerangkatDesaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                perangkat = form.save()
                messages.success(request, 'Perangkat Desa berhasil ditambahkan')
                return redirect('admin_panel:organization:admin_perangkat_desa_detail', pk=perangkat.id)
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
        else:
            messages.error(request, 'Terdapat kesalahan dalam form. Silakan periksa kembali.')
    else:
        form = PerangkatDesaForm()
    
    context = {
        'page_title': 'Tambah Perangkat Desa',
        'meta_description': 'Tambah data perangkat desa baru',
        'form': form,
        'active_menu': 'organization',
        'active_submenu': 'perangkat_desa'
    }
    return render(request, 'admin_panel/organization/perangkat_desa_form.html', context)


@login_required
def perangkat_desa_edit(request, pk):
    """Edit Perangkat Desa"""
    perangkat = get_object_or_404(VillageOfficial, pk=pk)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            penduduk_id = data.get('penduduk_id')
            jabatan = data.get('jabatan')
            nip = data.get('nip')
            status = data.get('status')
            gaji_pokok = data.get('gaji_pokok')
            
            if penduduk_id:
                perangkat.penduduk = get_object_or_404(Penduduk, id=penduduk_id)
            if jabatan:
                perangkat.jabatan = jabatan
            if nip:
                perangkat.nip = nip
            if status:
                perangkat.status = status
            if gaji_pokok:
                perangkat.gaji_pokok = gaji_pokok
            
            perangkat.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Perangkat Desa berhasil diperbarui'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'admin_panel/organization/perangkat_desa_form.html', {'perangkat': perangkat})


@login_required
def perangkat_desa_delete(request, pk):
    """Delete Perangkat Desa"""
    perangkat = get_object_or_404(VillageOfficial, pk=pk)
    
    if request.method == 'POST':
        try:
            perangkat.delete()
            return JsonResponse({
                'success': True,
                'message': 'Perangkat Desa berhasil dihapus'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def lembaga_adat_detail(request, pk):
    """Detail Lembaga Adat"""
    lembaga = get_object_or_404(LembagaAdat.objects.select_related('ketua', 'sekretaris', 'bendahara'), pk=pk)
    
    context = {
        'page_title': f'{lembaga.nama_lembaga}',
        'meta_description': f'Informasi lengkap tentang {lembaga.nama_lembaga} di Desa Pulosarok',
        'lembaga_adat': lembaga,
        'active_menu': 'organization',
        'active_submenu': 'lembaga_adat'
    }
    return render(request, 'admin_panel/organization/lembaga_adat_detail.html', context)


@login_required
def lembaga_adat_create(request):
    """Create new Lembaga Adat"""
    if request.method == 'POST':
        form = LembagaAdatForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                lembaga = form.save()
                messages.success(request, 'Lembaga Adat berhasil ditambahkan')
                return redirect('admin_panel:organization:admin_lembaga_adat_detail', pk=lembaga.id)
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
        else:
            messages.error(request, 'Terdapat kesalahan dalam form. Silakan periksa kembali.')
    else:
        form = LembagaAdatForm()
    
    context = {
        'page_title': 'Tambah Lembaga Adat',
        'meta_description': 'Tambah data lembaga adat baru',
        'form': form,
        'active_menu': 'organization',
        'active_submenu': 'lembaga_adat'
    }
    return render(request, 'admin_panel/organization/lembaga_adat_form.html', context)


@login_required
def lembaga_adat_edit(request, pk):
    """Edit Lembaga Adat"""
    lembaga = get_object_or_404(LembagaAdat, pk=pk)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nama_lembaga = data.get('nama_lembaga')
            jenis_lembaga = data.get('jenis_lembaga')
            ketua_id = data.get('ketua_id')
            sekretaris_id = data.get('sekretaris_id')
            bendahara_id = data.get('bendahara_id')
            jumlah_anggota = data.get('jumlah_anggota')
            status = data.get('status')
            
            if nama_lembaga:
                lembaga.nama_lembaga = nama_lembaga
            if jenis_lembaga:
                lembaga.jenis_lembaga = jenis_lembaga
            if ketua_id:
                lembaga.ketua = get_object_or_404(Penduduk, id=ketua_id)
            if sekretaris_id:
                lembaga.sekretaris = get_object_or_404(Penduduk, id=sekretaris_id)
            if bendahara_id:
                lembaga.bendahara = get_object_or_404(Penduduk, id=bendahara_id)
            if jumlah_anggota is not None:
                lembaga.jumlah_anggota = jumlah_anggota
            if status:
                lembaga.status = status
            
            lembaga.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Lembaga Adat berhasil diperbarui'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'admin_panel/organization/lembaga_adat_form.html', {'lembaga': lembaga})


@login_required
def lembaga_adat_delete(request, pk):
    """Delete Lembaga Adat"""
    lembaga = get_object_or_404(LembagaAdat, pk=pk)
    
    if request.method == 'POST':
        try:
            lembaga.delete()
            return JsonResponse({
                'success': True,
                'message': 'Lembaga Adat berhasil dihapus'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def pkk_detail(request, pk):
    """Detail Penggerak PKK"""
    pkk = get_object_or_404(PenggerakPKK.objects.select_related('penduduk', 'penduduk__dusun'), pk=pk)
    
    context = {
        'page_title': f'{pkk.penduduk.name} - {pkk.get_jabatan_display()}',
        'meta_description': f'Profil {pkk.penduduk.name}, {pkk.get_jabatan_display()} PKK Desa Pulosarok',
        'pkk': pkk,
        'active_menu': 'organization',
        'active_submenu': 'pkk'
    }
    return render(request, 'admin_panel/organization/pkk_detail.html', context)


@login_required
def pkk_create(request):
    """Create new Penggerak PKK"""
    if request.method == 'POST':
        form = PenggerakPKKForm(request.POST, request.FILES)
        if form.is_valid():
            pkk = form.save()
            messages.success(request, 'Penggerak PKK berhasil ditambahkan')
            return redirect('admin_panel:organization:admin_pkk_detail', pk=pkk.pk)
        else:
            messages.error(request, 'Terjadi kesalahan dalam pengisian form')
    else:
        form = PenggerakPKKForm()
    
    context = {
        'form': form,
        'page_title': 'Tambah Penggerak PKK',
        'active_menu': 'organization',
        'active_submenu': 'pkk'
    }
    return render(request, 'admin_panel/organization/pkk_form.html', context)


@login_required
def pkk_edit(request, pk):
    """Edit Penggerak PKK"""
    pkk = get_object_or_404(PenggerakPKK, pk=pk)
    
    if request.method == 'POST':
        form = PenggerakPKKForm(request.POST, request.FILES, instance=pkk)
        if form.is_valid():
            form.save()
            messages.success(request, 'Penggerak PKK berhasil diperbarui')
            return redirect('admin_panel:organization:pkk_detail', pk=pkk.pk)
        else:
            messages.error(request, 'Terjadi kesalahan dalam pengisian form')
    else:
        form = PenggerakPKKForm(instance=pkk)
    
    context = {
        'form': form,
        'pkk': pkk,
        'page_title': f'Edit {pkk.penduduk.name}',
        'active_menu': 'organization',
        'active_submenu': 'pkk'
    }
    return render(request, 'admin_panel/organization/pkk_form.html', context)


@login_required
def pkk_delete(request, pk):
    """Delete Penggerak PKK"""
    pkk = get_object_or_404(PenggerakPKK, pk=pk)
    
    if request.method == 'POST':
        try:
            pkk.delete()
            return JsonResponse({
                'success': True,
                'message': 'Penggerak PKK berhasil dihapus'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def kepemudaan_detail(request, pk):
    """Detail Organisasi Kepemudaan"""
    kepemudaan = get_object_or_404(Kepemudaan.objects.select_related('ketua', 'sekretaris', 'bendahara'), pk=pk)
    
    context = {
        'page_title': f'{kepemudaan.nama_organisasi}',
        'meta_description': f'Informasi lengkap tentang {kepemudaan.nama_organisasi} di Desa Pulosarok',
        'kepemudaan': kepemudaan,
        'active_menu': 'organization',
        'active_submenu': 'kepemudaan'
    }
    return render(request, 'admin_panel/organization/kepemudaan_detail.html', context)


@login_required
def kepemudaan_create(request):
    """Create new Kepemudaan"""
    if request.method == 'POST':
        form = KepemudaanForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                kepemudaan = form.save()
                messages.success(request, 'Organisasi Kepemudaan berhasil ditambahkan')
                return redirect('admin_panel:organization:admin_kepemudaan_detail', pk=kepemudaan.id)
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
        else:
            messages.error(request, 'Terdapat kesalahan dalam form. Silakan periksa kembali.')
    else:
        form = KepemudaanForm()
    
    context = {
        'page_title': 'Tambah Organisasi Kepemudaan',
        'meta_description': 'Tambah data organisasi kepemudaan baru',
        'form': form,
        'active_menu': 'organization',
        'active_submenu': 'kepemudaan'
    }
    return render(request, 'admin_panel/organization/kepemudaan_form.html', context)


@login_required
def kepemudaan_edit(request, pk):
    """Edit Kepemudaan"""
    kepemudaan = get_object_or_404(Kepemudaan, pk=pk)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nama_organisasi = data.get('nama_organisasi')
            jenis_organisasi = data.get('jenis_organisasi')
            ketua_id = data.get('ketua_id')
            sekretaris_id = data.get('sekretaris_id')
            bendahara_id = data.get('bendahara_id')
            jumlah_anggota_aktif = data.get('jumlah_anggota_aktif')
            rentang_usia = data.get('rentang_usia')
            status = data.get('status')
            media_sosial = data.get('media_sosial')
            visi_misi = data.get('visi_misi')
            
            if nama_organisasi:
                kepemudaan.nama_organisasi = nama_organisasi
            if jenis_organisasi:
                kepemudaan.jenis_organisasi = jenis_organisasi
            if ketua_id:
                kepemudaan.ketua = get_object_or_404(Penduduk, id=ketua_id)
            if sekretaris_id:
                kepemudaan.sekretaris = get_object_or_404(Penduduk, id=sekretaris_id)
            if bendahara_id:
                kepemudaan.bendahara = get_object_or_404(Penduduk, id=bendahara_id)
            if jumlah_anggota_aktif is not None:
                kepemudaan.jumlah_anggota_aktif = jumlah_anggota_aktif
            if rentang_usia:
                kepemudaan.rentang_usia = rentang_usia
            if status:
                kepemudaan.status = status
            if media_sosial:
                kepemudaan.media_sosial = media_sosial
            if visi_misi:
                kepemudaan.visi_misi = visi_misi
            
            kepemudaan.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Organisasi Kepemudaan berhasil diperbarui'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'admin_panel/organization/kepemudaan_form.html', {'kepemudaan': kepemudaan})


@login_required
def kepemudaan_delete(request, pk):
    """Delete Kepemudaan"""
    kepemudaan = get_object_or_404(Kepemudaan, pk=pk)
    
    if request.method == 'POST':
        try:
            kepemudaan.delete()
            return JsonResponse({
                'success': True,
                'message': 'Organisasi Kepemudaan berhasil dihapus'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def karang_taruna_detail(request, pk):
    """Detail Anggota Karang Taruna"""
    karang_taruna = get_object_or_404(KarangTaruna.objects.select_related('penduduk', 'penduduk__dusun'), pk=pk)
    
    context = {
        'page_title': f'{karang_taruna.penduduk.name} - {karang_taruna.get_jabatan_display()}',
        'meta_description': f'Profil {karang_taruna.penduduk.name}, {karang_taruna.get_jabatan_display()} Karang Taruna Desa Pulosarok',
        'karang_taruna': karang_taruna,
        'active_menu': 'organization',
        'active_submenu': 'karang_taruna'
    }
    return render(request, 'admin_panel/organization/karang_taruna_detail.html', context)


@login_required
def karang_taruna_create(request):
    """Create new Karang Taruna"""
    if request.method == 'POST':
        form = KarangTarunaForm(request.POST, request.FILES)
        if form.is_valid():
            karang_taruna = form.save()
            messages.success(request, 'Anggota Karang Taruna berhasil ditambahkan')
            return redirect('admin_panel:organization:admin_karang_taruna_detail', pk=karang_taruna.pk)
        else:
            messages.error(request, 'Terjadi kesalahan dalam pengisian form')
    else:
        form = KarangTarunaForm()
    
    context = {
        'form': form,
        'page_title': 'Tambah Anggota Karang Taruna',
        'active_menu': 'organization',
        'active_submenu': 'karang_taruna'
    }
    return render(request, 'admin_panel/organization/karang_taruna_form.html', context)


@login_required
def karang_taruna_edit(request, pk):
    """Edit Karang Taruna"""
    karang_taruna = get_object_or_404(KarangTaruna, pk=pk)
    
    if request.method == 'POST':
        form = KarangTarunaForm(request.POST, request.FILES, instance=karang_taruna)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anggota Karang Taruna berhasil diperbarui')
            return redirect('admin_panel:organization:karang_taruna_detail', pk=karang_taruna.pk)
        else:
            messages.error(request, 'Terjadi kesalahan dalam pengisian form')
    else:
        form = KarangTarunaForm(instance=karang_taruna)
    
    context = {
        'form': form,
        'karang_taruna': karang_taruna,
        'page_title': f'Edit {karang_taruna.penduduk.name}',
        'active_menu': 'organization',
        'active_submenu': 'karang_taruna'
    }
    return render(request, 'admin_panel/organization/karang_taruna_form.html', context)


@login_required
def karang_taruna_delete(request, pk):
    """Delete Karang Taruna"""
    karang_taruna = get_object_or_404(KarangTaruna, pk=pk)
    
    if request.method == 'POST':
        try:
            karang_taruna.delete()
            return JsonResponse({
                'success': True,
                'message': 'Anggota Karang Taruna berhasil dihapus'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# API Detail Views for Admin Panel

@login_required
@require_http_methods(["GET"])
def api_perangkat_desa_detail(request, pk):
    """Admin API untuk detail perangkat desa"""
    try:
        perangkat = VillageOfficial.objects.select_related('penduduk', 'penduduk__dusun').get(pk=pk)
        
        data = {
            'id': perangkat.id,
            'nama': perangkat.penduduk.name,
            'jabatan_display': perangkat.get_jabatan_display(),
            'foto': perangkat.foto_profil.url if perangkat.foto_profil else None,
            'nik': perangkat.penduduk.nik,
            'jenis_kelamin_display': perangkat.penduduk.get_gender_display() if perangkat.penduduk.gender else None,
            'tempat_lahir': perangkat.penduduk.birth_place,
            'tanggal_lahir': perangkat.penduduk.birth_date.strftime('%d %B %Y') if perangkat.penduduk.birth_date else None,
            'umur': perangkat.penduduk.age,
            'agama_display': perangkat.penduduk.get_religion_display() if perangkat.penduduk.religion else None,
            'status_perkawinan_display': perangkat.penduduk.get_marital_status_display() if perangkat.penduduk.marital_status else None,
            'pendidikan_terakhir_display': perangkat.penduduk.get_education_display() if perangkat.penduduk.education else None,
            'pekerjaan_display': perangkat.penduduk.occupation,
            'dusun': perangkat.penduduk.dusun.name if perangkat.penduduk.dusun else None,
            'lorong': perangkat.penduduk.lorong.name if perangkat.penduduk.lorong else None,
            'rt': perangkat.penduduk.rt_number,
            'rw': perangkat.penduduk.rw_number,
            'no_rumah': perangkat.penduduk.house_number,
            'tanggal_mulai_jabatan': perangkat.tanggal_mulai_tugas.strftime('%d %B %Y') if perangkat.tanggal_mulai_tugas else None,
            'tanggal_selesai_jabatan': perangkat.tanggal_selesai_tugas.strftime('%d %B %Y') if perangkat.tanggal_selesai_tugas else None,
            'status_display': perangkat.get_status_display(),
            'keterangan': getattr(perangkat, 'keterangan', None)
        }
        
        return JsonResponse(data)
    except VillageOfficial.DoesNotExist:
        return JsonResponse({'error': 'Perangkat Desa tidak ditemukan'}, status=404)


@login_required
@require_http_methods(["GET"])
def api_lembaga_adat_detail(request, pk):
    """Admin API untuk detail lembaga adat"""
    try:
        lembaga = LembagaAdat.objects.select_related('ketua', 'sekretaris', 'bendahara').get(pk=pk)
        
        data = {
            'id': lembaga.id,
            'nama_lembaga': lembaga.nama_lembaga,
            'jenis_lembaga_display': lembaga.get_jenis_lembaga_display(),
            'foto': lembaga.foto_kegiatan.url if lembaga.foto_kegiatan else None,
            'ketua_name': lembaga.ketua.name if lembaga.ketua else None,
            'sekretaris_name': lembaga.sekretaris.name if lembaga.sekretaris else None,
            'bendahara_name': lembaga.bendahara.name if lembaga.bendahara else None,
            'tanggal_terbentuk': lembaga.tanggal_terbentuk.strftime('%d %B %Y') if lembaga.tanggal_terbentuk else None,
            'jumlah_anggota': lembaga.jumlah_anggota,
            'alamat': lembaga.alamat_sekretariat,
            'keterangan': lembaga.deskripsi,
            'status_display': lembaga.get_status_display()
        }
        
        return JsonResponse(data)
    except LembagaAdat.DoesNotExist:
        return JsonResponse({'error': 'Lembaga Adat tidak ditemukan'}, status=404)


@login_required
@require_http_methods(["GET"])
def api_pkk_detail(request, pk):
    """Admin API untuk detail penggerak PKK"""
    try:
        pkk = PenggerakPKK.objects.select_related('penduduk', 'penduduk__dusun').get(pk=pk)
        
        data = {
            'id': pkk.id,
            'nama': pkk.penduduk.name,
            'jabatan_display': pkk.get_jabatan_display(),
            'foto_profil': pkk.foto_profil.url if pkk.foto_profil else None,
            'gender': pkk.penduduk.get_gender_display() if pkk.penduduk.gender else None,
            'age': pkk.penduduk.age,
            'phone': pkk.penduduk.phone_number or pkk.penduduk.mobile_number,
            'address': pkk.penduduk.full_address,
            'education': pkk.penduduk.get_education_display() if pkk.penduduk.education else None,
            'birth_place': pkk.penduduk.birth_place,
            'birth_date': pkk.penduduk.birth_date.strftime('%d %B %Y') if pkk.penduduk.birth_date else None,
            'religion': pkk.penduduk.get_religion_display() if pkk.penduduk.religion else None,
            'marital_status': pkk.penduduk.get_marital_status_display() if pkk.penduduk.marital_status else None,
            'occupation': pkk.penduduk.occupation,
            'keahlian': pkk.keahlian,
            'tanggal_mulai_tugas': pkk.tanggal_mulai_tugas.strftime('%d %B %Y') if pkk.tanggal_mulai_tugas else None,
            'tanggal_selesai_tugas': pkk.tanggal_selesai_tugas.strftime('%d %B %Y') if pkk.tanggal_selesai_tugas else None,
            'status': pkk.get_status_display(),
            'dusun': pkk.penduduk.dusun.name if pkk.penduduk.dusun else None,
            'rt_number': pkk.penduduk.rt_number,
            'rw_number': pkk.penduduk.rw_number,
            'house_number': pkk.penduduk.house_number,
            'lorong': pkk.penduduk.lorong
        }
        
        return JsonResponse(data)
    except PenggerakPKK.DoesNotExist:
        return JsonResponse({'error': 'Penggerak PKK tidak ditemukan'}, status=404)


@login_required
@require_http_methods(["GET"])
def api_kepemudaan_detail(request, pk):
    """Admin API untuk detail organisasi kepemudaan"""
    try:
        kepemudaan = Kepemudaan.objects.select_related('ketua', 'sekretaris', 'bendahara').get(pk=pk)
        
        data = {
            'id': kepemudaan.id,
            'nama_organisasi': kepemudaan.nama_organisasi,
            'jenis_organisasi_display': kepemudaan.get_jenis_organisasi_display(),
            'foto_kegiatan': kepemudaan.foto_kegiatan.url if kepemudaan.foto_kegiatan else None,
            'ketua_name': kepemudaan.ketua.name if kepemudaan.ketua else None,
            'sekretaris_name': kepemudaan.sekretaris.name if kepemudaan.sekretaris else None,
            'bendahara_name': kepemudaan.bendahara.name if kepemudaan.bendahara else None,
            'tanggal_terbentuk': kepemudaan.tanggal_terbentuk.strftime('%d %B %Y') if kepemudaan.tanggal_terbentuk else None,
            'jumlah_anggota_aktif': kepemudaan.jumlah_anggota_aktif,
            'alamat': kepemudaan.alamat_sekretariat,
            'keterangan': kepemudaan.deskripsi,
            'status_display': kepemudaan.get_status_display()
        }
        
        return JsonResponse(data)
    except Kepemudaan.DoesNotExist:
        return JsonResponse({'error': 'Organisasi Kepemudaan tidak ditemukan'}, status=404)


@login_required
@require_http_methods(["GET"])
def api_karang_taruna_detail(request, pk):
    """Admin API untuk detail anggota Karang Taruna"""
    try:
        kt = KarangTaruna.objects.select_related('penduduk', 'penduduk__dusun').get(pk=pk)
        
        data = {
            'id': kt.id,
            'nama': kt.penduduk.name,
            'jabatan_display': kt.get_jabatan_display(),
            'foto_profil': kt.foto_profil.url if kt.foto_profil else None,
            'gender': kt.penduduk.get_gender_display() if kt.penduduk.gender else None,
            'age': kt.penduduk.age,
            'phone': kt.penduduk.phone_number or kt.penduduk.mobile_number,
            'address': kt.penduduk.full_address,
            'education': kt.penduduk.get_education_display() if kt.penduduk.education else None,
            'birth_place': kt.penduduk.birth_place,
            'birth_date': kt.penduduk.birth_date.strftime('%d %B %Y') if kt.penduduk.birth_date else None,
            'religion': kt.penduduk.get_religion_display() if kt.penduduk.religion else None,
            'marital_status': kt.penduduk.get_marital_status_display() if kt.penduduk.marital_status else None,
            'occupation': kt.penduduk.occupation,
            'bidang_keahlian': kt.bidang_keahlian,
            'tanggal_mulai_tugas': kt.tanggal_bergabung.strftime('%d %B %Y') if kt.tanggal_bergabung else None,
            'tanggal_selesai_tugas': kt.tanggal_keluar.strftime('%d %B %Y') if kt.tanggal_keluar else None,
            'status': kt.get_status_display(),
            'dusun': kt.penduduk.dusun.name if kt.penduduk.dusun else None,
            'rt_number': kt.penduduk.rt_number,
            'rw_number': kt.penduduk.rw_number,
            'house_number': kt.penduduk.house_number,
            'lorong': kt.penduduk.lorong.name if kt.penduduk.lorong else None
        }
        
        return JsonResponse(data)
    except KarangTaruna.DoesNotExist:
        return JsonResponse({'error': 'Anggota Karang Taruna tidak ditemukan'}, status=404)


@login_required
def test_penduduk_search(request):
    """Test form untuk pencarian penduduk"""
    return render(request, 'admin_panel/organization/penduduk_search_form.html')