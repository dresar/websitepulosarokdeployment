from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .models import LembagaAdat, PenggerakPKK, Kepemudaan, KarangTaruna
from village_profile.models import VillageOfficial
# # from references.models import Penduduk  # COMMENTED OUT - references app disabled  # COMMENTED OUT - references app disabled
# Using letters app models instead
try:
    from letters.models import Penduduk  # COMMENTED OUT - references app disabled
except ImportError:
    Penduduk  # COMMENTED OUT - references app disabled = None
# Using letters app Penduduk model instead
try:
    from letters.models import Penduduk
except ImportError:
    Penduduk = None
import json


def organization_list(request):
    """PUBLIC - Halaman utama organisasi dengan daftar semua organisasi"""
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
        'page_title': 'Organisasi Desa Pulosarok',
        'meta_description': 'Daftar lengkap organisasi dan lembaga di Desa Pulosarok',
        'stats': stats
    }
    return render(request, 'public/organization/organization_list.html', context)


def organization_hierarchy(request):
    """PUBLIC - Hierarchical view of organization structure"""
    # Calculate statistics for hierarchy
    stats = {
        'kepala_desa': VillageOfficial.objects.filter(position='kepala_desa', is_active=True).count(),
        'sekretaris_desa': VillageOfficial.objects.filter(position='sekretaris_desa', is_active=True).count(),
        'kaur_kasi': VillageOfficial.objects.filter(
            position__in=['kaur_pemerintahan', 'kaur_pembangunan', 'kaur_kesra', 'kaur_keuangan', 'kaur_umum', 
                         'kasi_pemerintahan', 'kasi_pembangunan', 'kasi_kesra'], 
            is_active=True
        ).count(),
        'kepala_dusun': VillageOfficial.objects.filter(position='kepala_dusun', is_active=True).count(),
    }
    
    context = {
        'page_title': 'Struktur Organisasi Hierarkis',
        'meta_description': 'Struktur organisasi Desa Pulosarok dalam bentuk hierarki',
        'stats': stats
    }
    return render(request, 'public/organization/organization_hierarchy.html', context)


def perangkat_desa_list(request):
    """Daftar perangkat desa"""
    search_query = request.GET.get('search', '')
    jabatan_filter = request.GET.get('jabatan', '')
    status_filter = request.GET.get('status', 'aktif')
    
    perangkat = VillageOfficial.objects.select_related('village').filter(
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
    
    # Calculate statistics
    stats = {
        'total_perangkat': VillageOfficial.objects.filter(is_active=True).count(),
        'kepala_desa': VillageOfficial.objects.filter(position='kepala_desa', is_active=True).count(),
        'sekretaris_desa': VillageOfficial.objects.filter(position='sekretaris_desa', is_active=True).count(),
        'kaur_kasi': VillageOfficial.objects.filter(
            position__in=['kaur_pemerintahan', 'kaur_pembangunan', 'kaur_kesra', 'kaur_keuangan', 'kaur_umum', 
                         'kasi_pemerintahan', 'kasi_pembangunan', 'kasi_kesra'], 
            is_active=True
        ).count(),
        'kepala_dusun': VillageOfficial.objects.filter(position='kepala_dusun', is_active=True).count(),
    }
    
    context = {
        'page_title': 'Perangkat Desa Pulosarok',
        'meta_description': 'Daftar perangkat desa dan struktur pemerintahan Desa Pulosarok',
        'perangkat_desa': perangkat,
        'search_query': search_query,
        'jabatan_filter': jabatan_filter,
        'status_filter': status_filter,
        'jabatan_choices': jabatan_choices,
        'total_count': perangkat.count(),
        'stats': stats
    }
    return render(request, 'public/organization/perangkat_desa_list.html', context)


def perangkat_desa_detail(request, pk):
    """Detail perangkat desa"""
    perangkat = get_object_or_404(VillageOfficial.objects.select_related('village'), pk=pk)
    
    context = {
        'page_title': f'{perangkat.name} - {perangkat.get_position_display()}',
        'meta_description': f'Profil {perangkat.name}, {perangkat.get_position_display()} Desa Pulosarok',
        'perangkat': perangkat
    }
    return render(request, 'public/organization/perangkat_desa_detail.html', context)


def lembaga_adat_list(request):
    """Daftar lembaga adat"""
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
    
    # Pagination
    paginator = Paginator(lembaga, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get jenis choices for filter
    jenis_choices = LembagaAdat.JENIS_LEMBAGA_CHOICES
    
    # Calculate statistics
    stats = {
        'total_lembaga': LembagaAdat.objects.filter(status='aktif').count(),
        'total_anggota': LembagaAdat.objects.filter(status='aktif').aggregate(
            total=Count('jumlah_anggota')
        )['total'] or 0,
        'jenis_lembaga': len(LembagaAdat.JENIS_LEMBAGA_CHOICES),
        'tahun_aktif': 2024,  # This could be calculated from the data
    }
    
    context = {
        'page_title': 'Lembaga Adat Desa Pulosarok',
        'meta_description': 'Daftar lembaga adat dan budaya di Desa Pulosarok',
        'lembaga_adat': lembaga,
        'search_query': search_query,
        'jenis_filter': jenis_filter,
        'status_filter': status_filter,
        'jenis_choices': jenis_choices,
        'total_count': lembaga.count(),
        'stats': stats
    }
    return render(request, 'public/organization/lembaga_adat_list.html', context)


def lembaga_adat_detail(request, pk):
    """Detail lembaga adat"""
    lembaga = get_object_or_404(LembagaAdat.objects.select_related('ketua', 'sekretaris', 'bendahara'), pk=pk)
    
    context = {
        'page_title': f'{lembaga.nama_lembaga}',
        'meta_description': f'Informasi lengkap tentang {lembaga.nama_lembaga} di Desa Pulosarok',
        'lembaga': lembaga
    }
    return render(request, 'public/organization/lembaga_adat_detail.html', context)


def pkk_list(request):
    """Daftar penggerak PKK"""
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
    
    # Pagination
    paginator = Paginator(pkk, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get jabatan choices for filter
    jabatan_choices = PenggerakPKK.JABATAN_PKK_CHOICES
    
    # Calculate statistics
    total_penggerak = PenggerakPKK.objects.filter(status='aktif').count()
    aktif_count = PenggerakPKK.objects.filter(status='aktif').count()
    persentase_aktif = (aktif_count / total_penggerak * 100) if total_penggerak > 0 else 0
    
    stats = {
        'total_penggerak': total_penggerak,
        'ketua': PenggerakPKK.objects.filter(jabatan='ketua_tim_penggerak', status='aktif').count(),
        'pokja': len([choice for choice in PenggerakPKK.JABATAN_PKK_CHOICES if 'pokja' in choice[0]]),
        'persentase_aktif': round(persentase_aktif),
        'tahun_aktif': 2024,  # This could be calculated from the data
    }
    
    context = {
        'page_title': 'Tim Penggerak PKK Desa Pulosarok',
        'meta_description': 'Daftar penggerak PKK dan kegiatan pemberdayaan perempuan di Desa Pulosarok',
        'penggerak_pkk': pkk,
        'search_query': search_query,
        'jabatan_filter': jabatan_filter,
        'status_filter': status_filter,
        'jabatan_choices': jabatan_choices,
        'total_count': pkk.count(),
        'stats': stats
    }
    return render(request, 'public/organization/pkk_list.html', context)


def pkk_detail(request, pk):
    """Detail penggerak PKK"""
    pkk = get_object_or_404(PenggerakPKK.objects.select_related('penduduk', 'penduduk__dusun'), pk=pk)
    
    context = {
        'page_title': f'{pkk.penduduk.name} - {pkk.get_jabatan_display()}',
        'meta_description': f'Profil {pkk.penduduk.name}, {pkk.get_jabatan_display()} PKK Desa Pulosarok',
        'pkk': pkk
    }
    return render(request, 'public/organization/pkk_detail.html', context)


def kepemudaan_list(request):
    """Daftar organisasi kepemudaan"""
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
    
    # Pagination
    paginator = Paginator(kepemudaan, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get jenis choices for filter
    jenis_choices = Kepemudaan.JENIS_ORGANISASI_CHOICES
    
    # Calculate statistics
    stats = {
        'total_organisasi': Kepemudaan.objects.filter(status='aktif').count(),
        'total_anggota': Kepemudaan.objects.filter(status='aktif').aggregate(
            total=Count('jumlah_anggota_aktif')
        )['total'] or 0,
        'jenis_organisasi': len(Kepemudaan.JENIS_ORGANISASI_CHOICES),
        'tahun_aktif': 2024,  # This could be calculated from the data
    }
    
    context = {
        'page_title': 'Organisasi Kepemudaan Desa Pulosarok',
        'meta_description': 'Daftar organisasi kepemudaan dan kegiatan pemuda di Desa Pulosarok',
        'organisasi_kepemudaan': kepemudaan,
        'search_query': search_query,
        'jenis_filter': jenis_filter,
        'status_filter': status_filter,
        'jenis_choices': jenis_choices,
        'total_count': kepemudaan.count(),
        'stats': stats
    }
    return render(request, 'public/organization/kepemudaan_list.html', context)


def kepemudaan_detail(request, pk):
    """Detail organisasi kepemudaan"""
    kepemudaan = get_object_or_404(Kepemudaan.objects.select_related('ketua', 'sekretaris', 'bendahara'), pk=pk)
    
    context = {
        'page_title': f'{kepemudaan.nama_organisasi}',
        'meta_description': f'Informasi lengkap tentang {kepemudaan.nama_organisasi} di Desa Pulosarok',
        'kepemudaan': kepemudaan
    }
    return render(request, 'public/organization/kepemudaan_detail.html', context)


def karang_taruna_list(request):
    """Daftar anggota Karang Taruna"""
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
    
    # Pagination
    paginator = Paginator(karang_taruna, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get jabatan choices for filter
    jabatan_choices = KarangTaruna.JABATAN_CHOICES
    
    # Calculate statistics
    total_anggota = KarangTaruna.objects.filter(status='aktif').count()
    aktif_count = KarangTaruna.objects.filter(status='aktif').count()
    persentase_aktif = (aktif_count / total_anggota * 100) if total_anggota > 0 else 0
    
    stats = {
        'total_anggota': total_anggota,
        'ketua': KarangTaruna.objects.filter(jabatan='ketua_umum', status='aktif').count(),
        'persentase_aktif': round(persentase_aktif),
        'tahun_aktif': 2024,  # This could be calculated from the data
    }
    
    context = {
        'page_title': 'Karang Taruna Desa Pulosarok',
        'meta_description': 'Daftar anggota Karang Taruna dan kegiatan pemuda di Desa Pulosarok',
        'karang_taruna': karang_taruna,
        'page_obj': page_obj,
        'search_query': search_query,
        'jabatan_filter': jabatan_filter,
        'status_filter': status_filter,
        'pengurus_filter': pengurus_filter,
        'jabatan_choices': jabatan_choices,
        'total_count': karang_taruna.count(),
        'stats': stats
    }
    return render(request, 'public/organization/karang_taruna_list.html', context)


def karang_taruna_detail(request, pk):
    """Detail anggota Karang Taruna"""
    karang_taruna = get_object_or_404(KarangTaruna.objects.select_related('penduduk', 'penduduk__dusun'), pk=pk)
    
    context = {
        'page_title': f'{karang_taruna.penduduk.name} - {karang_taruna.get_jabatan_display()}',
        'meta_description': f'Profil {karang_taruna.penduduk.name}, {karang_taruna.get_jabatan_display()} Karang Taruna Desa Pulosarok',
        'karang_taruna': karang_taruna,
        'anggota': karang_taruna
    }
    return render(request, 'public/organization/karang_taruna_detail.html', context)


# PUBLIC API Views for read-only access
@require_http_methods(["GET"])
def api_organization_stats(request):
    """PUBLIC API untuk statistik organisasi (read-only)"""
    stats = {
        'perangkat_desa': VillageOfficial.objects.filter(is_active=True).count(),
        'lembaga_adat': LembagaAdat.objects.filter(status='aktif').count(),
        'penggerak_pkk': PenggerakPKK.objects.filter(status='aktif').count(),
        'kepemudaan': Kepemudaan.objects.filter(status='aktif').count(),
        'karang_taruna': KarangTaruna.objects.filter(status='aktif').count(),
        'total_members': (
            VillageOfficial.objects.filter(is_active=True).count() +
            PenggerakPKK.objects.filter(status='aktif').count() +
            KarangTaruna.objects.filter(status='aktif').count()
        ),
        'total_penduduk': Penduduk.objects.filter(is_active=True, is_alive=True).count(),
    }
    return JsonResponse(stats)


@require_http_methods(["GET"])
def api_search_penduduk(request):
    """API untuk pencarian penduduk"""
    query = request.GET.get('q', '')
    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    gender = request.GET.get('gender')
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    penduduk = Penduduk.objects.filter(
        Q(name__icontains=query) | Q(nik__icontains=query),
        is_active=True,
        is_alive=True
    )
    
    # Filter berdasarkan usia jika ada parameter
    if age_min:
        penduduk = penduduk.filter(age__gte=int(age_min))
    if age_max:
        penduduk = penduduk.filter(age__lte=int(age_max))
    
    # Filter berdasarkan jenis kelamin jika ada parameter
    if gender:
        penduduk = penduduk.filter(gender=gender)
    
    penduduk = penduduk[:10]
    
    results = []
    for p in penduduk:
        results.append({
            'id': p.id,
            'name': p.name,
            'nik': p.nik,
            'age': p.age,
            'gender': p.get_gender_display() if p.gender else None,
            'birth_date': p.birth_date.strftime('%Y-%m-%d') if p.birth_date else None,
            'alamat': p.full_address,
            'phone': p.phone_number or p.mobile_number,
            'education': p.get_education_display() if p.education else None,
            'pekerjaan': p.occupation,
            'foto_profil': p.photo.url if p.photo else None
        })
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def api_village_officials(request):
    """API endpoint untuk data perangkat desa"""
    search = request.GET.get('search', '')
    jabatan = request.GET.get('jabatan', '')
    status = request.GET.get('status', 'aktif')
    
    officials = VillageOfficial.objects.select_related('village').filter(
        is_active=(status == 'aktif')
    )
    
    if search:
        officials = officials.filter(
            Q(name__icontains=search) |
            Q(position__icontains=search) |
            Q(nik__icontains=search)
        )
    
    if jabatan:
        officials = officials.filter(position=jabatan)
    
    results = []
    for official in officials:
        results.append({
            'id': official.id,
            'penduduk_name': official.name,
            'penduduk_age': None,  # Age calculation would need birth_date
            'penduduk_gender': official.get_gender_display() if official.gender else None,
            'penduduk_education': official.get_education_display() if official.education else None,
            'penduduk_occupation': official.occupation,
            'penduduk_dusun': official.dusun,
            'penduduk_lorong': official.lorong,
            'jabatan': official.position,
            'jabatan_display': official.get_position_display(),
            'tanggal_mulai_tugas': official.start_date.strftime('%Y-%m-%d') if official.start_date else None,
            'tanggal_selesai_tugas': official.end_date.strftime('%Y-%m-%d') if official.end_date else None,
            'status': 'aktif' if official.is_active else 'non_aktif',
            'status_display': 'Aktif' if official.is_active else 'Non Aktif',
            'foto_profil': official.photo.url if official.photo else None,
            'experience': official.experience,
            'created_at': official.created_at.strftime('%Y-%m-%d %H:%M') if official.created_at else None,
            'updated_at': official.updated_at.strftime('%Y-%m-%d %H:%M') if official.updated_at else None
        })
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def api_lembaga_adat(request):
    """API untuk data lembaga adat"""
    search = request.GET.get('search', '')
    jenis = request.GET.get('jenis', '')
    status = request.GET.get('status', 'aktif')
    
    institutions = LembagaAdat.objects.select_related('ketua', 'sekretaris', 'bendahara').filter(
        status=status
    )
    
    if search:
        institutions = institutions.filter(
            Q(nama_lembaga__icontains=search) |
            Q(ketua__name__icontains=search) |
            Q(deskripsi__icontains=search)
        )
    
    if jenis:
        institutions = institutions.filter(jenis_lembaga=jenis)
    
    results = []
    for institution in institutions:
        results.append({
            'id': institution.id,
            'nama_lembaga': institution.nama_lembaga,
            'jenis_lembaga': institution.jenis_lembaga,
            'jenis_lembaga_display': institution.get_jenis_lembaga_display(),
            'ketua_name': institution.ketua.name if institution.ketua else None,
            'sekretaris_name': institution.sekretaris.name if institution.sekretaris else None,
            'bendahara_name': institution.bendahara.name if institution.bendahara else None,
            'tanggal_terbentuk': institution.tanggal_terbentuk.strftime('%Y-%m-%d') if institution.tanggal_terbentuk else None,
            'alamat_sekretariat': institution.alamat_sekretariat,
            'deskripsi': institution.deskripsi,
            'kegiatan_rutin': institution.kegiatan_rutin,
            'jumlah_anggota': institution.jumlah_anggota,
            'status': institution.status,
            'status_display': institution.get_status_display(),
            'kontak_phone': institution.kontak_phone,
            'foto_kegiatan': institution.foto_kegiatan.url if institution.foto_kegiatan else None,
            'created_at': institution.created_at.strftime('%Y-%m-%d %H:%M') if institution.created_at else None,
            'updated_at': institution.updated_at.strftime('%Y-%m-%d %H:%M') if institution.updated_at else None
        })
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def api_penggerak_pkk(request):
    """API untuk data penggerak PKK"""
    search = request.GET.get('search', '')
    jabatan = request.GET.get('jabatan', '')
    status = request.GET.get('status', 'aktif')
    
    pkk_members = PenggerakPKK.objects.select_related('penduduk', 'penduduk__dusun').filter(
        status=status
    )
    
    if search:
        pkk_members = pkk_members.filter(
            Q(penduduk__name__icontains=search) |
            Q(jabatan__icontains=search) |
            Q(nomor_anggota__icontains=search) |
            Q(keahlian__icontains=search)
        )
    
    if jabatan:
        pkk_members = pkk_members.filter(jabatan=jabatan)
    
    results = []
    for member in pkk_members:
        results.append({
            'id': member.id,
            'penduduk_name': member.penduduk.name,
            'penduduk_age': member.penduduk.age,
            'penduduk_gender': member.penduduk.get_gender_display() if member.penduduk.gender else None,
            'penduduk_education': member.penduduk.get_education_display() if member.penduduk.education else None,
            'penduduk_occupation': member.penduduk.occupation,
            'penduduk_dusun': member.penduduk.dusun.name if member.penduduk.dusun else None,
            'penduduk_lorong': member.penduduk.lorong.nama_lorong if member.penduduk.lorong else None,
            'jabatan': member.jabatan,
            'jabatan_display': member.get_jabatan_display(),
            'nomor_anggota': member.nomor_anggota,
            'tanggal_bergabung': member.tanggal_bergabung.strftime('%Y-%m-%d') if member.tanggal_bergabung else None,
            'tanggal_keluar': member.tanggal_keluar.strftime('%Y-%m-%d') if member.tanggal_keluar else None,
            'status': member.status,
            'status_display': member.get_status_display(),
            'keahlian': member.keahlian,
            'pengalaman_organisasi': member.pengalaman_organisasi,
            'prestasi': member.prestasi,
            'foto_profil': member.foto_profil.url if member.foto_profil else None,
            'created_at': member.created_at.strftime('%Y-%m-%d %H:%M') if member.created_at else None,
            'updated_at': member.updated_at.strftime('%Y-%m-%d %H:%M') if member.updated_at else None
        })
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def api_kepemudaan(request):
    """API untuk data kepemudaan"""
    search = request.GET.get('search', '')
    jenis = request.GET.get('jenis', '')
    status = request.GET.get('status', 'aktif')
    
    youth_members = Kepemudaan.objects.select_related('ketua', 'sekretaris', 'bendahara').filter(
        status=status
    )
    
    if search:
        youth_members = youth_members.filter(
            Q(nama_organisasi__icontains=search) |
            Q(ketua__name__icontains=search) |
            Q(deskripsi__icontains=search)
        )
    
    if jenis:
        youth_members = youth_members.filter(jenis_organisasi=jenis)
    
    results = []
    for member in youth_members:
        results.append({
            'id': member.id,
            'nama_organisasi': member.nama_organisasi,
            'jenis_organisasi': member.jenis_organisasi,
            'jenis_organisasi_display': member.get_jenis_organisasi_display(),
            'ketua_name': member.ketua.name if member.ketua else None,
            'sekretaris_name': member.sekretaris.name if member.sekretaris else None,
            'bendahara_name': member.bendahara.name if member.bendahara else None,
            'tanggal_terbentuk': member.tanggal_terbentuk.strftime('%Y-%m-%d') if member.tanggal_terbentuk else None,
            'jumlah_anggota_aktif': member.jumlah_anggota_aktif,
            'rentang_usia': member.rentang_usia,
            'kegiatan_rutin': member.kegiatan_rutin,
            'prestasi': member.prestasi,
            'alamat_sekretariat': member.alamat_sekretariat,
            'status': member.status,
            'status_display': member.get_status_display(),
            'kontak_phone': member.kontak_phone,
            'email': member.email,
            'foto_kegiatan': member.foto_kegiatan.url if member.foto_kegiatan else None,
            'deskripsi': member.deskripsi,
            'media_sosial': member.media_sosial,
            'visi_misi': member.visi_misi,
            'created_at': member.created_at.strftime('%Y-%m-%d %H:%M') if member.created_at else None,
            'updated_at': member.updated_at.strftime('%Y-%m-%d %H:%M') if member.updated_at else None
        })
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def api_karang_taruna(request):
    """API untuk data karang taruna"""
    search = request.GET.get('search', '')
    jabatan = request.GET.get('jabatan', '')
    status = request.GET.get('status', 'aktif')
    pengurus_inti = request.GET.get('pengurus_inti', '')
    
    kt_members = KarangTaruna.objects.select_related('penduduk', 'penduduk__dusun').filter(
        status=status
    )
    
    if search:
        kt_members = kt_members.filter(
            Q(penduduk__name__icontains=search) |
            Q(jabatan__icontains=search) |
            Q(nomor_anggota__icontains=search) |
            Q(bidang_keahlian__icontains=search)
        )
    
    if jabatan:
        kt_members = kt_members.filter(jabatan=jabatan)
    
    if pengurus_inti == 'true':
        kt_members = kt_members.filter(is_pengurus_inti=True)
    elif pengurus_inti == 'false':
        kt_members = kt_members.filter(is_pengurus_inti=False)
    
    results = []
    for member in kt_members:
        results.append({
            'id': member.id,
            'penduduk_name': member.penduduk.name,
            'penduduk_age': member.penduduk.age,
            'penduduk_gender': member.penduduk.get_gender_display() if member.penduduk.gender else None,
            'penduduk_education': member.penduduk.get_education_display() if member.penduduk.education else None,
            'penduduk_occupation': member.penduduk.occupation,
            'penduduk_dusun': member.penduduk.dusun.name if member.penduduk.dusun else None,
            'penduduk_lorong': member.penduduk.lorong.nama_lorong if member.penduduk.lorong else None,
            'jabatan': member.jabatan,
            'jabatan_display': member.get_jabatan_display(),
            'nomor_anggota': member.nomor_anggota,
            'tanggal_bergabung': member.tanggal_bergabung.strftime('%Y-%m-%d') if member.tanggal_bergabung else None,
            'tanggal_keluar': member.tanggal_keluar.strftime('%Y-%m-%d') if member.tanggal_keluar else None,
            'status': member.status,
            'status_display': member.get_status_display(),
            'bidang_keahlian': member.bidang_keahlian,
            'pengalaman_organisasi': member.pengalaman_organisasi,
            'prestasi_individu': member.prestasi_individu,
            'kontribusi': member.kontribusi,
            'foto_profil': member.foto_profil.url if member.foto_profil else None,
            'pendidikan_terakhir': member.pendidikan_terakhir,
            'pekerjaan': member.pekerjaan,
            'is_pengurus_inti': member.is_pengurus_inti,
            'created_at': member.created_at.strftime('%Y-%m-%d %H:%M') if member.created_at else None,
            'updated_at': member.updated_at.strftime('%Y-%m-%d %H:%M') if member.updated_at else None
        })
    
    return JsonResponse({'results': results})


@require_http_methods(["GET"])
def api_perangkat_desa_detail(request, pk):
    """API untuk detail perangkat desa"""
    try:
        perangkat = VillageOfficial.objects.select_related('village').get(pk=pk)
        
        data = {
            'id': perangkat.id,
            'nama': perangkat.name,
            'jabatan_display': perangkat.get_position_display(),
            'foto': perangkat.photo.url if perangkat.photo else None,
            'jenis_kelamin_display': perangkat.get_gender_display() if perangkat.gender else None,
            'umur': None,  # Age calculation would need birth_date
            'pendidikan_terakhir_display': perangkat.get_education_display() if perangkat.education else None,
            'pekerjaan_display': perangkat.occupation,
            'dusun': perangkat.dusun,
            'lorong': perangkat.lorong,
            'tanggal_mulai_jabatan': perangkat.start_date.strftime('%d %B %Y') if perangkat.start_date else None,
            'tanggal_selesai_jabatan': perangkat.end_date.strftime('%d %B %Y') if perangkat.end_date else None,
            'status_display': 'Aktif' if perangkat.is_active else 'Non Aktif',
            'keterangan': perangkat.experience or ''
        }
        
        return JsonResponse(data)
    except VillageOfficial.DoesNotExist:
        return JsonResponse({'error': 'Perangkat Desa tidak ditemukan'}, status=404)


@require_http_methods(["GET"])
def api_lembaga_adat_detail(request, pk):
    """API untuk detail lembaga adat"""
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


@require_http_methods(["GET"])
def api_pkk_detail(request, pk):
    """API untuk detail penggerak PKK"""
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


@require_http_methods(["GET"])
def api_kepemudaan_detail(request, pk):
    """API untuk detail organisasi kepemudaan"""
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


@require_http_methods(["GET"])
def api_karang_taruna_detail(request, pk):
    """API untuk detail anggota Karang Taruna"""
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


@require_http_methods(["GET"])
def api_organization_structure(request):
    """API untuk struktur organisasi"""
    # Mengambil data struktur organisasi dari semua entitas
    structure = {
        'kepala_desa': None,
        'sekretaris_desa': None,
        'kaur_pemerintahan': None,
        'kaur_pembangunan': None,
        'kaur_kesra': None,
        'kepala_dusun': []
    }
    
    # Perangkat Desa - Kepala Desa
    try:
        kepala_desa = VillageOfficial.objects.filter(is_active=True, position='KEPALA_DESA').select_related('penduduk').first()
        if kepala_desa:
            structure['kepala_desa'] = {
                'name': kepala_desa.name,
                'nik': kepala_desa.nik,
                'photo': kepala_desa.photo.url if kepala_desa.photo else None
            }
    except:
        pass
    
    # Sekretaris Desa
    try:
        sekretaris = VillageOfficial.objects.filter(is_active=True, position='SEKRETARIS').select_related('penduduk').first()
        if sekretaris:
            structure['sekretaris_desa'] = {
                'name': sekretaris.name,
                'nik': sekretaris.nik,
                'photo': sekretaris.photo.url if sekretaris.photo else None
            }
    except:
        pass
    
    # Kaur Pemerintahan
    try:
        kaur_pemerintahan = VillageOfficial.objects.filter(is_active=True, position='KAUR_PEMERINTAHAN').select_related('penduduk').first()
        if kaur_pemerintahan:
            structure['kaur_pemerintahan'] = {
                'name': kaur_pemerintahan.name,
                'nik': kaur_pemerintahan.nik,
                'photo': kaur_pemerintahan.photo.url if kaur_pemerintahan.photo else None
            }
    except:
        pass
    
    # Kaur Pembangunan
    try:
        kaur_pembangunan = VillageOfficial.objects.filter(is_active=True, position='KAUR_PEMBANGUNAN').select_related('penduduk').first()
        if kaur_pembangunan:
            structure['kaur_pembangunan'] = {
                'name': kaur_pembangunan.name,
                'nik': kaur_pembangunan.nik,
                'photo': kaur_pembangunan.photo.url if kaur_pembangunan.photo else None
            }
    except:
        pass
    
    # Kaur Kesra
    try:
        kaur_kesra = VillageOfficial.objects.filter(is_active=True, position='KAUR_KESRA').select_related('penduduk').first()
        if kaur_kesra:
            structure['kaur_kesra'] = {
                'name': kaur_kesra.name,
                'nik': kaur_kesra.nik,
                'photo': kaur_kesra.photo.url if kaur_kesra.photo else None
            }
    except:
        pass
    
    # Kepala Dusun
    try:
        kepala_dusun_list = VillageOfficial.objects.filter(is_active=True, position='KADUS').select_related('village')
        for kades in kepala_dusun_list:
            structure['kepala_dusun'].append({
                'name': kades.name,
                'nik': kades.nik,
                'dusun': kades.penduduk.dusun.name if kades.penduduk and kades.penduduk.dusun else None,
                'photo': kades.photo.url if kades.photo else None
            })
    except:
        pass
    
    return JsonResponse(structure)


@require_http_methods(["GET"])
def api_organizations(request):
    """API endpoint untuk mendapatkan daftar semua organisasi"""
    try:
        organizations = []
        
        # Perangkat Desa
        perangkat_desa = VillageOfficial.objects.filter(is_active=True).select_related('village')
        for official in perangkat_desa:
            organizations.append({
                'id': official.id,
                'name': f'Perangkat Desa - {official.name}',
                'type': 'perangkat-desa',
                'type_display': 'Perangkat Desa',
                'description': f'Jabatan: {official.position}',
                'member_count': 1,
                'activity_count': 0,
                'is_active': official.is_active,
                'created_at': official.created_at.isoformat() if hasattr(official, 'created_at') else None
            })
        
        # Lembaga Adat
        lembaga_adat = LembagaAdat.objects.filter(status='aktif')
        for lembaga in lembaga_adat:
            organizations.append({
                'id': lembaga.id,
                'name': lembaga.name,
                'type': 'lembaga-adat',
                'type_display': 'Lembaga Adat',
                'description': lembaga.description or 'Lembaga adat desa',
                'member_count': lembaga.members.count() if hasattr(lembaga, 'members') else 0,
                'activity_count': 0,
                'is_active': lembaga.status == 'aktif',
                'created_at': lembaga.created_at.isoformat() if hasattr(lembaga, 'created_at') else None
            })
        
        # PKK
        pkk = PenggerakPKK.objects.filter(status='aktif')
        for pkk_item in pkk:
            organizations.append({
                'id': pkk_item.id,
                'name': f'PKK - {pkk_item.name}',
                'type': 'pkk',
                'type_display': 'PKK',
                'description': f'Jabatan: {pkk_item.position}',
                'member_count': 1,
                'activity_count': 0,
                'is_active': pkk_item.status == 'aktif',
                'created_at': pkk_item.created_at.isoformat() if hasattr(pkk_item, 'created_at') else None
            })
        
        # Kepemudaan
        kepemudaan = Kepemudaan.objects.filter(status='aktif')
        for kepemudaan_item in kepemudaan:
            organizations.append({
                'id': kepemudaan_item.id,
                'name': f'Kepemudaan - {kepemudaan_item.name}',
                'type': 'kepemudaan',
                'type_display': 'Kepemudaan',
                'description': f'Jabatan: {kepemudaan_item.position}',
                'member_count': 1,
                'activity_count': 0,
                'is_active': kepemudaan_item.status == 'aktif',
                'created_at': kepemudaan_item.created_at.isoformat() if hasattr(kepemudaan_item, 'created_at') else None
            })
        
        # Karang Taruna
        karang_taruna = KarangTaruna.objects.filter(status='aktif')
        for karang_taruna_item in karang_taruna:
            organizations.append({
                'id': karang_taruna_item.id,
                'name': f'Karang Taruna - {karang_taruna_item.name}',
                'type': 'karang-taruna',
                'type_display': 'Karang Taruna',
                'description': f'Jabatan: {karang_taruna_item.position}',
                'member_count': 1,
                'activity_count': 0,
                'is_active': karang_taruna_item.status == 'aktif',
                'created_at': karang_taruna_item.created_at.isoformat() if hasattr(karang_taruna_item, 'created_at') else None
            })
        
        return JsonResponse({
            'success': True,
            'organizations': organizations
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@require_http_methods(["GET"])
def api_statistics(request):
    """API endpoint untuk mendapatkan statistik organisasi"""
    try:
        stats = {
            'total_organizations': 0,
            'total_members': 0,
            'active_organizations': 0,
            'total_activities': 0
        }
        
        # Count perangkat desa
        perangkat_desa_count = VillageOfficial.objects.filter(is_active=True).count()
        stats['total_organizations'] += perangkat_desa_count
        stats['active_organizations'] += perangkat_desa_count
        stats['total_members'] += perangkat_desa_count
        
        # Count lembaga adat
        lembaga_adat_count = LembagaAdat.objects.filter(status='aktif').count()
        stats['total_organizations'] += lembaga_adat_count
        stats['active_organizations'] += lembaga_adat_count
        
        # Count PKK
        pkk_count = PenggerakPKK.objects.filter(status='aktif').count()
        stats['total_organizations'] += pkk_count
        stats['active_organizations'] += pkk_count
        stats['total_members'] += pkk_count
        
        # Count kepemudaan
        kepemudaan_count = Kepemudaan.objects.filter(status='aktif').count()
        stats['total_organizations'] += kepemudaan_count
        stats['active_organizations'] += kepemudaan_count
        stats['total_members'] += kepemudaan_count
        
        # Count karang taruna
        karang_taruna_count = KarangTaruna.objects.filter(status='aktif').count()
        stats['total_organizations'] += karang_taruna_count
        stats['active_organizations'] += karang_taruna_count
        stats['total_members'] += karang_taruna_count
        
        return JsonResponse({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


# AJAX Views for filtering
@require_http_methods(["GET"])
def ajax_perangkat_desa_filter(request):
    """AJAX endpoint for filtering perangkat desa"""
    search_query = request.GET.get('search', '')
    jabatan_filter = request.GET.get('jabatan', '')
    status_filter = request.GET.get('status', 'aktif')
    
    perangkat = VillageOfficial.objects.select_related('village').filter(
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
    
    # Pagination
    paginator = Paginator(perangkat, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Render the results
    html = render_to_string('public/organization/partials/perangkat_desa_list.html', {
        'perangkat_desa': page_obj,
        'page_obj': page_obj,
    })
    
    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': page_obj.paginator.num_pages,
    })


@require_http_methods(["GET"])
def ajax_lembaga_adat_filter(request):
    """AJAX endpoint for filtering lembaga adat"""
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
    
    # Pagination
    paginator = Paginator(lembaga, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Render the results
    html = render_to_string('public/organization/partials/lembaga_adat_list.html', {
        'lembaga_adat': page_obj,
        'page_obj': page_obj,
    })
    
    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': page_obj.paginator.num_pages,
    })


@require_http_methods(["GET"])
def ajax_pkk_filter(request):
    """AJAX endpoint for filtering PKK"""
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
    
    # Pagination
    paginator = Paginator(pkk, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Render the results
    html = render_to_string('public/organization/partials/pkk_list.html', {
        'penggerak_pkk': page_obj,
        'page_obj': page_obj,
    })
    
    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': page_obj.paginator.num_pages,
    })


@require_http_methods(["GET"])
def ajax_kepemudaan_filter(request):
    """AJAX endpoint for filtering kepemudaan"""
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
    
    # Pagination
    paginator = Paginator(kepemudaan, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Render the results
    html = render_to_string('public/organization/partials/kepemudaan_list.html', {
        'organisasi_kepemudaan': page_obj,
        'page_obj': page_obj,
    })
    
    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': page_obj.paginator.num_pages,
    })


@require_http_methods(["GET"])
def ajax_karang_taruna_filter(request):
    """AJAX endpoint for filtering karang taruna"""
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
    
    # Pagination
    paginator = Paginator(karang_taruna, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Render the results
    html = render_to_string('public/organization/partials/karang_taruna_list.html', {
        'karang_taruna': page_obj,
        'page_obj': page_obj,
    })
    
    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': page_obj.paginator.num_pages,
    })

