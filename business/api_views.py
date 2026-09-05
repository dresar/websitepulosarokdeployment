from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    Business, BusinessCategory, BusinessOwner, BusinessProduct, 
    BusinessFinance, UKM, Koperasi, BUMG, Aset, LayananJasa, BusinessPageHeader,
    JenisKoperasi
)

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

# API Views for Admin Panel
@login_required
@user_passes_test(is_admin)
def api_business_statistics(request):
    """API untuk statistik bisnis admin"""
    try:
        stats = {
            'total_businesses': Business.objects.filter(status='approved').count(),
            'total_umkm': UKM.objects.filter(status='aktif').count(),
            'total_koperasi': Koperasi.objects.filter(status='aktif').count(),
            'total_bumg': BUMG.objects.filter(status='aktif').count(),
            'total_layanan': LayananJasa.objects.filter(status='aktif').count(),
            'pending_approvals': Business.objects.filter(status='pending').count(),
            'total_categories': BusinessCategory.objects.count(),
        }
        
        # Monthly statistics
        now = timezone.now()
        stats['monthly_registrations'] = UKM.objects.filter(
            created_at__month=now.month, 
            created_at__year=now.year
        ).count()
        
        stats['monthly_approvals'] = UKM.objects.filter(
            status='aktif', 
            updated_at__month=now.month, 
            updated_at__year=now.year
        ).count()
        
        stats['recent_registrations'] = UKM.objects.filter(
            created_at__gte=now - timedelta(days=7)
        ).count()
        
        return JsonResponse({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def api_penduduk_search(request):
    """API untuk pencarian penduduk di admin panel"""
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Anda tidak memiliki izin untuk mengakses sumber daya ini.'}, status=403)
    try:
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 10))
        
        if len(query) < 2:
            return JsonResponse({
                'success': True, 
                'results': [],
                'message': 'Query terlalu pendek'
            })
        
        if Penduduk:
            penduduk_list = Penduduk.objects.filter(
                Q(name__icontains=query) | Q(nik__icontains=query)
            )[:limit]
            
            results = []
            for penduduk in penduduk_list:
                results.append({
                    'id': penduduk.id,
                    'name': penduduk.name,
                    'nik': penduduk.nik,
                    'address': getattr(penduduk, 'address', '') or f"{penduduk.dusun.name if penduduk.dusun else ''}",
                    'tempat_lahir': penduduk.birth_place,
                    'tanggal_lahir': penduduk.birth_date.isoformat() if penduduk.birth_date else '',
                    'jenis_kelamin': penduduk.get_gender_display(),
                    'agama': penduduk.get_religion_display(),
                    'status_perkawinan': penduduk.get_marital_status_display(),
                    'pekerjaan': penduduk.occupation or '',
                    'pendidikan': penduduk.get_education_display() if penduduk.education else '',
                    'status_kependudukan': 'Aktif' if penduduk.is_active else 'Tidak Aktif',
                    'dusun': penduduk.dusun.name if penduduk.dusun else '',
                    'rt': penduduk.rt.rt_number if penduduk.rt else '',
                    'rw': penduduk.rw.rw_number if penduduk.rw else '',
                    'kelurahan': 'Pulosari',
                    'kecamatan': 'Pulosari',
                    'kabupaten': 'Bondowoso',
                    'provinsi': 'Jawa Timur',
                    'kode_pos': '68288',
                    'phone_number': penduduk.phone_number or penduduk.mobile_number or '',
                    'email': penduduk.email or '',
                })
            
            return JsonResponse({
                'success': True,
                'results': results
            })
        else:
            return JsonResponse({
                'success': True,
                'results': [],
                'message': 'Model Penduduk tidak tersedia'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

# Public API for penduduk search (no login required)
def api_penduduk_search_public(request):
    """API untuk pencarian penduduk publik"""
    try:
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 10))
        
        if len(query) < 2:
            return JsonResponse({
                'success': True, 
                'results': [],
                'message': 'Query terlalu pendek'
            })
        
        if Penduduk:
            penduduk_list = Penduduk.objects.filter(
                Q(name__icontains=query) | Q(nik__icontains=query)
            )[:limit]
            
            results = []
            for penduduk in penduduk_list:
                results.append({
                    'id': penduduk.id,
                    'nama': penduduk.name,
                    'nik': penduduk.nik,
                    'alamat': penduduk.address if hasattr(penduduk, 'address') else '',
                })
            
            return JsonResponse({
                'success': True,
                'results': results
            })
        else:
            return JsonResponse({
                'success': True,
                'results': [],
                'message': 'Model Penduduk tidak tersedia'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin)
def api_umkm_list(request):
    """API untuk daftar UMKM admin"""
    try:
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        umkm_list = UKM.objects.all().order_by('-created_at')
        
        if search:
            umkm_list = umkm_list.filter(
                Q(nama_usaha__icontains=search) |
                Q(pemilik__icontains=search) |
                Q(jenis_usaha__icontains=search)
            )
        
        paginator = Paginator(umkm_list, per_page)
        page_obj = paginator.get_page(page)
        
        results = []
        for umkm in page_obj:
            results.append({
                'id': umkm.id,
                'nama_usaha': umkm.nama_usaha,
                'pemilik': umkm.pemilik,
                'nik_pemilik': umkm.nik_pemilik,
                'jenis_usaha': umkm.jenis_usaha,
                'skala_usaha': umkm.skala_usaha,
                'skala_usaha_display': umkm.get_skala_usaha_display(),
                'tanggal_mulai': umkm.tanggal_mulai.isoformat() if umkm.tanggal_mulai else None,
                'nomor_izin': umkm.nomor_izin,
                'alamat_usaha': umkm.alamat_usaha,
                'alamat_pemilik': umkm.alamat_pemilik,
                'telepon': umkm.telepon,
                'email': umkm.email,
                'modal_awal': float(umkm.modal_awal),
                'omzet_bulanan': float(umkm.omzet_bulanan),
                'jumlah_karyawan': umkm.jumlah_karyawan,
                'produk_utama': umkm.produk_utama,
                'target_pasar': umkm.target_pasar,
                'status': umkm.status,
                'status_display': umkm.get_status_display(),
                'keterangan': umkm.keterangan,
                'created_at': umkm.created_at.isoformat(),
                'updated_at': umkm.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'umkm': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin)
def api_koperasi_list(request):
    """API untuk daftar Koperasi admin"""
    try:
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        koperasi_list = Koperasi.objects.all().order_by('-created_at')
        
        if search:
            koperasi_list = koperasi_list.filter(
                Q(nama_koperasi__icontains=search) |
                Q(ketua__icontains=search) |
                Q(sekretaris__icontains=search)
            )
        
        paginator = Paginator(koperasi_list, per_page)
        page_obj = paginator.get_page(page)
        
        results = []
        for koperasi in page_obj:
            results.append({
                'id': koperasi.id,
                'nama_koperasi': koperasi.nama_koperasi,
                'ketua': koperasi.ketua,
                'sekretaris': koperasi.sekretaris,
                'bendahara': koperasi.bendahara,
                'alamat': koperasi.alamat,
                'telepon': koperasi.telepon,
                'email': koperasi.email,
                'tanggal_berdiri': koperasi.tanggal_berdiri.isoformat() if koperasi.tanggal_berdiri else None,
                'nomor_badan_hukum': koperasi.nomor_badan_hukum,
                'jenis_koperasi': koperasi.jenis_koperasi,
                'bidang_usaha': koperasi.bidang_usaha,
                'jumlah_anggota': koperasi.jumlah_anggota,
                'modal_dasar': float(koperasi.modal_dasar),
                'modal_disetor': float(koperasi.modal_disetor),
                'status': koperasi.status,
                'status_display': koperasi.get_status_display(),
                'keterangan': koperasi.keterangan,
                'created_at': koperasi.created_at.isoformat(),
                'updated_at': koperasi.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'koperasi': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin)
def api_bumg_list(request):
    """API untuk daftar BUMG admin"""
    try:
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        bumg_list = BUMG.objects.all().order_by('-created_at')
        
        if search:
            bumg_list = bumg_list.filter(
                Q(nama__icontains=search) |
                Q(direktur__icontains=search) |
                Q(bidang_usaha__icontains=search)
            )
        
        paginator = Paginator(bumg_list, per_page)
        page_obj = paginator.get_page(page)
        
        results = []
        for bumg in page_obj:
            results.append({
                'id': bumg.id,
                'nama': bumg.nama,
                'direktur': bumg.direktur,
                'alamat': bumg.alamat,
                'telepon': bumg.telepon,
                'email': bumg.email,
                'tanggal_berdiri': bumg.tanggal_berdiri.isoformat() if bumg.tanggal_berdiri else None,
                'nomor_akta': bumg.nomor_akta,
                'bidang_usaha': bumg.bidang_usaha,
                'modal_dasar': float(bumg.modal_dasar),
                'modal_disetor': float(bumg.modal_disetor),
                'jumlah_karyawan': bumg.jumlah_karyawan,
                'status': bumg.status,
                'status_display': bumg.get_status_display(),
                'keterangan': bumg.keterangan,
                'created_at': bumg.created_at.isoformat(),
                'updated_at': bumg.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'bumg': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin)
def api_layanan_jasa_list(request):
    """API untuk daftar Layanan Jasa admin"""
    try:
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        layanan_list = LayananJasa.objects.all().order_by('-created_at')
        
        if search:
            layanan_list = layanan_list.filter(
                Q(nama_layanan__icontains=search) |
                Q(penyedia__icontains=search) |
                Q(jenis_layanan__icontains=search)
            )
        
        paginator = Paginator(layanan_list, per_page)
        page_obj = paginator.get_page(page)
        
        results = []
        for layanan in page_obj:
            results.append({
                'id': layanan.id,
                'nama_layanan': layanan.nama_layanan,
                'penyedia': layanan.penyedia,
                'alamat': layanan.alamat,
                'telepon': layanan.telepon,
                'email': layanan.email,
                'jenis_layanan': layanan.jenis_layanan,
                'deskripsi_layanan': layanan.deskripsi_layanan,
                'tarif_layanan': float(layanan.tarif_layanan),
                'jam_operasional': layanan.jam_operasional,
                'status': layanan.status,
                'status_display': layanan.get_status_display(),
                'keterangan': layanan.keterangan,
                'created_at': layanan.created_at.isoformat(),
                'updated_at': layanan.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'layanan': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin)
def api_business_categories_list(request):
    """API untuk daftar kategori bisnis admin"""
    try:
        categories = BusinessCategory.objects.all().order_by('name')
        
        results = []
        for category in categories:
            results.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'is_active': category.is_active,
                'created_at': category.created_at.isoformat(),
                'updated_at': category.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'categories': results
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin)
@csrf_exempt
@require_http_methods(["POST"])
def api_umkm_create(request):
    """API untuk membuat UMKM baru"""
    try:
        data = json.loads(request.body)
        
        ukm = UKM.objects.create(
            nama_usaha=data.get('nama_usaha'),
            pemilik=data.get('pemilik'),
            nik_pemilik=data.get('nik_pemilik'),
            jenis_usaha=data.get('jenis_usaha'),
            skala_usaha=data.get('skala_usaha'),
            tanggal_mulai=data.get('tanggal_mulai'),
            nomor_izin=data.get('nomor_izin'),
            alamat_usaha=data.get('alamat_usaha'),
            alamat_pemilik=data.get('alamat_pemilik'),
            telepon=data.get('telepon'),
            email=data.get('email'),
            modal_awal=data.get('modal_awal', 0),
            omzet_bulanan=data.get('omzet_bulanan', 0),
            jumlah_karyawan=data.get('jumlah_karyawan', 0),
            produk_utama=data.get('produk_utama'),
            target_pasar=data.get('target_pasar'),
            status=data.get('status', 'pending'),
            keterangan=data.get('keterangan')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'UMKM berhasil dibuat',
            'umkm_id': ukm.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin)
@csrf_exempt
@require_http_methods(["POST"])
def api_umkm_update(request, umkm_id):
    """API untuk update UMKM"""
    try:
        ukm = get_object_or_404(UKM, id=umkm_id)
        data = json.loads(request.body)
        
        ukm.nama_usaha = data.get('nama_usaha', ukm.nama_usaha)
        ukm.pemilik = data.get('pemilik', ukm.pemilik)
        ukm.nik_pemilik = data.get('nik_pemilik', ukm.nik_pemilik)
        ukm.jenis_usaha = data.get('jenis_usaha', ukm.jenis_usaha)
        ukm.skala_usaha = data.get('skala_usaha', ukm.skala_usaha)
        ukm.tanggal_mulai = data.get('tanggal_mulai', ukm.tanggal_mulai)
        ukm.nomor_izin = data.get('nomor_izin', ukm.nomor_izin)
        ukm.alamat_usaha = data.get('alamat_usaha', ukm.alamat_usaha)
        ukm.alamat_pemilik = data.get('alamat_pemilik', ukm.alamat_pemilik)
        ukm.telepon = data.get('telepon', ukm.telepon)
        ukm.email = data.get('email', ukm.email)
        ukm.modal_awal = data.get('modal_awal', ukm.modal_awal)
        ukm.omzet_bulanan = data.get('omzet_bulanan', ukm.omzet_bulanan)
        ukm.jumlah_karyawan = data.get('jumlah_karyawan', ukm.jumlah_karyawan)
        ukm.produk_utama = data.get('produk_utama', ukm.produk_utama)
        ukm.target_pasar = data.get('target_pasar', ukm.target_pasar)
        ukm.status = data.get('status', ukm.status)
        ukm.keterangan = data.get('keterangan', ukm.keterangan)
        
        ukm.save()
        
        return JsonResponse({
            'success': True,
            'message': 'UMKM berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin)
@csrf_exempt
@require_http_methods(["DELETE"])
def api_umkm_delete(request, umkm_id):
    """API untuk hapus UMKM"""
    try:
        ukm = get_object_or_404(UKM, id=umkm_id)
        ukm.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'UMKM berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@user_passes_test(is_admin)
def api_recent_activities(request):
    """API untuk aktivitas terbaru"""
    try:
        # Recent UMKM
        recent_ukm = UKM.objects.filter(status='aktif').order_by('-created_at')[:5]
        
        results = []
        for ukm in recent_ukm:
            results.append({
                'id': ukm.id,
                'type': 'umkm',
                'name': ukm.nama_usaha,
                'owner': ukm.pemilik,
                'business_type': ukm.jenis_usaha,
                'scale': ukm.skala_usaha,
                'created_at': ukm.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'activities': results
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
