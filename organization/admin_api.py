from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
try:
    from core.models import CustomUser as User
except ImportError:
    from django.contrib.auth.models import User
from .models import LembagaAdat, PenggerakPKK, Kepemudaan, KarangTaruna
from village_profile.models import VillageOfficial
# Import Penduduk from letters app
try:
    from letters.models import Penduduk
except ImportError:
    try:
        from references.models import Penduduk
    except ImportError:
        Penduduk = None


# ADMIN PANEL API ENDPOINTS

def check_admin_permission(user):
    """Check if user has admin permissions"""
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required")
    
    if not (user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists()):
        raise PermissionDenied("Admin permissions required")
    
    return True

@login_required
@require_http_methods(["GET"])
def admin_api_organization_stats(request):
    """Admin API untuk statistik organisasi"""
    try:
        # Check admin permissions
        check_admin_permission(request.user)
        
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
            'total_penduduk': Penduduk.objects.filter(is_active=True, is_alive=True).count() if Penduduk else 0,
        }
        return JsonResponse({'success': True, **stats})
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def admin_api_search_penduduk(request):
    """Admin API untuk pencarian penduduk"""
    try:
        # Check admin permissions
        check_admin_permission(request.user)
        
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 50))
        age_min = request.GET.get('age_min')
        age_max = request.GET.get('age_max')
        gender = request.GET.get('gender')
        
        if not Penduduk:
            return JsonResponse({'success': True, 'results': []})
        
        penduduk_list = Penduduk.objects.filter(is_active=True, is_alive=True)
        
        if query:
            penduduk_list = penduduk_list.filter(
                Q(name__icontains=query) |
                Q(nik__icontains=query) |
                Q(address__icontains=query)
            )
        
        if age_min:
            penduduk_list = penduduk_list.filter(age__gte=int(age_min))
        if age_max:
            penduduk_list = penduduk_list.filter(age__lte=int(age_max))
        if gender:
            penduduk_list = penduduk_list.filter(gender=gender)
        
        penduduk_list = penduduk_list[:limit]
        
        results = []
        for penduduk in penduduk_list:
            results.append({
                'id': penduduk.id,
                'nik': penduduk.nik or '',
                'nama': penduduk.name or '',
                'gender': getattr(penduduk, 'gender', '') or '',
                'age': getattr(penduduk, 'age', 0) or 0,
                'alamat': getattr(penduduk, 'address', '') or '',
                'telepon': getattr(penduduk, 'phone_number', '') or getattr(penduduk, 'mobile_number', '') or '',
                'email': getattr(penduduk, 'email', '') or '',
            })
        
        return JsonResponse({'success': True, 'results': results})
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e), 'results': []}, status=500)


@login_required
@require_http_methods(["GET"])
def admin_api_village_officials(request):
    """Admin API untuk data perangkat desa"""
    try:
        # Check admin permissions
        check_admin_permission(request.user)
        
        search = request.GET.get('search', '')
        jabatan = request.GET.get('jabatan', '')
        status = request.GET.get('status', 'aktif')
        
        officials = VillageOfficial.objects.filter(is_active=True)
        
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
                'name': official.name,
                'position': official.position,
                'nik': official.nik,
                'photo': official.photo.url if official.photo else None,
                'is_active': official.is_active,
                'start_date': official.start_date.strftime('%Y-%m-%d') if official.start_date else None,
                'end_date': official.end_date.strftime('%Y-%m-%d') if official.end_date else None,
            })
        
        return JsonResponse({'success': True, 'results': results})
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e), 'results': []}, status=500)


@login_required
@require_http_methods(["GET"])
def admin_api_penggerak_pkk(request):
    """Admin API untuk data penggerak PKK"""
    try:
        # Check admin permissions
        check_admin_permission(request.user)
        
        search = request.GET.get('search', '')
        jabatan = request.GET.get('jabatan', '')
        status = request.GET.get('status', 'aktif')
        
        pkk_members = PenggerakPKK.objects.filter(status=status)
        
        if search:
            pkk_members = pkk_members.filter(
                Q(penduduk__name__icontains=search) |
                Q(jabatan__icontains=search) |
                Q(nomor_anggota__icontains=search)
            )
        
        if jabatan:
            pkk_members = pkk_members.filter(jabatan=jabatan)
        
        results = []
        for member in pkk_members:
            results.append({
                'id': member.id,
                'penduduk_name': member.penduduk.name if member.penduduk else '',
                'penduduk_nik': member.penduduk.nik if member.penduduk else '',
                'jabatan': member.jabatan,
                'nomor_anggota': member.nomor_anggota,
                'status': member.status,
                'foto_profil': member.foto_profil.url if member.foto_profil else None,
                'tanggal_bergabung': member.tanggal_bergabung.strftime('%Y-%m-%d') if member.tanggal_bergabung else None,
            })
        
        return JsonResponse({'success': True, 'results': results})
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e), 'results': []}, status=500)


@login_required
@require_http_methods(["GET"])
def admin_api_karang_taruna(request):
    """Admin API untuk data karang taruna"""
    try:
        # Check admin permissions
        check_admin_permission(request.user)
        
        search = request.GET.get('search', '')
        jabatan = request.GET.get('jabatan', '')
        status = request.GET.get('status', 'aktif')
        pengurus_inti = request.GET.get('pengurus_inti', '')
        
        kt_members = KarangTaruna.objects.filter(status=status)
        
        if search:
            kt_members = kt_members.filter(
                Q(penduduk__name__icontains=search) |
                Q(jabatan__icontains=search) |
                Q(nomor_anggota__icontains=search)
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
                'penduduk_name': member.penduduk.name if member.penduduk else '',
                'penduduk_nik': member.penduduk.nik if member.penduduk else '',
                'jabatan': member.jabatan,
                'nomor_anggota': member.nomor_anggota,
                'status': member.status,
                'is_pengurus_inti': member.is_pengurus_inti,
                'foto_profil': member.foto_profil.url if member.foto_profil else None,
                'tanggal_bergabung': member.tanggal_bergabung.strftime('%Y-%m-%d') if member.tanggal_bergabung else None,
                'bidang_keahlian': member.bidang_keahlian,
                'pengalaman_organisasi': member.pengalaman_organisasi,
            })
        
        return JsonResponse({'success': True, 'results': results})
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e), 'results': []}, status=500)


@login_required
@require_http_methods(["GET"])
def admin_api_kepemudaan(request):
    """Admin API untuk data kepemudaan"""
    try:
        # Check admin permissions
        check_admin_permission(request.user)
        
        search = request.GET.get('search', '')
        status = request.GET.get('status', 'aktif')
        
        kepemudaan_list = Kepemudaan.objects.filter(status=status)
        
        if search:
            kepemudaan_list = kepemudaan_list.filter(
                Q(nama_organisasi__icontains=search) |
                Q(ketua__icontains=search) |
                Q(sekretaris__icontains=search)
            )
        
        results = []
        for kepemudaan in kepemudaan_list:
            results.append({
                'id': kepemudaan.id,
                'nama_organisasi': str(kepemudaan.nama_organisasi) if kepemudaan.nama_organisasi else '',
                'jenis_organisasi': str(kepemudaan.jenis_organisasi) if kepemudaan.jenis_organisasi else '',
                'ketua': str(kepemudaan.ketua) if kepemudaan.ketua else '',
                'sekretaris': str(kepemudaan.sekretaris) if kepemudaan.sekretaris else '',
                'bendahara': str(kepemudaan.bendahara) if kepemudaan.bendahara else '',
                'status': str(kepemudaan.status) if kepemudaan.status else '',
                'tanggal_terbentuk': kepemudaan.tanggal_terbentuk.strftime('%Y-%m-%d') if kepemudaan.tanggal_terbentuk else None,
            })
        
        return JsonResponse({'success': True, 'results': results})
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e), 'results': []}, status=500)


@login_required
@require_http_methods(["GET"])
def admin_api_lembaga_adat(request):
    """Admin API untuk data lembaga adat"""
    try:
        # Check admin permissions
        check_admin_permission(request.user)
        
        search = request.GET.get('search', '')
        status = request.GET.get('status', 'aktif')
        
        lembaga_list = LembagaAdat.objects.filter(status=status)
        
        if search:
            lembaga_list = lembaga_list.filter(
                Q(nama_lembaga__icontains=search) |
                Q(ketua__icontains=search) |
                Q(sekretaris__icontains=search)
            )
        
        results = []
        for lembaga in lembaga_list:
            results.append({
                'id': lembaga.id,
                'nama_lembaga': str(lembaga.nama_lembaga) if lembaga.nama_lembaga else '',
                'jenis_lembaga': str(lembaga.jenis_lembaga) if lembaga.jenis_lembaga else '',
                'ketua': str(lembaga.ketua) if lembaga.ketua else '',
                'sekretaris': str(lembaga.sekretaris) if lembaga.sekretaris else '',
                'bendahara': str(lembaga.bendahara) if lembaga.bendahara else '',
                'status': str(lembaga.status) if lembaga.status else '',
                'tanggal_terbentuk': lembaga.tanggal_terbentuk.strftime('%Y-%m-%d') if lembaga.tanggal_terbentuk else None,
            })
        
        return JsonResponse({'success': True, 'results': results})
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e), 'results': []}, status=500)


@login_required
@require_http_methods(["GET"])
def admin_api_organization_structure(request):
    """Admin API untuk struktur organisasi"""
    try:
        # Check admin permissions
        check_admin_permission(request.user)
        
        structure = {
            'perangkat_desa': [],
            'penggerak_pkk': [],
            'karang_taruna': [],
            'kepemudaan': [],
            'lembaga_adat': []
        }
        
        # Perangkat Desa
        officials = VillageOfficial.objects.filter(is_active=True)
        for official in officials:
            structure['perangkat_desa'].append({
                'id': official.id,
                'name': official.name,
                'position': official.position,
                'photo': official.photo.url if official.photo else None
            })
        
        # Penggerak PKK
        pkk_members = PenggerakPKK.objects.filter(status='aktif')
        for member in pkk_members:
            structure['penggerak_pkk'].append({
                'id': member.id,
                'name': member.penduduk.name if member.penduduk else '',
                'jabatan': member.jabatan,
                'photo': member.foto_profil.url if member.foto_profil else None
            })
        
        # Karang Taruna
        kt_members = KarangTaruna.objects.filter(status='aktif')
        for member in kt_members:
            structure['karang_taruna'].append({
                'id': member.id,
                'name': member.penduduk.name if member.penduduk else '',
                'jabatan': member.jabatan,
                'photo': member.foto_profil.url if member.foto_profil else None
            })
        
        # Kepemudaan
        kepemudaan_list = Kepemudaan.objects.filter(status='aktif')
        for kepemudaan in kepemudaan_list:
            structure['kepemudaan'].append({
                'id': kepemudaan.id,
                'name': kepemudaan.nama_organisasi,
                'ketua': kepemudaan.ketua.name if kepemudaan.ketua else None,
                'sekretaris': kepemudaan.sekretaris.name if kepemudaan.sekretaris else None
            })
        
        # Lembaga Adat
        lembaga_list = LembagaAdat.objects.filter(status='aktif')
        for lembaga in lembaga_list:
            structure['lembaga_adat'].append({
                'id': lembaga.id,
                'name': lembaga.nama_lembaga,
                'ketua': lembaga.ketua.name if lembaga.ketua else None,
                'sekretaris': lembaga.sekretaris.name if lembaga.sekretaris else None
            })
        
        return JsonResponse({
            'success': True,
            'structure': structure
        })
    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)