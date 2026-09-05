"""
Admin Panel Views - Centralized admin interface
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

# Import models from all applications safely
try:
    from beneficiaries.models import Beneficiary
except:
    Beneficiary = None

# try:
#     from business.models import UKM
# except:
UKM = None

try:
    from complaints.models import Complaint
except:
    Complaint = None

try:
    from documents.models import Document
except:
    Document = None

try:
    from news.models import News
except:
    News = None

try:
    from posyandu.models import PosyanduLocation
except:
    PosyanduLocation = None

from core.models import CustomUser, UserProfile, Role, MenuPermission, UserRole, LoginHistory, WebsiteSettings, HeroImage

# Try to import references models safely
try:
    from references.models import Penduduk, Dusun, Lorong, Family, Keluarga
except:
    Penduduk = None
    Dusun = None
    Lorong = None
    Family = None
    Keluarga = None

# Try to import business models safely
# try:
#     from business.models import UKM, Koperasi, BUMG, LayananJasa, BusinessCategory
# except:
UKM = None
Koperasi = None
BUMG = None
LayananJasa = None
BusinessCategory = None

# Try to import posyandu models safely
try:
    from posyandu.models import PosyanduLocation, PosyanduActivity
except:
    PosyanduLocation = None
    PosyanduActivity = None

# Try to import news models safely
try:
    from news.models import News, Announcement, NewsCategory, NewsComment
except:
    News = None
    Announcement = None
    NewsCategory = None
    NewsComment = None

def is_admin_user(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists())

@login_required
def admin_dashboard(request):
    """Main admin dashboard"""
    if not is_admin_user(request.user):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('core:home')
    
    try:
        # Get comprehensive statistics
        total_penduduk = Penduduk.objects.count() if Penduduk else 0
        total_keluarga = Keluarga.objects.count() if Keluarga else 0
        total_dusun = Dusun.objects.count() if Dusun else 0
        total_lorong = Lorong.objects.count() if Lorong else 0
        
        # Business statistics
        total_ukm = UKM.objects.count() if UKM else 0
        total_koperasi = Koperasi.objects.count() if Koperasi else 0
        total_bumg = BUMG.objects.count() if BUMG else 0
        total_layanan_jasa = LayananJasa.objects.count() if LayananJasa else 0
        total_businesses = total_ukm + total_koperasi + total_bumg + total_layanan_jasa
        
        # Other statistics
        total_beneficiaries = Beneficiary.objects.count() if Beneficiary else 0
        total_complaints = Complaint.objects.count() if Complaint else 0
        total_documents = Document.objects.count() if Document else 0
        total_news = News.objects.count() if News else 0
        total_posyandu_locations = PosyanduLocation.objects.count() if PosyanduLocation else 0
        
        # Try to get RT/RW data
        total_rt = 0
        total_rw = 0
        total_pelajar = 0
        total_disabilitas = 0
        try:
            from references.models import RT, RW, Pelajar, DisabilitasData
            total_rt = RT.objects.count() if RT else 0
            total_rw = RW.objects.count() if RW else 0
            total_pelajar = Pelajar.objects.count() if Pelajar else 0
            total_disabilitas = DisabilitasData.objects.count() if DisabilitasData else 0
        except:
            pass
        
        # Try to get tourism data
        total_tourism_locations = 0
        try:
            from tourism.models import TourismLocation
            total_tourism_locations = TourismLocation.objects.count()
        except:
            pass
        
        # Get user role information
        role_name = "Admin"
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role:
            role_name = request.user.userprofile.role.name
        
        # Get recent data
        recent_beneficiaries = Beneficiary.objects.all()[:5] if Beneficiary else []
        
        context = {
            'title': 'Dashboard Admin',
            'active_menu': 'dashboard',
            'role_name': role_name,
            
            # Main statistics
            'total_penduduk': total_penduduk,
            'total_keluarga': total_keluarga,
            'total_businesses': total_businesses,
            'total_beneficiaries': total_beneficiaries,
            'total_complaints': total_complaints,
            'total_documents': total_documents,
            'total_news': total_news,
            'total_posyandu_locations': total_posyandu_locations,
            'total_tourism_locations': total_tourism_locations,
            
            # Additional statistics
            'total_dusun': total_dusun,
            'total_lorong': total_lorong,
            'total_rt': total_rt,
            'total_rw': total_rw,
            'total_pelajar': total_pelajar,
            'total_disabilitas': total_disabilitas,
            
            # Business breakdown
            'total_ukm': total_ukm,
            'total_koperasi': total_koperasi,
            'total_bumg': total_bumg,
            'total_layanan_jasa': total_layanan_jasa,
            
            'recent_beneficiaries': recent_beneficiaries,
        }
        
        return render(request, 'admin_panel/dashboard.html', context)
        
    except Exception as e:
        # Fallback context if there are any errors
        context = {
            'title': 'Dashboard Admin',
            'active_menu': 'dashboard',
            'role_name': 'Admin',
            'total_penduduk': 0,
            'total_keluarga': 0,
            'total_businesses': 0,
            'total_beneficiaries': 0,
            'total_complaints': 0,
            'total_documents': 0,
            'total_news': 0,
            'total_posyandu_locations': 0,
            'total_tourism_locations': 0,
            'total_dusun': 0,
            'total_lorong': 0,
            'total_rt': 0,
            'total_rw': 0,
            'total_pelajar': 0,
            'total_disabilitas': 0,
            'recent_beneficiaries': [],
        }
        
        return render(request, 'admin_panel/dashboard.html', context)

def custom_login(request):
    """Custom login view for admin panel"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active and (user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists()):
                login(request, user)
                return redirect('admin_panel:dashboard')
            else:
                messages.error(request, 'Anda tidak memiliki akses ke admin panel.')
        else:
            messages.error(request, 'Username atau password salah.')
    
    return render(request, 'admin_panel/login.html')

# Dashboard functions that redirect to respective app admin views
def references_dashboard(request):
    """References admin dashboard"""
    return render(request, 'admin_panel/references/dashboard.html', {
        'title': 'Dashboard Referensi',
        'active_menu': 'references',
        'active_submenu': 'references_dashboard',
    })

def references_penduduk_list(request):
    """References penduduk list view"""
    from references.views import admin_panel_penduduk_list
    return admin_panel_penduduk_list(request)

def references_penduduk_add(request):
    """References penduduk add view"""
    from references.views import penduduk_add
    return penduduk_add(request)

def references_penduduk_edit(request, penduduk_id):
    """References penduduk edit view"""
    from references.views import penduduk_edit
    return penduduk_edit(request, penduduk_id)

def references_penduduk_delete(request, penduduk_id):
    """References penduduk delete view"""
    from references.views import penduduk_delete
    return penduduk_delete(request, penduduk_id)

def references_penduduk_detail(request, penduduk_id):
    """References penduduk detail view"""
    from references.views import penduduk_detail
    return penduduk_detail(request, penduduk_id)

def references_penduduk_export_excel(request):
    """References penduduk export excel view"""
    from django.http import HttpResponse
    return HttpResponse("Excel export not implemented yet", content_type='text/plain')

def references_penduduk_export_csv(request):
    """References penduduk export csv view"""
    from django.http import HttpResponse
    return HttpResponse("CSV export not implemented yet", content_type='text/plain')

def references_penduduk_export_json(request):
    """References penduduk export json view"""
    from django.http import JsonResponse
    return JsonResponse({"message": "JSON export not implemented yet"})

def references_penduduk_export_pdf(request):
    """References penduduk export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("PDF export not implemented yet", content_type='text/plain')

def references_bulk_action(request):
    """References bulk action view"""
    from references.views import penduduk_bulk_delete
    return penduduk_bulk_delete(request)

def references_penduduk_bulk_delete(request):
    """References penduduk bulk delete view"""
    from references.views import penduduk_bulk_delete
    return penduduk_bulk_delete(request)

def references_penduduk_bulk_activate(request):
    """References penduduk bulk activate view"""
    from references.views import penduduk_bulk_activate
    return penduduk_bulk_activate(request)

def references_penduduk_bulk_deactivate(request):
    """References penduduk bulk deactivate view"""
    from references.views import penduduk_bulk_deactivate
    return penduduk_bulk_deactivate(request)

def references_quick_import(request, model_name):
    """References quick import view"""
    from django.http import HttpResponse
    return HttpResponse(f"Quick import for {model_name} not implemented yet", content_type='text/plain')

def references_penduduk_save(request):
    """References penduduk save view"""
    from django.shortcuts import redirect, get_object_or_404
    from django.contrib import messages
    from references.models import Penduduk, Dusun
    from django.http import JsonResponse
    
    if request.method == 'POST':
        try:
            # Get form data
            penduduk_id = request.POST.get('penduduk_id')
            nik = request.POST.get('nik')
            name = request.POST.get('nama_lengkap')
            birth_place = request.POST.get('tempat_lahir')
            birth_date = request.POST.get('tanggal_lahir')
            gender = request.POST.get('jenis_kelamin')
            religion = request.POST.get('agama')
            marital_status = request.POST.get('status_perkawinan')
            occupation = request.POST.get('pekerjaan')
            education = request.POST.get('education')
            address = request.POST.get('alamat')
            dusun_id = request.POST.get('dusun')
            lorong_id = request.POST.get('lorong')
            rw_id = request.POST.get('rw')
            rt_id = request.POST.get('rt')
            rt_number = request.POST.get('rt_number')
            rw_number = request.POST.get('rw_number')
            house_number = request.POST.get('house_number')
            postal_code = request.POST.get('postal_code')
            phone_number = request.POST.get('phone_number')
            mobile_number = request.POST.get('mobile_number')
            email = request.POST.get('email')
            blood_type = request.POST.get('blood_type')
            kk_number = request.POST.get('kk_number')
            relationship_to_head = request.POST.get('relationship_to_head')
            is_active = request.POST.get('is_active') == 'on'
            
            # Get dusun object
            dusun = get_object_or_404(Dusun, id=dusun_id)
            
            if penduduk_id:
                # Update existing penduduk
                penduduk = get_object_or_404(Penduduk, id=penduduk_id)
                penduduk.nik = nik
                penduduk.name = name
                penduduk.birth_place = birth_place
                penduduk.birth_date = birth_date
                penduduk.gender = gender
                penduduk.religion = religion
                penduduk.marital_status = marital_status
                penduduk.occupation = occupation
                penduduk.education = education
                penduduk.address = address
                penduduk.dusun = dusun
                penduduk.rt_number = rt_number
                penduduk.rw_number = rw_number
                penduduk.house_number = house_number
                penduduk.postal_code = postal_code
                penduduk.phone_number = phone_number
                penduduk.mobile_number = mobile_number
                penduduk.email = email
                penduduk.blood_type = blood_type
                penduduk.kk_number = kk_number
                penduduk.relationship_to_head = relationship_to_head
                penduduk.is_active = is_active
                penduduk.save()
                
                messages.success(request, f'Data penduduk {name} berhasil diperbarui.')
                return redirect('admin_panel:references_penduduk_detail', penduduk_id=penduduk.id)
            else:
                # Create new penduduk
                penduduk = Penduduk.objects.create(
                    nik=nik,
                    name=name,
                    birth_place=birth_place,
                    birth_date=birth_date,
                    gender=gender,
                    religion=religion,
                    marital_status=marital_status,
                    occupation=occupation,
                    education=education,
                    address=address,
                    dusun=dusun,
                    rt_number=rt_number,
                    rw_number=rw_number,
                    house_number=house_number,
                    postal_code=postal_code,
                    phone_number=phone_number,
                    mobile_number=mobile_number,
                    email=email,
                    blood_type=blood_type,
                    kk_number=kk_number,
                    relationship_to_head=relationship_to_head,
                    is_active=is_active,
                    created_by=request.user
                )
                
                messages.success(request, f'Data penduduk {name} berhasil ditambahkan.')
                return redirect('admin_panel:references_penduduk_detail', penduduk_id=penduduk.id)
                
        except Exception as e:
            messages.error(request, f'Gagal menyimpan data penduduk: {str(e)}')
            return redirect('admin_panel:references_penduduk_list')
    
    return redirect('admin_panel:references_penduduk_list')

def references_pelajar_add(request):
    """References pelajar add view"""
    from references.views import pelajar_add
    return pelajar_add(request)

def references_pelajar_update(request, pelajar_id):
    """References pelajar update view"""
    from references.views import pelajar_edit
    return pelajar_edit(request, pelajar_id)

def references_pelajar_export_excel(request):
    """References pelajar export excel view"""
    from django.http import HttpResponse
    return HttpResponse("Pelajar Excel export not implemented yet", content_type='text/plain')

def references_pelajar_export_csv(request):
    """References pelajar export csv view"""
    from django.http import HttpResponse
    return HttpResponse("Pelajar CSV export not implemented yet", content_type='text/plain')

def references_pelajar_export_json(request):
    """References pelajar export json view"""
    from django.http import HttpResponse
    return HttpResponse("Pelajar JSON export not implemented yet", content_type='text/plain')

def references_pelajar_export_pdf(request):
    """References pelajar export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("Pelajar PDF export not implemented yet", content_type='text/plain')

def api_references_dusun_list(request):
    """API references dusun list view"""
    from django.http import JsonResponse
    try:
        from references.models import Dusun
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Get all dusun
        dusun_list = []
        if Dusun:
            dusuns = Dusun.objects.all()
            total_count = dusuns.count()
            
            # Paginate
            start = (page - 1) * per_page
            end = start + per_page
            dusuns = dusuns[start:end]
            
            for dusun in dusuns:
                dusun_data = {
                    'id': dusun.id,
                    'nama': getattr(dusun, 'nama', str(dusun)),
                    'nama_dusun': getattr(dusun, 'nama', str(dusun)),  # For JavaScript compatibility
                    'kode': getattr(dusun, 'kode', ''),
                    'status': getattr(dusun, 'status', 'active'),
                    'description': getattr(dusun, 'description', ''),
                    'rt': getattr(dusun, 'rt', '-'),
                    'house_count': getattr(dusun, 'house_count', 0),
                    'population_count': getattr(dusun, 'population_count', 0),
                    'is_active': getattr(dusun, 'is_active', True),
                    'created_at': dusun.created_at.isoformat() if hasattr(dusun, 'created_at') else '',
                    'updated_at': dusun.updated_at.isoformat() if hasattr(dusun, 'updated_at') else '',
                }
                
                dusun_list.append(dusun_data)
            
            return JsonResponse({
                'success': True,
                'data': dusun_list,
                'dusun_list': dusun_list,  # Keep for backward compatibility
                'statistics': {
                    'total': total_count,
                    'active': total_count,  # Assuming all are active for now
                    'inactive': 0
                },
                'pagination': {
                    'current_page': page,
                    'total_pages': (total_count + per_page - 1) // per_page,
                    'per_page': per_page,
                    'total': total_count,
                    'has_previous': page > 1,
                    'has_next': page < (total_count + per_page - 1) // per_page,
                    'previous_page': page - 1 if page > 1 else None,
                    'next_page': page + 1 if page < (total_count + per_page - 1) // per_page else None
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'data': [],
                'dusun_list': [],
                'statistics': {
                    'total': 0,
                    'active': 0,
                    'inactive': 0
                },
                'pagination': {
                    'current_page': page,
                    'total_pages': 0,
                    'per_page': per_page,
                    'total': 0,
                    'has_previous': False,
                    'has_next': False,
                    'previous_page': None,
                    'next_page': None
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': [],
            'dusun_list': [],
            'statistics': {
                'total': 0,
                'active': 0,
                'inactive': 0
            },
            'pagination': {
                'current_page': 1,
                'total_pages': 0,
                'per_page': 10,
                'total': 0,
                'has_previous': False,
                'has_next': False,
                'previous_page': None,
                'next_page': None
            }
        })

def api_references_lorong_list(request):
    """API references lorong list view"""
    from django.http import JsonResponse
    try:
        from references.models import Lorong
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Get all lorong
        lorong_list = []
        if Lorong:
            lorongs = Lorong.objects.all()
            total_count = lorongs.count()
            
            # Paginate
            start = (page - 1) * per_page
            end = start + per_page
            lorongs = lorongs[start:end]
            
            for lorong in lorongs:
                lorong_data = {
                    'id': lorong.id,
                    'nama': getattr(lorong, 'nama', str(lorong)),
                    'nama_lorong': getattr(lorong, 'nama', str(lorong)),  # For JavaScript compatibility
                    'kode': getattr(lorong, 'kode', ''),
                    'dusun': '',
                    'dusun_name': '',  # For JavaScript compatibility
                    'dusun_id': None,
                    'status': getattr(lorong, 'status', 'active'),
                    'description': getattr(lorong, 'description', ''),
                    'rt': getattr(lorong, 'rt', '-'),
                    'house_count': getattr(lorong, 'house_count', 0),
                    'population_count': getattr(lorong, 'population_count', 0),
                    'is_active': getattr(lorong, 'is_active', True),
                    'created_at': lorong.created_at.isoformat() if hasattr(lorong, 'created_at') else '',
                    'updated_at': lorong.updated_at.isoformat() if hasattr(lorong, 'updated_at') else '',
                }
                
                # Add dusun information if available
                if hasattr(lorong, 'dusun') and lorong.dusun:
                    dusun_name = getattr(lorong.dusun, 'nama', str(lorong.dusun))
                    lorong_data['dusun'] = dusun_name
                    lorong_data['dusun_name'] = dusun_name  # For JavaScript compatibility
                    lorong_data['dusun_id'] = lorong.dusun.id
                
                lorong_list.append(lorong_data)
            
            return JsonResponse({
                'success': True,
                'data': lorong_list,
                'lorong_list': lorong_list,  # Keep for backward compatibility
                'statistics': {
                    'total': total_count,
                    'active': total_count,  # Assuming all are active for now
                    'inactive': 0
                },
                'pagination': {
                    'current_page': page,
                    'total_pages': (total_count + per_page - 1) // per_page,
                    'per_page': per_page,
                    'total': total_count,
                    'has_previous': page > 1,
                    'has_next': page < (total_count + per_page - 1) // per_page,
                    'previous_page': page - 1 if page > 1 else None,
                    'next_page': page + 1 if page < (total_count + per_page - 1) // per_page else None
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'data': [],
                'lorong_list': [],
                'statistics': {
                    'total': 0,
                    'active': 0,
                    'inactive': 0
                },
                'pagination': {
                    'current_page': page,
                    'total_pages': 0,
                    'per_page': per_page,
                    'total': 0,
                    'has_previous': False,
                    'has_next': False,
                    'previous_page': None,
                    'next_page': None
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': [],
            'lorong_list': [],
            'statistics': {
                'total': 0,
                'active': 0,
                'inactive': 0
            },
            'pagination': {
                'current_page': 1,
                'total_pages': 0,
                'per_page': 10,
                'total': 0,
                'has_previous': False,
                'has_next': False,
                'previous_page': None,
                'next_page': None
            }
        })

def api_references_lorong_by_dusun(request):
    """API references lorong by dusun view"""
    from django.http import JsonResponse
    try:
        from references.models import Lorong
        
        dusun_id = request.GET.get('dusun_id')
        if not dusun_id:
            return JsonResponse({
                'success': False,
                'data': [],
                'message': 'dusun_id parameter is required'
            })
        
        # Get all lorong for the specified dusun
        lorong_list = Lorong.objects.filter(dusun_id=dusun_id, is_active=True).order_by('nama_lorong')
        
        data = []
        for lorong in lorong_list:
            data.append({
                'id': lorong.id,
                'nama_lorong': lorong.nama_lorong,
                'dusun_id': lorong.dusun_id,
                'dusun_name': lorong.dusun.name if lorong.dusun else '',
                'is_active': lorong.is_active,
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'message': f'Found {len(data)} lorong for dusun {dusun_id}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'data': [],
            'message': f'Error loading lorong: {str(e)}'
        })

def api_references_residents_search(request):
    """API references residents search view"""
    from django.http import JsonResponse
    from references.models import Penduduk
    from django.db.models import Q
    
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({
                'success': True,
                'data': []
            })
        
        # Search penduduk by name or NIK
        penduduk_list = Penduduk.objects.filter(
            Q(name__icontains=query) | Q(nik__icontains=query)
        ).order_by('name')[:20]  # Limit to 20 results
        
        data = []
        for penduduk in penduduk_list:
            data.append({
                'id': penduduk.id,
                'name': penduduk.name,
                'nik': penduduk.nik or '',
                'gender': penduduk.gender,
                'birth_date': penduduk.birth_date.isoformat() if penduduk.birth_date else None,
                'birth_place': penduduk.birth_place or '',
                'religion': penduduk.religion or '',
                'education': penduduk.education or '',
                'occupation': penduduk.occupation or '',
                'marital_status': penduduk.marital_status or '',
                'phone_number': penduduk.phone_number or '',
                'full_address': penduduk.full_address or '',
                'rt_number': penduduk.rt_number or '',
                'rw_number': penduduk.rw_number or '',
                'house_number': penduduk.house_number or '',
                'kk_number': penduduk.kk_number or '',
                'relationship_to_head': penduduk.relationship_to_head or '',
                'is_active': penduduk.is_active
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error searching residents: {str(e)}'
        })

def api_references_penduduk_list(request):
    """API references penduduk list view"""
    from django.http import JsonResponse
    from references.models import Penduduk
    from django.db.models import Q
    
    try:
        # Get query parameters
        kk_number = request.GET.get('kk_number', '').strip()
        search = request.GET.get('search', '').strip()
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        # Build query
        queryset = Penduduk.objects.all()
        
        # Filter by KK number if provided
        if kk_number:
            queryset = queryset.filter(kk_number=kk_number)
        
        # Search filter
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(nik__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        # Order by name
        queryset = queryset.order_by('name')
        
        # Pagination
        from django.core.paginator import Paginator
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Build response data
        data = []
        for penduduk in page_obj:
            data.append({
                'id': penduduk.id,
                'name': penduduk.name,
                'nik': penduduk.nik or '',
                'gender': penduduk.gender,
                'birth_date': penduduk.birth_date.isoformat() if penduduk.birth_date else None,
                'birth_place': penduduk.birth_place or '',
                'religion': penduduk.religion or '',
                'education': penduduk.education or '',
                'occupation': penduduk.occupation or '',
                'marital_status': penduduk.marital_status or '',
                'phone_number': penduduk.phone_number or '',
                'full_address': penduduk.full_address or '',
                'rt_number': penduduk.rt_number or '',
                'rw_number': penduduk.rw_number or '',
                'house_number': penduduk.house_number or '',
                'kk_number': penduduk.kk_number or '',
                'relationship_to_head': penduduk.relationship_to_head or '',
                'is_active': penduduk.is_active,
                'is_alive': getattr(penduduk, 'is_alive', True)  # Default to alive if field doesn't exist
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'per_page': per_page,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error loading penduduk data: {str(e)}'
        })

# Penduduk CRUD Views
def references_penduduk_list(request):
    """Penduduk list view"""
    from references.views import penduduk_list
    return penduduk_list(request)

def references_penduduk_add(request):
    """Penduduk add view"""
    from references.views import penduduk_add
    return penduduk_add(request)

def references_penduduk_edit(request, penduduk_id):
    """Penduduk edit view"""
    from references.views import penduduk_edit
    return penduduk_edit(request, penduduk_id)

def references_penduduk_detail(request, penduduk_id):
    """Penduduk detail view"""
    from references.views import penduduk_detail
    return penduduk_detail(request, penduduk_id)

def references_penduduk_delete(request, penduduk_id):
    """Penduduk delete view"""
    from references.views import penduduk_delete
    return penduduk_delete(request, penduduk_id)

def references_penduduk_upload_photo(request, penduduk_id):
    """Penduduk upload photo view"""
    from references.views import penduduk_upload_photo
    # Add penduduk_id to POST data if not present
    if request.method == 'POST' and 'penduduk_id' not in request.POST:
        request.POST = request.POST.copy()
        request.POST['penduduk_id'] = str(penduduk_id)
    return penduduk_upload_photo(request)

def references_penduduk_bulk_delete(request):
    """Penduduk bulk delete view"""
    from references.views import penduduk_bulk_delete
    return penduduk_bulk_delete(request)

def references_penduduk_bulk_activate(request):
    """Penduduk bulk activate view"""
    from references.views import penduduk_bulk_activate
    return penduduk_bulk_activate(request)

def references_penduduk_bulk_deactivate(request):
    """Penduduk bulk deactivate view"""
    from references.views import penduduk_bulk_deactivate
    return penduduk_bulk_deactivate(request)

def references_penduduk_export_excel(request):
    """Penduduk export Excel view"""
    from references.views_import_export import export_data
    return export_data(request, 'penduduk', 'excel')

def references_penduduk_export_csv(request):
    """Penduduk export CSV view"""
    from references.views_import_export import export_data
    return export_data(request, 'penduduk', 'csv')

def references_penduduk_export_json(request):
    """Penduduk export JSON view"""
    from references.views_import_export import export_data
    return export_data(request, 'penduduk', 'json')

def references_penduduk_export_pdf(request):
    """Penduduk export PDF view"""
    from references.views_import_export import export_data
    return export_data(request, 'penduduk', 'pdf')

def references_dusun_list(request):
    """References dusun list view"""
    from references.views import dusun_list
    return dusun_list(request)

def references_dusun_add(request):
    """References dusun add view"""
    from references.views import dusun_add
    return dusun_add(request)

def references_dusun_edit(request, dusun_id):
    """References dusun edit view"""
    from references.views import dusun_edit
    return dusun_edit(request, dusun_id)

def references_dusun_delete(request, dusun_id):
    """References dusun delete view"""
    from references.views import dusun_delete
    return dusun_delete(request, dusun_id)

def references_dusun_detail(request, dusun_id):
    """References dusun detail view"""
    from references.views import dusun_detail
    return dusun_detail(request, dusun_id)

# References Dusun Export Functions
def references_dusun_export_excel(request):
    """References dusun export excel view"""
    from django.http import HttpResponse
    return HttpResponse("Dusun Excel export not implemented yet", content_type='text/plain')

def references_dusun_export_csv(request):
    """References dusun export csv view"""
    from django.http import HttpResponse
    return HttpResponse("Dusun CSV export not implemented yet", content_type='text/plain')

def references_dusun_export_json(request):
    """References dusun export json view"""
    from django.http import JsonResponse
    return JsonResponse({"message": "Dusun JSON export not implemented yet"})

def references_dusun_export_pdf(request):
    """References dusun export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("Dusun PDF export not implemented yet", content_type='text/plain')

def references_dusun_bulk_delete(request):
    """References dusun bulk delete view"""
    from django.http import HttpResponse
    return HttpResponse("Dusun bulk delete not implemented yet", content_type='text/plain')

def references_dusun_bulk_activate(request):
    """References dusun bulk activate view"""
    from django.http import HttpResponse
    return HttpResponse("Dusun bulk activate not implemented yet", content_type='text/plain')

def references_dusun_bulk_deactivate(request):
    """References dusun bulk deactivate view"""
    from django.http import HttpResponse
    return HttpResponse("Dusun bulk deactivate not implemented yet", content_type='text/plain')

# References Lorong CRUD Functions
def references_lorong_add(request):
    """References lorong add view"""
    from references.views import lorong_add
    return lorong_add(request)

def references_lorong_edit(request, lorong_id):
    """References lorong edit view"""
    from references.views import lorong_edit
    return lorong_edit(request, lorong_id)

def references_lorong_delete(request, lorong_id):
    """References lorong delete view"""
    from references.views import lorong_delete
    return lorong_delete(request, lorong_id)

def references_lorong_detail(request, lorong_id):
    """References lorong detail view"""
    from references.views import lorong_detail
    return lorong_detail(request, lorong_id)

# References Lorong Export Functions
def references_lorong_export_excel(request):
    """References lorong export excel view"""
    from django.http import HttpResponse
    return HttpResponse("Lorong Excel export not implemented yet", content_type='text/plain')

def references_lorong_export_csv(request):
    """References lorong export csv view"""
    from django.http import HttpResponse
    return HttpResponse("Lorong CSV export not implemented yet", content_type='text/plain')

def references_lorong_export_json(request):
    """References lorong export json view"""
    from django.http import JsonResponse
    return JsonResponse({"message": "Lorong JSON export not implemented yet"})

def references_lorong_export_pdf(request):
    """References lorong export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("Lorong PDF export not implemented yet", content_type='text/plain')

def references_lorong_bulk_delete(request):
    """References lorong bulk delete view"""
    from django.http import HttpResponse
    return HttpResponse("Lorong bulk delete not implemented yet", content_type='text/plain')

def references_lorong_bulk_activate(request):
    """References lorong bulk activate view"""
    from django.http import HttpResponse
    return HttpResponse("Lorong bulk activate not implemented yet", content_type='text/plain')

def references_lorong_bulk_deactivate(request):
    """References lorong bulk deactivate view"""
    from django.http import HttpResponse
    return HttpResponse("Lorong bulk deactivate not implemented yet", content_type='text/plain')

def references_lorong_list(request):
    """References lorong list view"""
    from references.views import lorong_list
    return lorong_list(request)

# References RW CRUD Functions
def references_rw_add(request):
    """References rw add view"""
    from references.views import rw_add
    return rw_add(request)

def references_rw_edit(request, rw_id):
    """References rw edit view"""
    from references.views import rw_edit
    return rw_edit(request, rw_id)

def references_rw_delete(request, rw_id):
    """References rw delete view"""
    from references.views import rw_delete
    return rw_delete(request, rw_id)

def references_rw_detail(request, rw_id):
    """References rw detail view"""
    from references.views import rw_detail
    return rw_detail(request, rw_id)

# References RW Export Functions
def references_rw_export_excel(request):
    """References rw export excel view"""
    from django.http import HttpResponse
    return HttpResponse("RW Excel export not implemented yet", content_type='text/plain')

def references_rw_export_csv(request):
    """References rw export csv view"""
    from django.http import HttpResponse
    return HttpResponse("RW CSV export not implemented yet", content_type='text/plain')

def references_rw_export_json(request):
    """References rw export json view"""
    from django.http import JsonResponse
    return JsonResponse({"message": "RW JSON export not implemented yet"})

def references_rw_export_pdf(request):
    """References rw export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("RW PDF export not implemented yet", content_type='text/plain')

def references_rw_bulk_delete(request):
    """References rw bulk delete view"""
    from django.http import HttpResponse
    return HttpResponse("RW bulk delete not implemented yet", content_type='text/plain')

def references_rw_bulk_activate(request):
    """References rw bulk activate view"""
    from django.http import HttpResponse
    return HttpResponse("RW bulk activate not implemented yet", content_type='text/plain')

def references_rw_bulk_deactivate(request):
    """References rw bulk deactivate view"""
    from django.http import HttpResponse
    return HttpResponse("RW bulk deactivate not implemented yet", content_type='text/plain')

# References RT CRUD Functions
def references_rt_add(request):
    """References rt add view"""
    from references.views import rt_add
    return rt_add(request)

def references_rt_edit(request, rt_id):
    """References rt edit view"""
    from references.views import rt_edit
    return rt_edit(request, rt_id)

def references_rt_delete(request, rt_id):
    """References rt delete view"""
    from references.views import rt_delete
    return rt_delete(request, rt_id)

def references_rt_detail(request, rt_id):
    """References rt detail view"""
    from references.views import rt_detail
    return rt_detail(request, rt_id)

# References RT Export Functions
def references_rt_export_excel(request):
    """References rt export excel view"""
    from django.http import HttpResponse
    return HttpResponse("RT Excel export not implemented yet", content_type='text/plain')

def references_rt_export_csv(request):
    """References rt export csv view"""
    from django.http import HttpResponse
    return HttpResponse("RT CSV export not implemented yet", content_type='text/plain')

def references_rt_export_json(request):
    """References rt export json view"""
    from django.http import JsonResponse
    return JsonResponse({"message": "RT JSON export not implemented yet"})

def references_rt_export_pdf(request):
    """References rt export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("RT PDF export not implemented yet", content_type='text/plain')

def references_rt_bulk_delete(request):
    """References rt bulk delete view"""
    from django.http import HttpResponse
    return HttpResponse("RT bulk delete not implemented yet", content_type='text/plain')

def references_rt_bulk_activate(request):
    """References rt bulk activate view"""
    from django.http import HttpResponse
    return HttpResponse("RT bulk activate not implemented yet", content_type='text/plain')

def references_rt_bulk_deactivate(request):
    """References rt bulk deactivate view"""
    from django.http import HttpResponse
    return HttpResponse("RT bulk deactivate not implemented yet", content_type='text/plain')

# References Disabilitas CRUD Functions
def references_disabilitas_add(request):
    """References disabilitas add view"""
    from references.views import disabilitas_add
    return disabilitas_add(request)

def references_disabilitas_edit(request, disabilitas_id):
    """References disabilitas edit view"""
    from references.views import disabilitas_edit
    return disabilitas_edit(request, disabilitas_id)

def references_disabilitas_delete(request, disabilitas_id):
    """References disabilitas delete view"""
    from references.views import disabilitas_delete
    return disabilitas_delete(request, disabilitas_id)

def references_disabilitas_detail(request, disabilitas_id):
    """References disabilitas detail view"""
    from references.views import disabilitas_detail
    return disabilitas_detail(request, disabilitas_id)

# References Disabilitas Export Functions
def references_disabilitas_export_excel(request):
    """References disabilitas export excel view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas Excel export not implemented yet", content_type='text/plain')

def references_disabilitas_export_csv(request):
    """References disabilitas export csv view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas CSV export not implemented yet", content_type='text/plain')

def references_disabilitas_export_json(request):
    """References disabilitas export json view"""
    from django.http import JsonResponse
    return JsonResponse({"message": "Disabilitas JSON export not implemented yet"})

def references_disabilitas_export_pdf(request):
    """References disabilitas export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas PDF export not implemented yet", content_type='text/plain')

def references_disabilitas_bulk_delete(request):
    """References disabilitas bulk delete view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas bulk delete not implemented yet", content_type='text/plain')

def references_disabilitas_bulk_activate(request):
    """References disabilitas bulk activate view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas bulk activate not implemented yet", content_type='text/plain')

def references_disabilitas_bulk_deactivate(request):
    """References disabilitas bulk deactivate view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas bulk deactivate not implemented yet", content_type='text/plain')

# References Pelajar CRUD Functions
def references_pelajar_detail(request, pelajar_id):
    """References pelajar detail view"""
    from references.views import pelajar_detail
    return pelajar_detail(request, pelajar_id)

def references_pelajar_edit(request, pelajar_id):
    """References pelajar edit view"""
    from references.views import pelajar_edit
    return pelajar_edit(request, pelajar_id)

def references_pelajar_delete(request, pelajar_id):
    """References pelajar delete view"""
    from references.views import pelajar_delete
    return pelajar_delete(request, pelajar_id)

def references_pelajar_bulk_delete(request):
    """References pelajar bulk delete view"""
    from django.http import HttpResponse
    return HttpResponse("Pelajar bulk delete not implemented yet", content_type='text/plain')

def references_pelajar_bulk_activate(request):
    """References pelajar bulk activate view"""
    from django.http import HttpResponse
    return HttpResponse("Pelajar bulk activate not implemented yet", content_type='text/plain')

def references_pelajar_bulk_deactivate(request):
    """References pelajar bulk deactivate view"""
    from django.http import HttpResponse
    return HttpResponse("Pelajar bulk deactivate not implemented yet", content_type='text/plain')

# References Keluarga CRUD Functions
def references_keluarga_add(request):
    """References keluarga add view"""
    from references.views import keluarga_add
    return keluarga_add(request)

def references_keluarga_edit(request, keluarga_id):
    """References keluarga edit view"""
    from references.views import keluarga_edit
    return keluarga_edit(request, keluarga_id)

def references_keluarga_delete(request, keluarga_id):
    """References keluarga delete view"""
    from references.views import keluarga_delete
    return keluarga_delete(request, keluarga_id)

def references_keluarga_detail(request, keluarga_id):
    """References keluarga detail view"""
    from references.views import keluarga_detail
    return keluarga_detail(request, keluarga_id)

# References Keluarga Export Functions
def references_keluarga_export_excel(request):
    """References keluarga export excel view"""
    from references.views_import_export import export_data
    return export_data(request, 'keluarga', 'excel')

def references_keluarga_export_csv(request):
    """References keluarga export csv view"""
    from references.views_import_export import export_data
    return export_data(request, 'keluarga', 'csv')

def references_keluarga_export_json(request):
    """References keluarga export json view"""
    from references.views_import_export import export_data
    return export_data(request, 'keluarga', 'json')

def references_keluarga_export_pdf(request):
    """References keluarga export pdf view"""
    from references.views_import_export import export_data
    return export_data(request, 'keluarga', 'pdf')

def references_keluarga_bulk_delete(request):
    """References keluarga bulk delete view"""
    from references.views import keluarga_bulk_delete
    return keluarga_bulk_delete(request)

def references_keluarga_bulk_activate(request):
    """References keluarga bulk activate view"""
    from references.views import keluarga_bulk_activate
    return keluarga_bulk_activate(request)

def references_keluarga_bulk_deactivate(request):
    """References keluarga bulk deactivate view"""
    from references.views import keluarga_bulk_deactivate
    return keluarga_bulk_deactivate(request)

def references_keluarga_update_anggota(request, keluarga_id):
    """References keluarga update anggota view"""
    from references.views import keluarga_update_anggota
    return keluarga_update_anggota(request, keluarga_id)

# Missing RW Functions
def references_rw_list(request):
    """References RW list view"""
    from references.views import rw_list
    return rw_list(request)

def references_rw_add(request):
    """References RW add view"""
    from references.views import rw_create
    return rw_create(request)

def references_rw_edit(request, rw_id):
    """References RW edit view"""
    from references.views import rw_edit
    return rw_edit(request, rw_id)

def references_rw_delete(request, rw_id):
    """References RW delete view"""
    from references.views import rw_delete
    return rw_delete(request, rw_id)

def references_rw_detail(request, rw_id):
    """References RW detail view"""
    from django.http import HttpResponse
    return HttpResponse("RW detail not implemented yet", content_type='text/plain')

def references_rw_export_excel(request):
    """References RW export excel view"""
    from django.http import HttpResponse
    return HttpResponse("RW Excel export not implemented yet", content_type='text/plain')

def references_rw_export_csv(request):
    """References RW export csv view"""
    from django.http import HttpResponse
    return HttpResponse("RW CSV export not implemented yet", content_type='text/plain')

def references_rw_export_json(request):
    """References RW export json view"""
    from django.http import HttpResponse
    return HttpResponse("RW JSON export not implemented yet", content_type='text/plain')

def references_rw_export_pdf(request):
    """References RW export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("RW PDF export not implemented yet", content_type='text/plain')

def references_rw_bulk_delete(request):
    """References RW bulk delete view"""
    from references.views import rw_bulk_delete
    return rw_bulk_delete(request)

def references_rw_bulk_activate(request):
    """References RW bulk activate view"""
    from references.views import rw_bulk_activate
    return rw_bulk_activate(request)

def references_rw_bulk_deactivate(request):
    """References RW bulk deactivate view"""
    from references.views import rw_bulk_deactivate
    return rw_bulk_deactivate(request)

# Missing RT Functions
def references_rt_list(request):
    """References RT list view"""
    from references.views import rt_list
    return rt_list(request)

def references_rt_add(request):
    """References RT add view"""
    from references.views import rt_create
    return rt_create(request)

def references_rt_edit(request, rt_id):
    """References RT edit view"""
    from references.views import rt_edit
    return rt_edit(request, rt_id)

def references_rt_delete(request, rt_id):
    """References RT delete view"""
    from references.views import rt_delete
    return rt_delete(request, rt_id)

def references_rt_detail(request, rt_id):
    """References RT detail view"""
    from django.http import HttpResponse
    return HttpResponse("RT detail not implemented yet", content_type='text/plain')

def references_rt_export_excel(request):
    """References RT export excel view"""
    from django.http import HttpResponse
    return HttpResponse("RT Excel export not implemented yet", content_type='text/plain')

def references_rt_export_csv(request):
    """References RT export csv view"""
    from django.http import HttpResponse
    return HttpResponse("RT CSV export not implemented yet", content_type='text/plain')

def references_rt_export_json(request):
    """References RT export json view"""
    from django.http import HttpResponse
    return HttpResponse("RT JSON export not implemented yet", content_type='text/plain')

def references_rt_export_pdf(request):
    """References RT export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("RT PDF export not implemented yet", content_type='text/plain')

def references_rt_bulk_delete(request):
    """References RT bulk delete view"""
    from references.views import rt_bulk_delete
    return rt_bulk_delete(request)

def references_rt_bulk_activate(request):
    """References RT bulk activate view"""
    from references.views import rt_bulk_activate
    return rt_bulk_activate(request)

def references_rt_bulk_deactivate(request):
    """References RT bulk deactivate view"""
    from references.views import rt_bulk_deactivate
    return rt_bulk_deactivate(request)

# Missing Disabilitas Functions
def references_disabilitas_list(request):
    """References disabilitas list view"""
    from references.views import disabilitas_list
    return disabilitas_list(request)

def references_disabilitas_add(request):
    """References disabilitas add view"""
    from references.views import disabilitas_add
    return disabilitas_add(request)

def references_disabilitas_edit(request, disabilitas_id):
    """References disabilitas edit view"""
    from references.views import disabilitas_edit
    return disabilitas_edit(request, disabilitas_id)

def references_disabilitas_delete(request, disabilitas_id):
    """References disabilitas delete view"""
    from references.views import disabilitas_delete
    return disabilitas_delete(request, disabilitas_id)

def references_disabilitas_detail(request, disabilitas_id):
    """References disabilitas detail view"""
    from references.views import disabilitas_detail
    return disabilitas_detail(request, disabilitas_id)

def references_disabilitas_export_excel(request):
    """References disabilitas export excel view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas Excel export not implemented yet", content_type='text/plain')

def references_disabilitas_export_csv(request):
    """References disabilitas export csv view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas CSV export not implemented yet", content_type='text/plain')

def references_disabilitas_export_json(request):
    """References disabilitas export json view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas JSON export not implemented yet", content_type='text/plain')

def references_disabilitas_export_pdf(request):
    """References disabilitas export pdf view"""
    from django.http import HttpResponse
    return HttpResponse("Disabilitas PDF export not implemented yet", content_type='text/plain')

def references_disabilitas_bulk_delete(request):
    """References disabilitas bulk delete view"""
    from references.views import disabilitas_bulk_delete
    return disabilitas_bulk_delete(request)

def references_disabilitas_bulk_activate(request):
    """References disabilitas bulk activate view"""
    from references.views import disabilitas_bulk_activate
    return disabilitas_bulk_activate(request)

def references_disabilitas_bulk_deactivate(request):
    """References disabilitas bulk deactivate view"""
    from references.views import disabilitas_bulk_deactivate
    return disabilitas_bulk_deactivate(request)

# Missing Pelajar Functions
def references_pelajar_list(request):
    """References pelajar list view"""
    from references.views import pelajar_list
    return pelajar_list(request)

def references_pelajar_detail(request, pelajar_id):
    """References pelajar detail view"""
    from references.views import pelajar_detail
    return pelajar_detail(request, pelajar_id)

def references_pelajar_edit(request, pelajar_id):
    """References pelajar edit view"""
    from references.views import pelajar_edit
    return pelajar_edit(request, pelajar_id)

def references_pelajar_delete(request, pelajar_id):
    """References pelajar delete view"""
    from references.views import pelajar_delete
    return pelajar_delete(request, pelajar_id)

def references_pelajar_bulk_delete(request):
    """References pelajar bulk delete view"""
    from references.views import pelajar_bulk_delete
    return pelajar_bulk_delete(request)

def references_pelajar_bulk_activate(request):
    """References pelajar bulk activate view"""
    from references.views import pelajar_bulk_activate
    return pelajar_bulk_activate(request)

def references_pelajar_bulk_deactivate(request):
    """References pelajar bulk deactivate view"""
    from references.views import pelajar_bulk_deactivate
    return pelajar_bulk_deactivate(request)

def references_rw_list(request):
    """References rw list view"""
    from references.views import rw_list
    return rw_list(request)

def references_rt_list(request):
    """References rt list view"""
    from references.views import rt_list
    return rt_list(request)

def references_disabilitas_list(request):
    """References disabilitas list view"""
    from references.views import disabilitas_list
    return disabilitas_list(request)

def references_pelajar_list(request):
    """References pelajar list view"""
    from references.views import pelajar_list
    return pelajar_list(request)

def references_keluarga_list(request):
    """References keluarga list view"""
    from references.views import keluarga_list
    return keluarga_list(request)

def beneficiaries_dashboard(request):
    """Redirect to beneficiaries admin dashboard"""
    return redirect('/beneficiaries/admin/dashboard/')

def beneficiaries_list(request):
    """Beneficiaries list view"""
    from beneficiaries.views import admin_beneficiaries_list
    return admin_beneficiaries_list(request)

def beneficiary_create(request):
    """Beneficiary create view"""
    from beneficiaries.views import admin_beneficiary_create
    return admin_beneficiary_create(request)

def beneficiary_update(request, pk):
    """Beneficiary update view"""
    from beneficiaries.views import admin_beneficiary_update
    return admin_beneficiary_update(request, pk)

def beneficiary_delete(request, pk):
    """Beneficiary delete view"""
    from beneficiaries.views import admin_beneficiary_delete
    return admin_beneficiary_delete(request, pk)

def beneficiary_detail(request, pk):
    """Beneficiary detail view"""
    from beneficiaries.views import admin_beneficiary_detail
    return admin_beneficiary_detail(request, pk)

def beneficiaries_bulk_delete(request):
    """Beneficiaries bulk delete view"""
    from beneficiaries.views import admin_beneficiaries_bulk_delete
    return admin_beneficiaries_bulk_delete(request)

def beneficiaries_bulk_activate(request):
    """Beneficiaries bulk activate view"""
    from beneficiaries.views import admin_beneficiaries_bulk_activate
    return admin_beneficiaries_bulk_activate(request)

def beneficiaries_bulk_deactivate(request):
    """Beneficiaries bulk deactivate view"""
    from beneficiaries.views import admin_beneficiaries_bulk_deactivate
    return admin_beneficiaries_bulk_deactivate(request)

def beneficiaries_bulk_verify(request):
    """Beneficiaries bulk verify view"""
    from beneficiaries.views import admin_beneficiaries_bulk_verify
    return admin_beneficiaries_bulk_verify(request)

def beneficiaries_export_excel(request):
    """Beneficiaries export excel view"""
    from beneficiaries.views import admin_beneficiaries_export_excel
    return admin_beneficiaries_export_excel(request)

def beneficiaries_export_csv(request):
    """Beneficiaries export csv view"""
    from beneficiaries.views import admin_beneficiaries_export_csv
    return admin_beneficiaries_export_csv(request)

def beneficiaries_export_json(request):
    """Beneficiaries export json view"""
    from beneficiaries.views import admin_beneficiaries_export_json
    return admin_beneficiaries_export_json(request)

def beneficiaries_export_pdf(request):
    """Beneficiaries export pdf view"""
    from beneficiaries.views import admin_beneficiaries_export_pdf
    return admin_beneficiaries_export_pdf(request)

def beneficiaries_import(request):
    """Beneficiaries import view"""
    from beneficiaries.views import admin_beneficiaries_import
    return admin_beneficiaries_import(request)

def beneficiaries_search(request):
    """Beneficiaries search view"""
    from beneficiaries.views import admin_beneficiaries_search
    return admin_beneficiaries_search(request)

def beneficiaries_stats(request):
    """Beneficiaries stats view"""
    from beneficiaries.views import admin_beneficiaries_stats
    return admin_beneficiaries_stats(request)

def beneficiaries_reports(request):
    """Beneficiaries reports view"""
    from beneficiaries.views import admin_beneficiaries_reports
    return admin_beneficiaries_reports(request)

def beneficiaries_analytics(request):
    """Beneficiaries analytics view"""
    from beneficiaries.views import admin_beneficiaries_analytics
    return admin_beneficiaries_analytics(request)

def beneficiaries_categories(request):
    """Beneficiaries categories view"""
    from beneficiaries.views import admin_categories_list
    return admin_categories_list(request)

def beneficiaries_category_create(request):
    """Beneficiaries category create view"""
    from beneficiaries.views import admin_category_create
    return admin_category_create(request)

def beneficiaries_category_edit(request, pk):
    """Beneficiaries category edit view"""
    from beneficiaries.views import admin_category_update
    return admin_category_update(request, pk)

def beneficiaries_category_delete(request, pk):
    """Beneficiaries category delete view"""
    from beneficiaries.views import admin_category_delete
    return admin_category_delete(request, pk)

def beneficiaries_aid_programs(request):
    """Beneficiaries aid programs view"""
    from beneficiaries.views import admin_aid_programs_list
    return admin_aid_programs_list(request)

def beneficiaries_aid_program_create(request):
    """Beneficiaries aid program create view"""
    from beneficiaries.views import admin_aid_program_create
    return admin_aid_program_create(request)

def beneficiaries_aid_program_edit(request, pk):
    """Beneficiaries aid program edit view"""
    from beneficiaries.views import admin_aid_program_update
    return admin_aid_program_update(request, pk)

def beneficiaries_aid_program_delete(request, pk):
    """Beneficiaries aid program delete view"""
    from beneficiaries.views import admin_aid_program_delete
    return admin_aid_program_delete(request, pk)

def beneficiaries_distributions(request):
    """Beneficiaries distributions view"""
    from beneficiaries.views import admin_distributions_list
    return admin_distributions_list(request)

def beneficiaries_distribution_create(request):
    """Beneficiaries distribution create view"""
    from beneficiaries.views import admin_distribution_create
    return admin_distribution_create(request)

def beneficiaries_distribution_update_status(request, pk):
    """Beneficiaries distribution update status view"""
    from beneficiaries.views import admin_distribution_update_status
    return admin_distribution_update_status(request, pk)

def beneficiaries_verifications(request):
    """Beneficiaries verifications view"""
    from beneficiaries.views import admin_verifications_list
    return admin_verifications_list(request)

def beneficiaries_verification_update(request, pk):
    """Beneficiaries verification update view"""
    from beneficiaries.views import admin_verification_update
    return admin_verification_update(request, pk)

def api_beneficiaries_search(request):
    """API beneficiaries search view"""
    from beneficiaries.views import api_beneficiary_search
    return api_beneficiary_search(request)

def api_beneficiaries_stats(request):
    """API beneficiaries stats view"""
    from beneficiaries.views import api_beneficiary_stats
    return api_beneficiary_stats(request)

def category_create(request):
    """Category create view"""
    from beneficiaries.views import admin_category_create
    return admin_category_create(request)

def aid_distribution_create(request):
    """Aid distribution create view"""
    from beneficiaries.views import admin_distribution_create
    return admin_distribution_create(request)

def aid_distributions_list(request):
    """Aid distributions list view"""
    from beneficiaries.views import admin_distributions_list
    return admin_distributions_list(request)

def aid_distribution_detail(request, pk):
    """Aid distribution detail view"""
    from beneficiaries.views import admin_distribution_detail
    return admin_distribution_detail(request, pk)

def aid_distribution_update(request, pk):
    """Aid distribution update view"""
    from beneficiaries.views import admin_distribution_update
    return admin_distribution_update(request, pk)

def aid_distribution_delete(request, pk):
    """Aid distribution delete view"""
    from beneficiaries.views import aid_distribution_delete
    return aid_distribution_delete(request, pk)

def aid_distribution_check(request):
    """Aid distribution check view"""
    from beneficiaries.views import aid_distribution_check
    return aid_distribution_check(request)

def category_detail(request, pk):
    """Category detail view"""
    from beneficiaries.views import admin_category_detail
    return admin_category_detail(request, pk)

def category_update(request, pk):
    """Category update view"""
    from beneficiaries.views import admin_category_update
    return admin_category_update(request, pk)

def category_delete(request, pk):
    """Category delete view"""
    from beneficiaries.views import admin_category_delete
    return admin_category_delete(request, pk)

def api_penduduk_search(request):
    """API endpoint to search penduduk for beneficiaries form"""
    from django.http import JsonResponse
    from django.db.models import Q
    
    try:
        # Import Penduduk model dynamically
        try:
            from references.models import Penduduk
            print("Admin panel api_penduduk_search: Using references.models.Penduduk")
        except ImportError:
            try:
                from letters.models import Penduduk
                print("Admin panel api_penduduk_search: Using letters.models.Penduduk")
            except ImportError:
                return JsonResponse({'error': 'Penduduk model not found'}, status=500)
        
        query = request.GET.get('q', '').strip()
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        # Base queryset - check if we have the right model structure
        try:
            # Check if this is the references model (has 'is_active' and 'is_alive' fields)
            if hasattr(Penduduk, 'is_active') and hasattr(Penduduk, 'is_alive'):
                print("Admin panel: Using references model structure")
                penduduk_list = Penduduk.objects.filter(
                    is_active=True, 
                    is_alive=True
                ).select_related('dusun', 'rt', 'rw', 'created_by', 'updated_by')
            else:
                # This is the letters model (no 'is_active' field)
                print("Admin panel: Using letters model structure")
                penduduk_list = Penduduk.objects.all()
        except Exception as e:
            print(f"Error with penduduk query: {e}")
            # Final fallback - basic queryset
            penduduk_list = Penduduk.objects.all()
        
        # Apply search filter - check which field name to use
        if query:
            try:
                # Check if this is the references model (has 'name' field)
                if hasattr(Penduduk, 'name'):
                    print("Admin panel: Using 'name' field for search")
                    penduduk_list = penduduk_list.filter(
                        Q(name__icontains=query) |
                        Q(nik__icontains=query)
                    )
                else:
                    # This is the letters model (has 'nama' field)
                    print("Admin panel: Using 'nama' field for search")
                    penduduk_list = penduduk_list.filter(
                        Q(nama__icontains=query) |
                        Q(nik__icontains=query)
                    )
            except Exception as e:
                print(f"Error with search: {e}")
                # Final fallback - search by NIK only
                penduduk_list = penduduk_list.filter(nik__icontains=query)
        
        # Pagination
        from django.core.paginator import Paginator
        paginator = Paginator(penduduk_list, per_page)
        page_obj = paginator.get_page(page)
        
        # Format response
        penduduk_data = []
        for penduduk in page_obj:
            # Get name field (try both 'name' and 'nama')
            penduduk_name = getattr(penduduk, 'name', None) or getattr(penduduk, 'nama', '')
            
            # Get address from dusun or alamat field
            address = ''
            if hasattr(penduduk, 'dusun') and penduduk.dusun:
                address = penduduk.dusun.name
                if hasattr(penduduk, 'rt') and penduduk.rt:
                    address += f', RT {penduduk.rt.rt_number}' if address else f'RT {penduduk.rt.rt_number}'
                if hasattr(penduduk, 'rw') and penduduk.rw:
                    address += f', RW {penduduk.rw.rw_number}' if address else f'RW {penduduk.rw.rw_number}'
            else:
                # Fallback to alamat field
                address = getattr(penduduk, 'alamat', '') or ''
            
            # Get phone number (try multiple fields)
            phone = (getattr(penduduk, 'phone_number', '') or 
                    getattr(penduduk, 'mobile_number', '') or 
                    getattr(penduduk, 'telepon', '') or '')
            
            penduduk_data.append({
                'id': penduduk.id,
                'name': penduduk_name,
                'nik': penduduk.nik,
                'address': address,
                'phone': phone,
                'email': getattr(penduduk, 'email', '') or '',
                'display_text': f'{penduduk_name} - {penduduk.nik}',
                'value': f'{penduduk_name} - {penduduk.nik}',
            })
        
        return JsonResponse({
            'success': True,
            'results': penduduk_data,
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'results': [],
            'total': 0
        })

def categories_list(request):
    """Categories list view"""
    from beneficiaries.views import admin_categories_list
    return admin_categories_list(request)

def business_dashboard(request):
    """Redirect to business admin dashboard"""
    return redirect('/business/admin/dashboard/')

def umkm_list(request):
    """UMKM list view"""
    from business.admin_views import admin_ukm_list
    return admin_ukm_list(request)

def koperasi_list(request):
    """Koperasi list view"""
    from business.admin_views import koperasi_list as business_koperasi_list
    return business_koperasi_list(request)

def bumg_list(request):
    """BUMG list view"""
    from business.admin_views import bumg_list as business_bumg_list
    return business_bumg_list(request)

def layanan_jasa_list(request):
    """Layanan Jasa list view"""
    from business.admin_views import admin_layanan_jasa_list
    return admin_layanan_jasa_list(request)

def business_categories_list(request):
    """Business categories list view"""
    from business.admin_views import business_categories_list
    return business_categories_list(request)

def umkm_create(request):
    """UMKM create view"""
    from business.admin_views import umkm_create as business_umkm_create
    return business_umkm_create(request)

def koperasi_create(request):
    """Koperasi create view"""
    from business.admin_views import koperasi_create as business_koperasi_create
    return business_koperasi_create(request)

def bumg_create(request):
    """BUMG create view"""
    from business.admin_views import bumg_create as business_bumg_create
    return business_bumg_create(request)

def layanan_jasa_create(request):
    """Layanan Jasa create view"""
    from business.admin_views import layanan_jasa_create as business_layanan_jasa_create
    return business_layanan_jasa_create(request)

def business_category_create(request):
    """Business category create view"""
    from business.admin_views import admin_category_create
    return admin_category_create(request)

# UMKM CRUD Views
def umkm_detail(request, umkm_id):
    """UMKM detail view"""
    from business.admin_views import umkm_detail as business_umkm_detail
    return business_umkm_detail(request, umkm_id)

def umkm_edit(request, umkm_id):
    """UMKM edit view"""
    from business.admin_views import umkm_edit as business_umkm_edit
    return business_umkm_edit(request, umkm_id)

def umkm_update(request, umkm_id):
    """UMKM update view"""
    from business.admin_views import umkm_update as business_umkm_update
    return business_umkm_update(request, umkm_id)

def umkm_delete(request, umkm_id):
    """UMKM delete view"""
    from business.admin_views import umkm_delete as business_umkm_delete
    return business_umkm_delete(request, umkm_id)

# Koperasi CRUD Views
def koperasi_detail(request, koperasi_id):
    """Koperasi detail view"""
    from business.admin_views import koperasi_detail as business_koperasi_detail
    return business_koperasi_detail(request, koperasi_id)

def koperasi_edit(request, koperasi_id):
    """Koperasi edit view"""
    from business.admin_views import koperasi_edit as business_koperasi_edit
    return business_koperasi_edit(request, koperasi_id)

def koperasi_update(request, koperasi_id):
    """Koperasi update view"""
    from business.admin_views import koperasi_update as business_koperasi_update
    return business_koperasi_update(request, koperasi_id)

def koperasi_delete(request, koperasi_id):
    """Koperasi delete view"""
    from business.admin_views import koperasi_delete as business_koperasi_delete
    return business_koperasi_delete(request, koperasi_id)

# BUMG CRUD Views
def bumg_detail(request, bumg_id):
    """BUMG detail view"""
    from business.admin_views import bumg_detail as business_bumg_detail
    return business_bumg_detail(request, bumg_id)

def bumg_edit(request, bumg_id):
    """BUMG edit view"""
    from business.admin_views import bumg_edit as business_bumg_edit
    return business_bumg_edit(request, bumg_id)

def bumg_update(request, bumg_id):
    """BUMG update view"""
    from business.admin_views import bumg_update as business_bumg_update
    return business_bumg_update(request, bumg_id)

def bumg_delete(request, bumg_id):
    """BUMG delete view"""
    from business.admin_views import bumg_delete as business_bumg_delete
    return business_bumg_delete(request, bumg_id)

# Layanan Jasa CRUD Views
def layanan_jasa_detail(request, layanan_id):
    """Layanan Jasa detail view"""
    from business.admin_views import layanan_jasa_detail as business_layanan_jasa_detail
    return business_layanan_jasa_detail(request, layanan_id)

def layanan_jasa_edit(request, layanan_id):
    """Layanan Jasa edit view"""
    from business.admin_views import layanan_jasa_edit as business_layanan_jasa_edit
    return business_layanan_jasa_edit(request, layanan_id)

def layanan_jasa_update(request, layanan_id):
    """Layanan Jasa update view"""
    from business.admin_views import layanan_jasa_edit as business_layanan_jasa_update
    return business_layanan_jasa_update(request, layanan_id)

def layanan_jasa_delete(request, layanan_id):
    """Layanan Jasa delete view"""
    from business.admin_views import layanan_jasa_delete as business_layanan_jasa_delete
    return business_layanan_jasa_delete(request, layanan_id)

# Business Category CRUD Views
def business_category_detail(request, category_id):
    """Business category detail view"""
    from business.admin_views import business_category_detail
    return business_category_detail(request, category_id)

def business_category_edit(request, category_id):
    """Business category edit view"""
    from business.admin_views import business_category_edit
    return business_category_edit(request, category_id)

def business_category_update(request, category_id):
    """Business category update view"""
    from business.admin_views import business_category_edit
    return business_category_edit(request, category_id)

def business_category_delete(request, category_id):
    """Business category delete view"""
    from business.admin_views import business_category_delete
    return business_category_delete(request, category_id)

def business_category_delete_confirm(request, category_id):
    """Business category delete confirmation view"""
    from business.admin_views import business_category_delete
    return business_category_delete(request, category_id)

# Business API Views
def api_business_penduduk_search(request):
    """API for penduduk search in business forms"""
    if not request.user.is_authenticated:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'message': 'Anda tidak memiliki izin untuk mengakses sumber daya ini.'}, status=403)
    from business.api_views import api_penduduk_search
    return api_penduduk_search(request)

def api_business_umkm_search(request):
    """API for UMKM search"""
    from business.admin_views import api_business_search
    return api_business_search(request)

def api_business_koperasi_search(request):
    """API for Koperasi search"""
    from business.admin_views import api_business_search
    return api_business_search(request)

def api_business_bumg_search(request):
    """API for BUMG search"""
    from business.admin_views import api_business_search
    return api_business_search(request)

def api_business_layanan_search(request):
    """API for Layanan Jasa search"""
    from business.admin_views import api_business_search
    return api_business_search(request)

def complaints_dashboard(request):
    """Redirect to complaints admin dashboard"""
    return redirect('/complaints/admin/dashboard/')

def complaints_list(request):
    """Complaints list view"""
    from complaints.views import admin_complaints_list
    return admin_complaints_list(request)

def complaint_categories_list(request):
    """Complaint categories list view"""
    from complaints.views import admin_complaint_categories_list
    return admin_complaint_categories_list(request)

def verifications_list(request):
    """Verifications list view"""
    from complaints.views import admin_verifications_list
    return admin_verifications_list(request)

def complaint_detail(request, pk):
    """Complaint detail view"""
    from complaints.views import admin_complaint_detail
    return admin_complaint_detail(request, pk)

def complaint_edit(request, pk):
    """Complaint edit view"""
    from complaints.views import admin_complaint_update
    return admin_complaint_update(request, pk)

def complaint_update(request, pk):
    """Complaint update view"""
    from complaints.views import admin_complaint_update
    return admin_complaint_update(request, pk)

def complaint_delete(request, pk):
    """Complaint delete view"""
    from complaints.views import admin_complaint_delete
    return admin_complaint_delete(request, pk)

def complaint_add_update(request, pk):
    """Complaint add update view"""
    from complaints.views import admin_complaint_add_update
    return admin_complaint_add_update(request, pk)

def verification_dashboard(request):
    """Verification dashboard view"""
    from complaints.views import admin_verification_dashboard
    return admin_verification_dashboard(request)

def verification_create(request, complaint_id):
    """Verification create view"""
    from complaints.views import admin_verification_create
    return admin_verification_create(request, complaint_id)

def verification_detail(request, pk):
    """Verification detail view"""
    from complaints.views import admin_verification_detail
    return admin_verification_detail(request, pk)

def verification_update(request, pk):
    """Verification update view"""
    from complaints.views import admin_verification_update
    return admin_verification_update(request, pk)

def verification_delete(request, pk):
    """Verification delete view"""
    from complaints.views import admin_verification_delete
    return admin_verification_delete(request, pk)

def documents_dashboard(request):
    """Documents dashboard view"""
    from documents.views import documents_dashboard
    return documents_dashboard(request)

def documents_list(request):
    """Documents list view"""
    from documents.views import documents_list
    return documents_list(request)

def document_requests_list(request):
    """Document requests list view"""
    from documents.views import document_requests_list
    return document_requests_list(request)

def document_types_list(request):
    """Document types list view"""
    from documents.views import document_types_list
    return document_types_list(request)

def document_templates_list(request):
    """Document templates list view"""
    from documents.views import document_templates_list
    return document_templates_list(request)

def tourism_dashboard(request):
    """Redirect to tourism admin dashboard"""
    return redirect('/tourism/admin/')

def tourism_locations_list(request):
    """Tourism locations list view"""
    from tourism.views import admin_panel_location_list
    return admin_panel_location_list(request)

def tourism_categories_list(request):
    """Tourism categories list view"""
    from tourism.views import admin_panel_category_list
    return admin_panel_category_list(request)

def tourism_events_list(request):
    """Tourism events list view"""
    from tourism.views import admin_panel_event_list
    return admin_panel_event_list(request)

def tourism_location_create(request):
    """Tourism location create view"""
    from tourism.views import admin_panel_location_create
    return admin_panel_location_create(request)

def tourism_location_detail(request, location_id):
    """Tourism location detail view"""
    from tourism.views import admin_panel_location_detail
    return admin_panel_location_detail(request, location_id)

def tourism_location_edit(request, location_id):
    """Tourism location edit view"""
    from tourism.views import admin_panel_location_update
    return admin_panel_location_update(request, location_id)

def tourism_location_delete(request, location_id):
    """Tourism location delete view"""
    from tourism.views import admin_panel_location_delete
    return admin_panel_location_delete(request, location_id)

def tourism_location_toggle_status(request, location_id):
    """Tourism location toggle status view"""
    from tourism.views import admin_panel_location_toggle_status
    return admin_panel_location_toggle_status(request, location_id)

def tourism_location_toggle_featured(request, location_id):
    """Tourism location toggle featured view"""
    from tourism.views import admin_panel_location_toggle_featured
    return admin_panel_location_toggle_featured(request, location_id)

# Tourism Categories
def tourism_category_create(request):
    """Tourism category create view"""
    from tourism.views import admin_panel_category_create
    return admin_panel_category_create(request)

def tourism_category_detail(request, category_id):
    """Tourism category detail view"""
    from tourism.views import admin_panel_category_detail
    return admin_panel_category_detail(request, category_id)

def tourism_category_edit(request, category_id):
    """Tourism category edit view"""
    from tourism.views import admin_panel_category_update
    return admin_panel_category_update(request, category_id)

def tourism_category_delete(request, category_id):
    """Tourism category delete view"""
    from tourism.views import admin_panel_category_delete
    return admin_panel_category_delete(request, category_id)

# Tourism Packages
def tourism_packages_list(request):
    """Tourism packages list view"""
    from tourism.views import admin_panel_package_list
    return admin_panel_package_list(request)

def tourism_package_create(request):
    """Tourism package create view"""
    from tourism.views import admin_panel_package_create
    return admin_panel_package_create(request)

def tourism_package_detail(request, package_id):
    """Tourism package detail view"""
    from tourism.views import admin_panel_package_detail
    return admin_panel_package_detail(request, package_id)

def tourism_package_edit(request, package_id):
    """Tourism package edit view"""
    from tourism.views import admin_panel_package_update
    return admin_panel_package_update(request, package_id)

def tourism_package_delete(request, package_id):
    """Tourism package delete view"""
    from tourism.views import admin_panel_package_delete
    return admin_panel_package_delete(request, package_id)

# Tourism Events
def tourism_event_create(request):
    """Tourism event create view"""
    from tourism.views import admin_panel_event_create
    return admin_panel_event_create(request)

def tourism_event_detail(request, event_id):
    """Tourism event detail view"""
    from tourism.views import admin_panel_event_detail
    return admin_panel_event_detail(request, event_id)

def tourism_event_edit(request, event_id):
    """Tourism event edit view"""
    from tourism.views import admin_panel_event_update
    return admin_panel_event_update(request, event_id)

def tourism_event_delete(request, event_id):
    """Tourism event delete view"""
    from tourism.views import admin_panel_event_delete
    return admin_panel_event_delete(request, event_id)

# Tourism Reviews
def tourism_reviews_list(request):
    """Tourism reviews list view"""
    from tourism.views import admin_panel_review_list
    return admin_panel_review_list(request)

def tourism_review_approve(request, review_id):
    """Tourism review approve view"""
    from tourism.views import admin_panel_review_approve
    return admin_panel_review_approve(request, review_id)

def tourism_review_reject(request, review_id):
    """Tourism review reject view"""
    from tourism.views import admin_panel_review_reject
    return admin_panel_review_reject(request, review_id)

def tourism_review_delete(request, review_id):
    """Tourism review delete view"""
    from tourism.views import admin_panel_review_delete
    return admin_panel_review_delete(request, review_id)

# Tourism Gallery
def tourism_gallery_list(request):
    """Tourism gallery list view"""
    from tourism.views import admin_panel_gallery_list
    return admin_panel_gallery_list(request)

def tourism_gallery_delete(request, gallery_id):
    """Tourism gallery delete view"""
    from tourism.views import admin_panel_gallery_delete
    return admin_panel_gallery_delete(request, gallery_id)

# Tourism FAQ
def tourism_faq_list(request):
    """Tourism FAQ list view"""
    from tourism.views import admin_panel_faq_list
    return admin_panel_faq_list(request)

# Tourism Reports
def tourism_reports(request):
    """Tourism reports view"""
    from tourism.views import admin_panel_reports
    return admin_panel_reports(request)

def tourism_export_data(request):
    """Tourism export data view"""
    from tourism.views import admin_panel_export_data
    return admin_panel_export_data(request)

def tourism_bulk_operations(request):
    """Tourism bulk operations view"""
    from tourism.views import admin_panel_bulk_operations
    return admin_panel_bulk_operations(request)

# Tourism Settings
def tourism_settings(request):
    """Tourism settings view"""
    from tourism.views import admin_panel_settings
    return admin_panel_settings(request)

# Tourism API
def tourism_api_locations(request):
    """Tourism API locations view"""
    from tourism.views import admin_panel_api_locations
    return admin_panel_api_locations(request)

def tourism_api_categories(request):
    """Tourism API categories view"""
    from tourism.views import admin_panel_api_categories
    return admin_panel_api_categories(request)

def tourism_api_statistics(request):
    """Tourism API statistics view"""
    from tourism.views import admin_panel_api_statistics
    return admin_panel_api_statistics(request)

def tourism_search_locations(request):
    """Tourism search locations view"""
    from tourism.views import admin_panel_search_locations
    return admin_panel_search_locations(request)

def tourism_location_stats(request, location_id):
    """Tourism location stats view"""
    from tourism.views import admin_panel_location_stats
    return admin_panel_location_stats(request, location_id)

def village_profile_dashboard(request):
    """Village profile admin dashboard"""
    try:
        # Import the village_profile admin view function
        from village_profile.admin_views import village_profile_dashboard as village_dashboard_view
        return village_dashboard_view(request)
    except ImportError as e:
        # Fallback if import fails
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading village profile dashboard: {str(e)}')
        return render(request, 'admin_panel/village_profile/dashboard.html', {
            'page_title': 'Dashboard Profil Desa',
            'active_menu': 'village_profile',
            'active_submenu': 'dashboard',
            'village_profile': None,
            'stats': {},
            'recent_activities': [],
        })

def news_dashboard(request):
    """News admin dashboard"""
    try:
        # Import the news admin view function
        from news.views import admin_news_dashboard as news_dashboard_view
        return news_dashboard_view(request)
    except ImportError as e:
        # Fallback if import fails
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news dashboard: {str(e)}')
        return render(request, 'admin_panel/news/dashboard.html', {
            'page_title': 'Dashboard Berita',
            'active_menu': 'news',
            'active_submenu': 'dashboard',
            'news_count': 0,
            'categories_count': 0,
            'comments_count': 0,
            'recent_news': [],
        })

def news_list(request):
    """News list view"""
    try:
        from news.views import admin_news_list
        return admin_news_list(request)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news list: {str(e)}')
        return render(request, 'admin_panel/news/list.html', {
            'page_title': 'Daftar Berita',
            'active_menu': 'news',
            'active_submenu': 'list',
            'news_list': [],
        })

def news_categories_list(request):
    """News categories list view"""
    try:
        from news.views import admin_news_categories_list
        return admin_news_categories_list(request)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news categories: {str(e)}')
        return render(request, 'admin_panel/news/categories.html', {
            'page_title': 'Kategori Berita',
            'active_menu': 'news',
            'active_submenu': 'categories',
            'categories_list': [],
        })

def news_create(request):
    """News create view"""
    try:
        from news.views import admin_news_create
        return admin_news_create(request)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news create form: {str(e)}')
        return render(request, 'admin_panel/news/form.html', {
            'page_title': 'Tambah Berita',
            'active_menu': 'news',
            'active_submenu': 'add',
            'form': None,
        })

def news_category_create(request):
    """News category create view"""
    try:
        from news.views import admin_news_category_create
        return admin_news_category_create(request)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news category create form: {str(e)}')
        return render(request, 'admin_panel/news/categories.html', {
            'page_title': 'Tambah Kategori Berita',
            'active_menu': 'news',
            'active_submenu': 'categories',
            'form': None,
        })

def announcement_create(request):
    """Announcement create view"""
    try:
        from news.views import admin_announcement_create
        return admin_announcement_create(request)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading announcement create form: {str(e)}')
        return render(request, 'admin_panel/news/announcement_form.html', {
            'page_title': 'Tambah Pengumuman',
            'active_menu': 'news',
            'active_submenu': 'announcements',
            'form': None,
        })

def news_comments(request):
    """News comments view"""
    try:
        from news.views import admin_news_comments_list
        return admin_news_comments_list(request)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news comments: {str(e)}')
        return render(request, 'admin_panel/news/comments.html', {
            'page_title': 'Komentar Berita',
            'active_menu': 'news',
            'active_submenu': 'comments',
            'comments_list': [],
        })

def news_detail(request, pk):
    """News detail view"""
    try:
        from news.views import admin_news_detail
        return admin_news_detail(request, pk)
    except ImportError as e:
        from django.shortcuts import render, get_object_or_404
        from django.contrib import messages
        messages.error(request, f'Error loading news detail: {str(e)}')
        return render(request, 'admin_panel/news/detail.html', {
            'page_title': 'Detail Berita',
            'active_menu': 'news',
            'active_submenu': 'detail',
            'news': None,
        })

def news_edit(request, pk):
    """News edit view"""
    try:
        from news.views import admin_news_update
        return admin_news_update(request, pk)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news edit form: {str(e)}')
        return render(request, 'admin_panel/news/form.html', {
            'page_title': 'Edit Berita',
            'active_menu': 'news',
            'active_submenu': 'edit',
            'form': None,
        })

def news_delete(request, pk):
    """News delete view"""
    try:
        from news.views import admin_news_delete
        return admin_news_delete(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error deleting news: {str(e)}')
        return redirect('admin_panel:news_list')

def news_upload_image(request):
    """News upload image view"""
    try:
        from news.views import admin_news_upload_image
        return admin_news_upload_image(request)
    except ImportError as e:
        from django.http import JsonResponse
        return JsonResponse({'error': f'Error uploading image: {str(e)}'}, status=500)

def news_category_edit(request, pk):
    """News category edit view"""
    try:
        from news.views import admin_news_category_update
        return admin_news_category_update(request, pk)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading category edit form: {str(e)}')
        return render(request, 'admin_panel/news/categories.html', {
            'page_title': 'Edit Kategori',
            'active_menu': 'news',
            'active_submenu': 'categories',
            'form': None,
        })

def news_category_update(request, pk):
    """News category update view"""
    try:
        from news.views import admin_news_category_update
        return admin_news_category_update(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error updating category: {str(e)}')
        return redirect('admin_panel:news_categories_list')

def news_category_delete(request, pk):
    """News category delete view"""
    try:
        from news.views import admin_news_category_delete
        return admin_news_category_delete(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error deleting category: {str(e)}')
        return redirect('admin_panel:news_categories_list')

def news_tags_list(request):
    """News tags list view"""
    try:
        from news.views import admin_news_tags_list
        return admin_news_tags_list(request)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news tags: {str(e)}')
        return render(request, 'admin_panel/news/tags.html', {
            'page_title': 'Tag Berita',
            'active_menu': 'news',
            'active_submenu': 'tags',
            'tags_list': [],
        })

def news_tag_create(request):
    """News tag create view"""
    try:
        from news.views import admin_news_tag_create
        return admin_news_tag_create(request)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading tag create form: {str(e)}')
        return render(request, 'admin_panel/news/tags.html', {
            'page_title': 'Tambah Tag',
            'active_menu': 'news',
            'active_submenu': 'tags',
            'form': None,
        })

def news_tag_edit(request, pk):
    """News tag edit view"""
    try:
        from news.views import admin_news_tag_update
        return admin_news_tag_update(request, pk)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading tag edit form: {str(e)}')
        return render(request, 'admin_panel/news/tags.html', {
            'page_title': 'Edit Tag',
            'active_menu': 'news',
            'active_submenu': 'tags',
            'form': None,
        })

def news_tag_update(request, pk):
    """News tag update view"""
    try:
        from news.views import admin_news_tag_update
        return admin_news_tag_update(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error updating tag: {str(e)}')
        return redirect('admin_panel:news_tags_list')

def news_tag_delete(request, pk):
    """News tag delete view"""
    try:
        from news.views import admin_news_tag_delete
        return admin_news_tag_delete(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error deleting tag: {str(e)}')
        return redirect('admin_panel:news_tags_list')

def news_comment_approve(request, pk):
    """News comment approve view"""
    try:
        from news.views import admin_news_comment_approve
        return admin_news_comment_approve(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error approving comment: {str(e)}')
        return redirect('admin_panel:news_comments')

def news_comment_reject(request, pk):
    """News comment reject view"""
    try:
        from news.views import admin_news_comment_reject
        return admin_news_comment_reject(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error rejecting comment: {str(e)}')
        return redirect('admin_panel:news_comments')

def news_comment_delete(request, pk):
    """News comment delete view"""
    try:
        from news.views import admin_news_comment_delete
        return admin_news_comment_delete(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error deleting comment: {str(e)}')
        return redirect('admin_panel:news_comments')

def news_comment_spam(request, pk):
    """News comment spam view"""
    try:
        from news.views import admin_news_comment_spam
        return admin_news_comment_spam(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error marking comment as spam: {str(e)}')
        return redirect('admin_panel:news_comments')

def news_duplicate(request, pk):
    """News duplicate view"""
    try:
        from news.views import admin_news_duplicate
        return admin_news_duplicate(request, pk)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error duplicating news: {str(e)}')
        return redirect('admin_panel:news_list')

def news_preview(request, pk):
    """News preview view"""
    try:
        from news.views import admin_news_preview
        return admin_news_preview(request, pk)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news preview: {str(e)}')
        return render(request, 'admin_panel/news/detail.html', {
            'page_title': 'Preview Berita',
            'active_menu': 'news',
            'active_submenu': 'preview',
            'news': None,
        })

def news_analytics_detail(request, pk):
    """News analytics detail view"""
    try:
        from news.views import admin_news_analytics_detail
        return admin_news_analytics_detail(request, pk)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news analytics: {str(e)}')
        return render(request, 'admin_panel/news/analytics_detail.html', {
            'page_title': 'Analitik Berita',
            'active_menu': 'news',
            'active_submenu': 'analytics',
            'news': None,
        })

def news_generate_slug(request):
    """News generate slug view"""
    try:
        from news.views import admin_news_generate_slug
        return admin_news_generate_slug(request)
    except ImportError as e:
        from django.http import JsonResponse
        return JsonResponse({'error': f'Error generating slug: {str(e)}'}, status=500)

def news_bulk_update(request):
    """News bulk update view"""
    try:
        from news.views import admin_news_bulk_update
        return admin_news_bulk_update(request)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error bulk updating news: {str(e)}')
        return redirect('admin_panel:news_list')

def news_export(request):
    """News export view"""
    try:
        from news.views import admin_news_export
        return admin_news_export(request)
    except ImportError as e:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, f'Error exporting news: {str(e)}')
        return redirect('admin_panel:news_list')

def news_reports(request):
    """News reports view"""
    try:
        from news.views import admin_news_reports
        return admin_news_reports(request)
    except ImportError as e:
        from django.shortcuts import render
        from django.contrib import messages
        messages.error(request, f'Error loading news reports: {str(e)}')
        return render(request, 'admin_panel/news/reports.html', {
            'page_title': 'Laporan Berita',
            'active_menu': 'news',
            'active_submenu': 'reports',
            'reports_data': {},
        })

# Posyandu views are now handled by the posyandu app directly

def reports_dashboard(request):
    """Reports dashboard"""
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get date range from request
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_from:
        date_from = (timezone.now() - timedelta(days=30)).date()
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Initialize stats
    stats = {
        'beneficiaries_stats': {'total': 0, 'active': 0, 'by_category': []},
        'business_stats': {'total': 0, 'active': 0, 'by_category': []},
        'complaints_stats': {'total': 0, 'pending': 0, 'in_progress': 0, 'resolved': 0, 'by_category': []},
        'documents_stats': {'total_requests': 0, 'approved': 0, 'rejected': 0, 'by_type': []},
        'tourism_stats': {'locations': 0, 'published': 0, 'events': 0, 'packages': 0, 'reviews': 0, 'avg_rating': 0},
        'population_stats': {'total': 0, 'male': 0, 'female': 0, 'by_dusun': []}
    }
    
    try:
        # Beneficiaries stats
        from beneficiaries.models import Beneficiary
        beneficiaries = Beneficiary.objects.filter(created_at__date__range=[date_from, date_to])
        stats['beneficiaries_stats']['total'] = beneficiaries.count()
        stats['beneficiaries_stats']['active'] = beneficiaries.filter(status='active').count()
        
        # Business stats
        from business.models import Business
        businesses = Business.objects.filter(created_at__date__range=[date_from, date_to])
        stats['business_stats']['total'] = businesses.count()
        stats['business_stats']['active'] = businesses.filter(status='active').count()
        
        # Complaints stats
        from complaints.models import Complaint
        complaints = Complaint.objects.filter(created_at__date__range=[date_from, date_to])
        stats['complaints_stats']['total'] = complaints.count()
        stats['complaints_stats']['pending'] = complaints.filter(status='pending').count()
        stats['complaints_stats']['in_progress'] = complaints.filter(status='in_progress').count()
        stats['complaints_stats']['resolved'] = complaints.filter(status='resolved').count()
        
        # Documents stats
        from documents.models import DocumentRequest
        documents = DocumentRequest.objects.filter(created_at__date__range=[date_from, date_to])
        stats['documents_stats']['total_requests'] = documents.count()
        stats['documents_stats']['approved'] = documents.filter(status='approved').count()
        stats['documents_stats']['rejected'] = documents.filter(status='rejected').count()
        
        # Tourism stats
        from tourism.models import TourismLocation
        tourism_locations = TourismLocation.objects.filter(created_at__date__range=[date_from, date_to])
        stats['tourism_stats']['locations'] = tourism_locations.count()
        stats['tourism_stats']['published'] = tourism_locations.filter(status='published').count()
        
        # Population stats
        from references.models import Penduduk
        population = Penduduk.objects.all()
        stats['population_stats']['total'] = population.count()
        stats['population_stats']['male'] = population.filter(gender='L').count()
        stats['population_stats']['female'] = population.filter(gender='P').count()
        
    except Exception as e:
        print(f"Error loading stats: {str(e)}")
        pass
    
    return render(request, 'admin_panel/reports/dashboard.html', {
        'title': 'Laporan',
        'active_menu': 'reports',
        'date_from': date_from,
        'date_to': date_to,
        **stats
    })

def settings_dashboard(request):
    """Settings dashboard"""
    return render(request, 'admin_panel/settings/dashboard.html', {
        'title': 'Pengaturan',
        'active_menu': 'settings'
    })

def export_data(request):
    """Export data view"""
    from django.http import HttpResponse
    import csv
    import json
    from datetime import datetime
    
    export_type = request.GET.get('type', 'all')
    format_type = request.GET.get('format', 'csv')
    
    try:
        if export_type == 'beneficiaries':
            from beneficiaries.models import Beneficiary
            queryset = Beneficiary.objects.all()
            filename = f'beneficiaries_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
        elif export_type == 'businesses':
            from business.models import Business
            queryset = Business.objects.all()
            filename = f'businesses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
        elif export_type == 'complaints':
            from complaints.models import Complaint
            queryset = Complaint.objects.all()
            filename = f'complaints_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
        elif export_type == 'documents':
            from documents.models import DocumentRequest
            queryset = DocumentRequest.objects.all()
            filename = f'documents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
        elif export_type == 'tourism':
            from tourism.models import TourismLocation
            queryset = TourismLocation.objects.all()
            filename = f'tourism_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
        else:  # all
            # Export all data as JSON
            data = {
                'export_date': datetime.now().isoformat(),
                'beneficiaries': [],
                'businesses': [],
                'complaints': [],
                'documents': [],
                'tourism': []
            }
            
            # Add beneficiaries data
            try:
                from beneficiaries.models import Beneficiary
                for item in Beneficiary.objects.all()[:100]:  # Limit to 100 records
                    data['beneficiaries'].append({
                        'id': item.id,
                        'name': getattr(item, 'name', ''),
                        'created_at': item.created_at.isoformat() if hasattr(item, 'created_at') else ''
                    })
            except:
                pass
                
            # Add business data
            try:
                from business.models import Business
                for item in Business.objects.all()[:100]:
                    data['businesses'].append({
                        'id': item.id,
                        'name': getattr(item, 'name', ''),
                        'created_at': item.created_at.isoformat() if hasattr(item, 'created_at') else ''
                    })
            except:
                pass
                
            response = HttpResponse(
                json.dumps(data, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="all_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            return response
        
        # Handle CSV export for specific types
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            writer = csv.writer(response)
            
            # Write headers
            if queryset.exists():
                first_obj = queryset.first()
                headers = [field.name for field in first_obj._meta.fields if field.name != 'id']
                writer.writerow(headers)
                
                # Write data
                for obj in queryset:
                    row = []
                    for field in first_obj._meta.fields:
                        if field.name != 'id':
                            value = getattr(obj, field.name, '')
                            if hasattr(value, 'isoformat'):  # Handle datetime fields
                                value = value.isoformat()
                            row.append(str(value))
                    writer.writerow(row)
            
            return response
            
        else:
            # For other formats, return JSON
            data = []
            for obj in queryset:
                obj_data = {}
                for field in obj._meta.fields:
                    value = getattr(obj, field.name, '')
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    obj_data[field.name] = str(value)
                data.append(obj_data)
            
            response = HttpResponse(
                json.dumps(data, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            return response
            
    except Exception as e:
        print(f"Export error: {str(e)}")
        return HttpResponse(f"Error exporting data: {str(e)}", status=500)

def test_roles(request):
    """Test roles view"""
    return JsonResponse({
        'user': str(request.user),
        'is_authenticated': request.user.is_authenticated,
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'groups': [group.name for group in request.user.groups.all()]
    })

def profile(request):
    """Simple profile view"""
    if not request.user.is_authenticated:
        return redirect('admin_panel:login')
    
    try:
        # Get or create user profile
        from core.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Get recent logins for the user
        recent_logins = []
        try:
            from core.models import LoginHistory
            recent_logins = LoginHistory.objects.filter(user=request.user).order_by('-login_time')[:5]
        except:
            pass
        
        return render(request, 'admin_panel/profil.html', {
            'title': 'Profil',
            'recent_logins': recent_logins,
            'profile': profile,
        })
    except Exception as e:
        print(f"Error in profile view: {str(e)}")
        return render(request, 'admin_panel/profil.html', {
            'title': 'Profil',
            'recent_logins': [],
            'profile': None,
        })

def profile_update(request):
    """Update user profile - simplified version"""
    print(f"DEBUG: profile_update called with method: {request.method}")
    print(f"DEBUG: POST data: {request.POST}")
    print(f"DEBUG: FILES data: {request.FILES}")
    
    if request.method == 'POST':
        try:
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            # Get or create profile
            from core.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            print(f"DEBUG: Profile created: {created}, Profile ID: {profile.id}")
            
            # Update profile fields
            profile.phone = request.POST.get('phone', '')
            profile.address = request.POST.get('address', '')
            profile.birth_date = request.POST.get('birth_date') or None
            profile.gender = request.POST.get('gender', '')
            
            # Handle photo upload
            print(f"DEBUG: Checking for photo in FILES: {'photo' in request.FILES}")
            if 'photo' in request.FILES:
                photo = request.FILES['photo']
                print(f"DEBUG: Photo file received: {photo.name}, size: {photo.size}, type: {photo.content_type}")
                
                # Validate file size (max 2MB)
                if photo.size > 2 * 1024 * 1024:
                    print("DEBUG: Photo too large")
                    messages.error(request, 'Ukuran file terlalu besar! Maksimal 2MB.')
                    return redirect('admin_panel:profile')
                
                # Validate file type
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if photo.content_type not in allowed_types:
                    print(f"DEBUG: Invalid file type: {photo.content_type}")
                    messages.error(request, 'Format file tidak didukung! Gunakan JPG, PNG, GIF, atau WebP.')
                    return redirect('admin_panel:profile')
                
                # Save photo
                print("DEBUG: Saving photo to profile")
                profile.photo = photo
                print(f"DEBUG: Photo saved: {profile.photo.url}")
                print(f"DEBUG: Photo path: {profile.photo.path}")
            else:
                print("DEBUG: No photo in request.FILES")
            
            profile.save()
            print(f"DEBUG: Profile saved successfully")
            
            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('admin_panel:profile')
        except Exception as e:
            print(f"Error in profile_update: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return redirect('admin_panel:profile')
    
    return redirect('admin_panel:profile')

def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not user.check_password(old_password):
            messages.error(request, 'Password lama tidak benar!')
            return redirect('admin_panel:profile')
        
        if new_password1 != new_password2:
            messages.error(request, 'Konfirmasi password tidak cocok!')
            return redirect('admin_panel:profile')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password minimal 8 karakter!')
            return redirect('admin_panel:profile')
        
        user.set_password(new_password1)
        user.save()
        
        messages.success(request, 'Password berhasil diubah!')
        return redirect('admin_panel:profile')
    
    return redirect('admin_panel:profile')


def dashboard_stats_api(request):
    """Dashboard stats API"""
    from django.http import JsonResponse
    
    try:
        # Get real statistics from models
        stats = {
            'success': True,
            'data': {
                # Population data
                'total_penduduk': Penduduk.objects.count() if Penduduk else 0,
                'total_keluarga': Keluarga.objects.count() if Keluarga else 0,
                'total_dusun': Dusun.objects.count() if Dusun else 0,
                'total_lorong': Lorong.objects.count() if Lorong else 0,
                'total_rt': 0,  # Will be calculated from references
                'total_rw': 0,  # Will be calculated from references
                'total_pelajar': 0,  # Will be calculated from references
                'total_disabilitas': 0,  # Will be calculated from references
                
                # Business data
                'total_businesses': 0,
                'total_ukm': UKM.objects.count() if UKM else 0,
                'total_koperasi': Koperasi.objects.count() if Koperasi else 0,
                'total_bumg': BUMG.objects.count() if BUMG else 0,
                'total_layanan_jasa': LayananJasa.objects.count() if LayananJasa else 0,
                
                # Beneficiaries data
                'total_beneficiaries': Beneficiary.objects.count() if Beneficiary else 0,
                
                # Complaints data
                'total_complaints': Complaint.objects.count() if Complaint else 0,
                
                # Documents data
                'total_documents': Document.objects.count() if Document else 0,
                
                # News data
                'total_news': News.objects.count() if News else 0,
                
                # Posyandu data
                'total_posyandu_locations': PosyanduLocation.objects.count() if PosyanduLocation else 0,
                
                # Tourism data
                'total_tourism_locations': 0,  # Will be calculated from tourism app
                
                # User data
                'total_users': CustomUser.objects.count(),
            }
        }
        
        # Calculate additional statistics
        if UKM and Koperasi and BUMG and LayananJasa:
            stats['data']['total_businesses'] = (
                stats['data']['total_ukm'] + 
                stats['data']['total_koperasi'] + 
                stats['data']['total_bumg'] + 
                stats['data']['total_layanan_jasa']
            )
        
        # Try to get RT/RW data from references
        try:
            from references.models import RT, RW, Pelajar, DisabilitasData
            stats['data']['total_rt'] = RT.objects.count() if RT else 0
            stats['data']['total_rw'] = RW.objects.count() if RW else 0
            stats['data']['total_pelajar'] = Pelajar.objects.count() if Pelajar else 0
            stats['data']['total_disabilitas'] = DisabilitasData.objects.count() if DisabilitasData else 0
        except:
            pass
        
        # Try to get tourism data
        try:
            from tourism.models import TourismLocation
            stats['data']['total_tourism_locations'] = TourismLocation.objects.count()
        except:
            pass
        
        return JsonResponse(stats)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': {
                'total_penduduk': 0,
                'total_keluarga': 0,
                'total_businesses': 0,
                'total_beneficiaries': 0,
                'total_complaints': 0,
                'total_documents': 0,
                'total_news': 0,
                'total_posyandu_locations': 0,
                'total_tourism_locations': 0,
                'total_dusun': 0,
                'total_lorong': 0,
                'total_rt': 0,
                'total_rw': 0,
                'total_pelajar': 0,
                'total_disabilitas': 0,
                'total_users': 0,
            }
        })

def api_references_dashboard_data(request):
    """References dashboard data API"""
    from django.http import JsonResponse
    
    try:
        # Try to get real data from models
        from references.models import Penduduk, Dusun, Lorong, RW, RT, DisabilitasData, Pelajar, Keluarga
        
        # Count data safely
        total_penduduk = Penduduk.objects.count() if Penduduk else 0
        total_dusun = Dusun.objects.count() if Dusun else 0
        total_lorong = Lorong.objects.count() if Lorong else 0
        total_rw = RW.objects.count() if RW else 0
        total_rt = RT.objects.count() if RT else 0
        total_disabilitas = DisabilitasData.objects.count() if DisabilitasData else 0
        total_pelajar = Pelajar.objects.count() if Pelajar else 0
        total_keluarga = Keluarga.objects.count() if Keluarga else 0
        
        
        # Get gender distribution
        total_laki_laki = 0
        total_perempuan = 0
        if Penduduk:
            total_laki_laki = Penduduk.objects.filter(gender='L').count()
            total_perempuan = Penduduk.objects.filter(gender='P').count()
        
        # Get age groups
        age_groups = {
            'balita': 0,
            'anak': 0,
            'dewasa': 0,
            'lansia': 0
        }
        
        # Education stats
        education_stats = []
        
        data = {
            'success': True,
            'total_penduduk': total_penduduk,
            'total_keluarga': total_keluarga,
            'total_dusun': total_dusun,
            'total_lorong': total_lorong,
            'total_rw': total_rw,
            'total_rt': total_rt,
            'total_disabilitas': total_disabilitas,
            'total_pelajar': total_pelajar,
            'total_families': total_keluarga,
            'total_laki_laki': total_laki_laki,
            'total_perempuan': total_perempuan,
            'age_groups': age_groups,
            'education_stats': education_stats,
            'last_update': '2025-10-05T17:45:00Z',
            'data_integrity': 100,
            'recent_activities': []
        }
        
    except Exception as e:
        # Fallback to mock data if there's an error
        data = {
            'success': True,
            'total_penduduk': 0,
            'total_keluarga': 0,
            'total_dusun': 0,
            'total_lorong': 0,
            'total_rw': 0,
            'total_rt': 0,
            'total_disabilitas': 0,
            'total_pelajar': 0,
            'total_families': 0,
            'total_laki_laki': 0,
            'total_perempuan': 0,
            'age_groups': {
                'balita': 0,
                'anak': 0,
                'dewasa': 0,
                'lansia': 0
            },
            'education_stats': [],
            'last_update': '2025-10-05T17:45:00Z',
            'data_integrity': 100,
            'recent_activities': []
        }
    
    return JsonResponse(data)

def api_references_keluarga_list(request):
    """API untuk list keluarga dengan pagination dan filter"""
    try:
        from django.core.paginator import Paginator
        
        # Get filter parameters
        search = request.GET.get('search', '')
        dusun_id = request.GET.get('dusun', '')
        rt = request.GET.get('rt', '')
        rw = request.GET.get('rw', '')
        page = int(request.GET.get('page', 1))
        per_page = 20
        
        # Build query
        queryset = Keluarga.objects.select_related('dusun').all()
        
        if search:
            queryset = queryset.filter(
                Q(nama_kepala_keluarga__icontains=search) |
                Q(nomor_kk__icontains=search)
            )
        
        if dusun_id:
            queryset = queryset.filter(dusun_id=dusun_id)
        
        if rt:
            queryset = queryset.filter(rt=rt)
        
        if rw:
            queryset = queryset.filter(rw=rw)
        
        # Pagination
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize data
        data = []
        for keluarga in page_obj:
            # Count family members
            from references.models import Penduduk
            jumlah_anggota = Penduduk.objects.filter(kk_number=keluarga.nomor_kk).count()
            
            data.append({
                'id': keluarga.id,
                'nomor_kk': keluarga.nomor_kk,
                'nama_kepala_keluarga': keluarga.nama_kepala_keluarga,
                'alamat': keluarga.alamat,
                'dusun_name': keluarga.dusun.name if keluarga.dusun else '',
                'rt': keluarga.rt,
                'rw': keluarga.rw,
                'jumlah_anggota': jumlah_anggota,
                'is_active': keluarga.is_active,
                'created_at': keluarga.created_at.isoformat() if keluarga.created_at else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'per_page': per_page,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': [],
            'pagination': {
                'current_page': 1,
                'total_pages': 0,
                'total_items': 0,
                'per_page': 20,
                'has_previous': False,
                'has_next': False,
                'previous_page': None,
                'next_page': None,
            }
        })

def api_references_rw_by_dusun(request, dusun_id):
    """API references RW by dusun view"""
    from django.http import JsonResponse
    try:
        from references.models import RW
        
        # Get all RW for the specified dusun
        rw_list = RW.objects.filter(dusun_id=dusun_id, is_active=True).order_by('rw_number')
        
        data = []
        for rw in rw_list:
            data.append({
                'id': rw.id,
                'rw_number': rw.rw_number,
                'dusun_id': rw.dusun_id,
                'dusun_name': rw.dusun.name if rw.dusun else '',
                'is_active': rw.is_active,
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'message': f'Found {len(data)} RW for dusun {dusun_id}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'data': [],
            'message': f'Error loading RW: {str(e)}'
        })

def api_references_rt_by_rw(request, rw_id):
    """API references RT by RW view"""
    from django.http import JsonResponse
    try:
        from references.models import RT
        
        # Get all RT for the specified RW
        rt_list = RT.objects.filter(rw_id=rw_id, is_active=True).order_by('rt_number')
        
        data = []
        for rt in rt_list:
            data.append({
                'id': rt.id,
                'rt_number': rt.rt_number,
                'rw_id': rt.rw_id,
                'rw_number': rt.rw.rw_number if rt.rw else '',
                'dusun_name': rt.rw.dusun.name if rt.rw and rt.rw.dusun else '',
                'is_active': rt.is_active,
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'message': f'Found {len(data)} RT for RW {rw_id}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'data': [],
            'message': f'Error loading RT: {str(e)}'
        })

def api_references_rw_by_dusun(request, dusun_id):
    """API references RW by dusun view"""
    from django.http import JsonResponse
    try:
        from references.models import RW
        
        # Get all RW for the specified dusun
        rw_list = RW.objects.filter(dusun_id=dusun_id, is_active=True).order_by('rw_number')
        
        data = []
        for rw in rw_list:
            data.append({
                'id': rw.id,
                'rw_number': rw.rw_number,
                'dusun_id': rw.dusun_id,
                'dusun_name': rw.dusun.name if rw.dusun else '',
                'is_active': rw.is_active,
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'message': f'Found {len(data)} RW for dusun {dusun_id}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'data': [],
            'message': f'Error loading RW: {str(e)}'
        })
