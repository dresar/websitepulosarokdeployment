from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.template.loader import render_to_string
import json
from datetime import datetime, timedelta
from .models import (
    LetterType, Letter, LetterAttachment, LetterTracking, 
    LetterTemplate, LetterRecipient
)
from .forms import LetterForm, LetterTypeForm
# Groq service removed
from .services import LetterValidationService
# from references.models import Penduduk, Dusun  # COMMENTED OUT - references app disabled
# Using letters app models instead
try:
    from references.models import Penduduk, Dusun
except ImportError:
    Penduduk = None
    Dusun = None
# from documents.models import DocumentType  # Removed - using simplified models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
# Rate limiter and input validator removed - not needed
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.core.cache import cache
from django.conf import settings
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

# ===========================
# UTILITY FUNCTIONS
# ===========================

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def has_letter_permission(user, permission_name, letter=None):
    """Check if user has specific letter permission"""
    if user.is_superuser:
        return True
    
    # Check group permissions
    if user.groups.filter(name__in=['Letter Admin', 'Village Admin']).exists():
        return True
    
    # Check specific permissions
    content_type = ContentType.objects.get_for_model(Letter)
    permission = Permission.objects.filter(
        content_type=content_type,
        codename=permission_name
    ).first()
    
    if permission and user.has_perm(f'letters.{permission_name}'):
        return True
    
    # Check if user is the creator of the letter
    if letter and hasattr(letter, 'created_by') and letter.created_by == user:
        return True
    
    return False

def require_letter_permission(permission_name):
    """Decorator to require specific letter permission"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            letter_id = kwargs.get('letter_id')
            letter = None
            if letter_id:
                letter = get_object_or_404(Letter, id=letter_id)
            
            if not has_letter_permission(request.user, permission_name, letter):
                raise PermissionDenied("You don't have permission to perform this action.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def get_user_accessible_letters(user):
    """Get letters accessible by user based on their role"""
    if user.is_superuser or user.groups.filter(name__in=['Letter Admin', 'Village Admin']).exists():
        return Letter.objects.all()
    
    # Regular users can only see their own letters
    return Letter.objects.filter(created_by=user)

def cache_letter_stats(cache_key, calculation_func, timeout=300):
    """Cache letter statistics with timeout"""
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    result = calculation_func()
    cache.set(cache_key, result, timeout)
    return result

# Public Views untuk Layanan Desa

def document_services(request):
    """Halaman daftar layanan dokumen desa"""
    # Ambil semua jenis surat yang aktif
    document_types = LetterType.objects.filter(is_active=True).order_by('name')
    
    # Filter berdasarkan pencarian
    search_query = request.GET.get('search', '')
    if search_query:
        document_types = document_types.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(document_types, 12)  # 12 layanan per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Layanan Dokumen Desa',
        'document_types': page_obj,
        'search_query': search_query,
        'total_services': document_types.count(),
    }
    
    return render(request, 'Layanan/document_services.html', context)

def document_info(request, document_type_id):
    """Halaman informasi detail dokumen"""
    document_type = get_object_or_404(LetterType, id=document_type_id, is_active=True)
    
    # Ambil dokumen yang diperlukan sebagai list
    required_docs = []
    if document_type.required_documents:
        required_docs = [doc.strip() for doc in document_type.required_documents.split(',') if doc.strip()]
    
    # Statistik penggunaan
    total_requests = Letter.objects.filter(letter_type=document_type).count()
    completed_requests = Letter.objects.filter(
        letter_type=document_type, 
        status='completed'
    ).count()
    
    context = {
        'page_title': f'Informasi {document_type.name}',
        'document_type': document_type,
        'required_documents': required_docs,
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'success_rate': round((completed_requests / total_requests * 100) if total_requests > 0 else 0, 1),
    }
    
    return render(request, 'Layanan/document_info.html', context)

def document_request(request, document_type_id=None):
    """Halaman pengajuan dokumen"""
    document_type = None
    if document_type_id:
        document_type = get_object_or_404(LetterType, id=document_type_id, is_active=True)
    
    if request.method == 'POST':
        return handle_document_request_submission(request, document_type)
    
    # Ambil semua jenis dokumen untuk dropdown
    document_types = LetterType.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_title': 'Pengajuan Dokumen' + (f' - {document_type.name}' if document_type else ''),
        'document_type': document_type,
        'document_types': document_types,
    }
    
    return render(request, 'Layanan/document_request.html', context)

def handle_document_request_submission(request, document_type):
    """Handle form submission untuk pengajuan dokumen"""
    try:
        # Ambil data dari form
        nik = request.POST.get('nik')
        subject = request.POST.get('subject')
        purpose = request.POST.get('purpose')
        content = request.POST.get('content', '')
        
        # Validasi NIK dan cari penduduk
        try:
            applicant = Penduduk.objects.get(nik=nik)
        except Penduduk.DoesNotExist:
            messages.error(request, 'NIK tidak ditemukan dalam database penduduk.')
            return redirect('letters:document_request', document_type_id=document_type.id if document_type else None)
        
        # Jika document_type tidak ada, ambil dari form
        if not document_type:
            document_type_id = request.POST.get('document_type')
            document_type = get_object_or_404(LetterType, id=document_type_id, is_active=True)
        
        # Buat user dummy untuk created_by (nanti bisa diganti dengan sistem auth yang proper)
        admin_user, created = User.objects.get_or_create(
            username='system_admin',
            defaults={
                'email': 'admin@pulosarok.go.id',
                'first_name': 'System',
                'last_name': 'Admin'
            }
        )
        
        # Buat letter request
        letter = Letter.objects.create(
            letter_type=document_type,
            applicant=applicant,
            subject=subject,
            content=content or f'Permohonan {document_type.name}',
            purpose=purpose,
            status='submitted',
            submission_date=timezone.now(),
            created_by=admin_user
        )
        
        # Buat tracking record
        LetterTracking.objects.create(
            letter=letter,
            action='submitted',
            description=f'Permohonan {document_type.name} diajukan oleh {applicant.name}',
            performed_by=admin_user,
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, f'Permohonan {document_type.name} berhasil diajukan. Nomor tracking: {letter.letter_number or letter.id}')
        return redirect('letters:request_status')
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('letters:document_request', document_type_id=document_type.id if document_type else None)

def request_status(request):
    """Halaman cek status permohonan"""
    letter = None
    tracking_history = []
    
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '').strip()
        nik = request.POST.get('nik', '').strip()
        
        if search_query or nik:
            # Cari berdasarkan nomor surat atau NIK
            letters_query = Letter.objects.select_related('letter_type', 'applicant')
            
            if search_query:
                letters_query = letters_query.filter(
                    Q(letter_number__icontains=search_query) |
                    Q(id__icontains=search_query)
                )
            
            if nik:
                letters_query = letters_query.filter(applicant__nik=nik)
            
            letters = letters_query.order_by('-created_at')[:10]  # Ambil 10 terakhir
            
            if letters.count() == 1:
                letter = letters.first()
                tracking_history = letter.tracking_history.all().order_by('-performed_at')
            elif letters.count() > 1:
                # Jika lebih dari 1, tampilkan list untuk dipilih
                context = {
                    'page_title': 'Status Permohonan Dokumen',
                    'letters': letters,
                    'search_query': search_query,
                    'nik': nik,
                }
                return render(request, 'Layanan/request_status.html', context)
            else:
                messages.warning(request, 'Tidak ada permohonan yang ditemukan dengan kriteria tersebut.')
    
    # Ambil statistik umum
    total_requests = Letter.objects.count()
    pending_requests = Letter.objects.filter(status__in=['submitted', 'in_review']).count()
    completed_requests = Letter.objects.filter(status='completed').count()
    
    context = {
        'page_title': 'Status Permohonan Dokumen',
        'letter': letter,
        'tracking_history': tracking_history,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
    }
    
    return render(request, 'Layanan/request_status.html', context)

def letter_detail(request, letter_id):
    """Detail surat berdasarkan ID"""
    letter = get_object_or_404(Letter, id=letter_id)
    tracking_history = letter.tracking_history.all().order_by('-performed_at')
    attachments = letter.attachments.all()
    
    context = {
        'page_title': f'Detail {letter.letter_type.name}',
        'letter': letter,
        'tracking_history': tracking_history,
        'attachments': attachments,
    }
    
    return render(request, 'Layanan/letter_detail.html', context)

# API Views untuk AJAX

@csrf_exempt
@require_http_methods(["GET"])
def api_document_types(request):
    """API untuk mendapatkan daftar jenis dokumen"""
    document_types = LetterType.objects.filter(is_active=True).values(
        'id', 'name', 'code', 'description', 'processing_time_days', 'fee_amount'
    )
    
    return JsonResponse({
        'success': True,
        'data': list(document_types)
    })

@csrf_exempt
@require_http_methods(["GET"])
def api_search_residents(request):
    """API untuk pencarian penduduk berdasarkan NIK atau nama"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 3:
        return JsonResponse({
            'success': False,
            'message': 'Query minimal 3 karakter'
        })
    
    residents = Penduduk.objects.filter(
        Q(nik__icontains=query) |
        Q(name__icontains=query)
    ).select_related('dusun', 'lorong')[:10]  # Limit 10 hasil
    
    data = []
    for resident in residents:
        data.append({
            'id': resident.id,
            'nik': resident.nik,
            'name': resident.name,
            'gender': resident.get_gender_display(),
            'birth_date': resident.birth_date.strftime('%Y-%m-%d') if resident.birth_date else '',
            'age': resident.age if hasattr(resident, 'age') else '',
            'address': resident.address or '',
            'dusun': resident.dusun.name if resident.dusun else '',
            'lorong': resident.lorong.name if resident.lorong else '',
            'phone_number': resident.phone_number or '',
            'full_address': f"{resident.address}, {resident.dusun.name if resident.dusun else ''}, {resident.lorong.name if resident.lorong else ''}".strip(', ')
        })
    
    return JsonResponse({
        'success': True,
        'data': data
    })

@csrf_exempt
@require_http_methods(["POST"])
def api_submit_request(request):
    """API untuk submit permohonan dokumen"""
    try:
        data = json.loads(request.body)
        
        # Validasi data
        required_fields = ['document_type_id', 'nik', 'subject', 'purpose']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Field {field} wajib diisi'
                })
        
        # Cari document type dan applicant
        document_type = get_object_or_404(LetterType, id=data['document_type_id'], is_active=True)
        applicant = get_object_or_404(Penduduk, nik=data['nik'])
        
        # Buat user admin jika belum ada
        admin_user, created = User.objects.get_or_create(
            username='system_admin',
            defaults={
                'email': 'admin@pulosarok.go.id',
                'first_name': 'System',
                'last_name': 'Admin'
            }
        )
        
        # Buat letter
        letter = Letter.objects.create(
            letter_type=document_type,
            applicant=applicant,
            subject=data['subject'],
            content=data.get('content', f'Permohonan {document_type.name}'),
            purpose=data['purpose'],
            status='submitted',
            submission_date=timezone.now(),
            created_by=admin_user
        )
        
        # Buat tracking
        LetterTracking.objects.create(
            letter=letter,
            action='submitted',
            description=f'Permohonan {document_type.name} diajukan melalui API',
            performed_by=admin_user,
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Permohonan berhasil diajukan',
            'data': {
                'letter_id': letter.id,
                'letter_number': letter.letter_number or str(letter.id),
                'status': letter.status
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def api_request_status(request):
    """API untuk cek status permohonan"""
    query = request.GET.get('q', '').strip()
    nik = request.GET.get('nik', '').strip()
    
    if not query and not nik:
        return JsonResponse({
            'success': False,
            'message': 'Parameter q (nomor surat) atau nik diperlukan'
        })
    
    letters_query = Letter.objects.select_related('letter_type', 'applicant')
    
    if query:
        letters_query = letters_query.filter(
            Q(letter_number__icontains=query) |
            Q(id__icontains=query)
        )
    
    if nik:
        letters_query = letters_query.filter(applicant__nik=nik)
    
    letters = letters_query.order_by('-created_at')[:10]
    
    data = []
    for letter in letters:
        tracking = letter.tracking_history.all().order_by('-performed_at')
        data.append({
            'id': letter.id,
            'letter_number': letter.letter_number or str(letter.id),
            'document_type': letter.letter_type.name,
            'applicant_name': letter.applicant.nama,
            'applicant_nik': letter.applicant.nik,
            'subject': letter.subject,
            'status': letter.status,
            'submission_date': letter.submission_date.isoformat() if letter.submission_date else None,
            'tracking_history': [{
                'action': t.action,
                'description': t.description,
                'performed_at': t.performed_at.isoformat(),
                'performed_by': t.performed_by.get_full_name() or t.performed_by.username
            } for t in tracking[:5]]  # 5 tracking terakhir
        })
    
    return JsonResponse({
        'success': True,
        'data': data
    })

# Chat Integration Views

def chat_layanan(request):
    """Halaman chat untuk layanan desa"""
    context = {
        'page_title': 'Chat Layanan Desa',
    }
    return render(request, 'public/layanan/chat_layanan.html', context)

@csrf_exempt
@require_http_methods(["POST"])
# Rate limiter removed - not needed
def api_chat_message(request):
    """API untuk mengirim pesan chat dengan Groq AI dan form handling"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id', None)
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Pesan tidak boleh kosong'
            }, status=400)
        
        # Generate session_id jika belum ada
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        # Input validation removed - not needed
        
        # Generate response menggunakan Groq API dengan form handling
        # Groq service removed
        
        groq_service = GroqChatService()
        if groq_service.is_available():
            # Gunakan Groq API dengan session_id untuk form handling
            response_data = groq_service.get_enhanced_response(message, session_id=session_id)
            response = response_data.get('content', 'Maaf, terjadi kesalahan dalam memproses pesan Anda.')
            form_active = response_data.get('form_active', False)
            form_type = response_data.get('form_type', None)
        else:
            # Fallback ke chatbot sederhana
            print("Groq API fallback: API tidak tersedia atau terjadi kesalahan")
            response = generate_chat_response(message)
            form_active = False
            form_type = None
        
        return JsonResponse({
            'success': True,
            'response': response,
            'session_id': session_id,
            'form_active': form_active,
            'form_type': form_type
        })
        
    except Exception as e:
        print(f"Error in api_chat_message: {e}")
        # Fallback ke chatbot sederhana jika terjadi error
        try:
            response = generate_chat_response(message)
            return JsonResponse({
                'success': True,
                'response': response,
                'session_id': session_id if 'session_id' in locals() else None,
                'form_active': False,
                'form_type': None
            })
        except:
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            })

# Helper Functions

def get_client_ip(request):
    """Mendapatkan IP address client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_chat_response(message):
    """Generate response untuk chatbot layanan desa"""
    message_lower = message.lower()
    
    # Responses berdasarkan keyword
    if any(word in message_lower for word in ['halo', 'hai', 'hello', 'selamat']):
        return "Halo! Selamat datang di layanan chat Desa Pulosarok. Ada yang bisa saya bantu mengenai layanan dokumen desa?"
    
    elif any(word in message_lower for word in ['mengadu', 'adu', 'pengaduan', 'lapor', 'komplain']):
        return "Untuk pengaduan atau laporan, silakan kunjungi halaman Pengaduan di website kami atau hubungi langsung kantor desa. Namun jika Anda membutuhkan dokumen untuk keperluan pengaduan, saya bisa membantu menjelaskan prosedurnya."
    
    elif any(word in message_lower for word in ['dokumen', 'surat', 'layanan']):
        return "Kami menyediakan berbagai layanan dokumen desa seperti:\n- Surat Keterangan Domisili\n- Surat Keterangan Usaha\n- Surat Pengantar\n- Dan masih banyak lagi\n\nApakah ada dokumen tertentu yang Anda butuhkan?"
    
    elif any(word in message_lower for word in ['cara', 'bagaimana', 'prosedur']):
        return "Untuk mengajukan dokumen, Anda bisa:\n1. Kunjungi halaman Layanan Dokumen\n2. Pilih jenis dokumen yang dibutuhkan\n3. Isi formulir pengajuan\n4. Upload dokumen pendukung jika diperlukan\n5. Submit permohonan\n\nApakah ada yang ingin ditanyakan lebih lanjut?"
    
    elif any(word in message_lower for word in ['status', 'cek', 'tracking']):
        return "Untuk mengecek status permohonan Anda:\n1. Kunjungi halaman Status Permohonan\n2. Masukkan nomor tracking atau NIK\n3. Klik Cari\n\nAnda akan melihat status terkini dari permohonan dokumen Anda."
    
    elif any(word in message_lower for word in ['biaya', 'tarif', 'gratis']):
        return "Sebagian besar layanan dokumen desa kami gratis. Namun untuk dokumen tertentu mungkin ada biaya administrasi. Anda bisa melihat detail biaya di halaman informasi masing-masing dokumen."
    
    elif any(word in message_lower for word in ['waktu', 'lama', 'proses']):
        return "Waktu pemrosesan dokumen bervariasi tergantung jenis dokumen:\n- Dokumen sederhana: 1-3 hari kerja\n- Dokumen kompleks: 3-7 hari kerja\n\nWaktu pasti bisa dilihat di halaman informasi masing-masing dokumen."
    
    elif any(word in message_lower for word in ['terima kasih', 'thanks', 'makasih']):
        return "Sama-sama! Senang bisa membantu Anda. Jika ada pertanyaan lain mengenai layanan desa, jangan ragu untuk bertanya."
    
    else:
        return "Maaf, saya belum memahami pertanyaan Anda. Bisa tolong dijelaskan lebih detail? Atau Anda bisa menanyakan tentang:\n- Jenis dokumen yang tersedia\n- Cara mengajukan dokumen\n- Status permohonan\n- Biaya layanan\n- Waktu pemrosesan"


# ===========================
# ADMIN DASHBOARD VIEWS
# ===========================

@staff_member_required
def admin_dashboard(request):
    """Dashboard admin untuk manajemen dokumen surat dengan role-based access control"""
    # Get letters based on user role
    user_letters = get_user_accessible_letters(request.user)
    
    # Cache dashboard statistics
    def get_dashboard_stats():
        # Statistik umum
        total_letters = user_letters.count()
        pending_letters = user_letters.filter(status__in=['draft', 'submitted', 'in_review']).count()
        completed_letters = user_letters.filter(status='completed').count()
        rejected_letters = user_letters.filter(status='rejected').count()
        
        # Statistik bulanan
        current_month = timezone.now().replace(day=1)
        monthly_letters = user_letters.filter(created_at__gte=current_month).count()
        
        return {
            'total_letters': total_letters,
            'pending_letters': pending_letters,
            'completed_letters': completed_letters,
            'rejected_letters': rejected_letters,
            'monthly_letters': monthly_letters,
            'completion_rate': round((completed_letters / total_letters * 100) if total_letters > 0 else 0, 1)
        }
    
    stats = cache_letter_stats(f'dashboard_stats_{request.user.id}', get_dashboard_stats)
    
    # Jenis surat paling populer (based on user accessible letters)
    popular_letter_types = LetterType.objects.filter(
        letter__in=user_letters
    ).annotate(
        letter_count=Count('letter')
    ).order_by('-letter_count')[:5]
    
    # Surat yang perlu perhatian (pending > 3 hari)
    urgent_letters = user_letters.filter(
        status__in=['submitted', 'in_review'],
        submission_date__lt=timezone.now() - timedelta(days=3)
    ).select_related('letter_type', 'applicant').order_by('submission_date')[:10]
    
    # AI Validation Statistics (only for accessible letters)
    current_month = timezone.now().replace(day=1)
    ai_validations = LetterAIValidation.objects.filter(
        letter__in=user_letters,
        created_at__gte=current_month
    ).aggregate(
        total=Count('id'),
        avg_confidence=Avg('confidence_score')
    )
    
    # Recent activities
    recent_activities = LetterTracking.objects.filter(
        letter__in=user_letters
    ).select_related('letter', 'performed_by').order_by('-performed_at')[:10]
    
    context = {
        'page_title': 'Dashboard Admin - Manajemen Dokumen Surat',
        'stats': stats,
        'popular_letter_types': popular_letter_types,
        'urgent_letters': urgent_letters,
        'ai_validations': ai_validations,
        'recent_activities': recent_activities,
        'user_role': 'Admin' if request.user.groups.filter(name__in=['Letter Admin', 'Village Admin']).exists() else 'User',
        'can_manage_all': has_letter_permission(request.user, 'change_letter'),
        'can_view_analytics': has_letter_permission(request.user, 'view_letter'),
    }
    
    return render(request, 'letters/admin/dashboard.html', context)

@staff_member_required
def admin_letter_list(request):
    """Daftar semua surat untuk admin dengan role-based access control"""
    # Get letters based on user role
    letters = get_user_accessible_letters(request.user).select_related(
        'letter_type', 'applicant', 'applicant__dusun', 'created_by'
    ).order_by('-created_at')
    
    # Filter berdasarkan status
    status_filter = request.GET.get('status')
    if status_filter:
        letters = letters.filter(status=status_filter)
    
    # Filter berdasarkan jenis surat
    type_filter = request.GET.get('type')
    if type_filter:
        letters = letters.filter(letter_type_id=type_filter)
    
    # Filter berdasarkan dusun (untuk admin dusun)
    dusun_filter = request.GET.get('dusun')
    if dusun_filter:
        letters = letters.filter(applicant__dusun_id=dusun_filter)
    
    # Pencarian
    search_query = request.GET.get('search')
    if search_query:
        letters = letters.filter(
            Q(letter_number__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(applicant__name__icontains=search_query) |
            Q(applicant__nik__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(letters, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Data untuk filter
    letter_types = LetterType.objects.filter(is_active=True)
    status_choices = Letter.STATUS_CHOICES
    dusun_list = Dusun.objects.filter(is_active=True).order_by('name')
    
    # Cache statistics for performance
    def get_letter_stats():
        return {
            'total_letters': letters.count(),
            'pending_count': letters.filter(status__in=['draft', 'submitted', 'in_review']).count(),
            'completed_count': letters.filter(status='completed').count(),
        }
    
    stats = cache_letter_stats(f'letter_stats_{request.user.id}', get_letter_stats)
    
    context = {
        'page_title': 'Manajemen Surat',
        'letters': page_obj,
        'letter_types': letter_types,
        'status_choices': status_choices,
        'dusun_list': dusun_list,
        'current_status': status_filter,
        'current_type': type_filter,
        'current_dusun': dusun_filter,
        'search_query': search_query,
        'stats': stats,
        'can_create_letter': has_letter_permission(request.user, 'add_letter'),
        'can_edit_all': has_letter_permission(request.user, 'change_letter'),
    }
    
    return render(request, 'letters/admin/letter_list.html', context)

@staff_member_required
def admin_letter_detail(request, letter_id):
    """Detail surat untuk admin dengan fitur editing"""
    letter = get_object_or_404(Letter, id=letter_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            notes = request.POST.get('notes', '')
            
            if new_status in dict(Letter.STATUS_CHOICES):
                old_status = letter.status
                letter.status = new_status
                letter.save()
                
                # Create tracking record
                LetterTracking.objects.create(
                    letter=letter,
                    action=new_status,
                    description=f'Status diubah dari {old_status} ke {new_status}',
                    performed_by=request.user,
                    notes=notes,
                    ip_address=get_client_ip(request)
                )
                
                messages.success(request, f'Status surat berhasil diubah ke {letter.get_status_display()}')
                return redirect('letters:admin_letter_detail', letter_id=letter.id)
        
        elif action == 'validate':
            # Basic validation without AI
            validation_service = LetterValidationService()
            validation_result = validation_service.validate_letter(
                letter.content, 
                letter.letter_type.name if letter.letter_type else None
            )
            
            messages.success(request, 'Validasi surat berhasil dilakukan')
            return redirect('letters:admin_letter_detail', letter_id=letter.id)
    
    # Get tracking history
    tracking_history = letter.tracking_history.all().order_by('-performed_at')
    
    # Get validation if exists (removed AI validation)
    validation = None
    
    # Get recipients
    recipients = letter.recipients.all()
    
    context = {
        'page_title': f'Detail Surat - {letter.subject}',
        'letter': letter,
        'tracking_history': tracking_history,
        'validation': validation,
        'recipients': recipients,
        'status_choices': Letter.STATUS_CHOICES,
    }
    
    return render(request, 'letters/admin/letter_detail.html', context)

@staff_member_required
def admin_letter_create(request):
    """Buat surat baru oleh admin"""
    if request.method == 'POST':
        form = LetterForm(request.POST)
        if form.is_valid():
            letter = form.save(commit=False)
            letter.created_by = request.user
            letter.save()
            
            # Create tracking record
            LetterTracking.objects.create(
                letter=letter,
                action='created',
                description='Surat dibuat oleh admin',
                performed_by=request.user,
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Surat berhasil dibuat')
            return redirect('letters:admin_letter_detail', letter_id=letter.id)
    else:
        form = LetterForm()
    
    context = {
        'page_title': 'Buat Surat Baru',
        'form': form,
    }
    
    return render(request, 'letters/admin/letter_create.html', context)

@staff_member_required
def admin_letter_edit(request, letter_id):
    """Edit surat oleh admin"""
    letter = get_object_or_404(Letter, id=letter_id)
    
    if request.method == 'POST':
        form = LetterForm(request.POST, instance=letter)
        if form.is_valid():
            form.save()
            
            # Create tracking record
            LetterTracking.objects.create(
                letter=letter,
                action='updated',
                description='Surat diperbarui oleh admin',
                performed_by=request.user,
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Surat berhasil diperbarui')
            return redirect('letters:admin_letter_detail', letter_id=letter.id)
    else:
        form = LetterForm(instance=letter)
    
    context = {
        'page_title': f'Edit Surat - {letter.subject}',
        'form': form,
        'letter': letter,
    }
    
    return render(request, 'letters/admin/letter_edit.html', context)

@staff_member_required
def admin_template_list(request):
    """Daftar template surat untuk admin"""
    templates = LetterTemplate.objects.all().order_by('-created_at')
    
    # Pencarian
    search_query = request.GET.get('search')
    if search_query:
        templates = templates.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(templates, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Manajemen Template Surat',
        'templates': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'letters/admin/template_list.html', context)

@staff_member_required
def admin_letter_analytics(request):
    """Analytics surat untuk admin"""
    # Letter Statistics
    total_letters = Letter.objects.count()
    draft_letters = Letter.objects.filter(status='draft').count()
    sent_letters = Letter.objects.filter(status='sent').count()
    approved_letters = Letter.objects.filter(status='approved').count()
    
    # Monthly letter usage
    current_month = timezone.now().replace(day=1)
    monthly_letters = Letter.objects.filter(
        created_at__gte=current_month
    ).count()
    
    # Recent letters
    recent_letters = Letter.objects.select_related(
        'applicant', 'letter_type'
    ).order_by('-created_at')[:10]
    
    context = {
        'page_title': 'Analytics Surat',
        'total_letters': total_letters,
        'draft_letters': draft_letters,
        'sent_letters': sent_letters,
        'approved_letters': approved_letters,
        'monthly_letters': monthly_letters,
        'recent_letters': recent_letters,
    }
    
    return render(request, 'letters/admin/letter_analytics.html', context)

# ===========================
# AJAX ENDPOINTS FOR ADMIN
# ===========================

# AI endpoints removed

# AI template generation removed