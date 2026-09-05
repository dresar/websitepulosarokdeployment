from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import json
import re
import uuid
from .models import (
    Complaint, ComplaintCategory, ComplaintUpdate, 
    ChatSession, ChatMessage, ChatIntent, ChatPattern, ChatResponse,
    Notification, Contact, ComplaintVerification
)
from .forms import ComplaintForm, ComplaintTrackingForm, ChatMessageForm, ContactForm
# SimpleChatBot removed - using simple AI function instead

def get_simple_ai_response(message):
    """AI sederhana untuk chat"""
    message_lower = message.lower()
    
    # Greeting responses
    if any(word in message_lower for word in ['halo', 'hai', 'selamat', 'assalamualaikum']):
        return "Halo! Selamat datang di layanan pengaduan Desa Pulosarok. Ada yang bisa saya bantu?"
    
    # Complaint related
    if any(word in message_lower for word in ['pengaduan', 'laporan', 'komplain', 'aduan', 'keluhan']):
        return "Untuk membuat pengaduan, silakan isi formulir di website atau datang langsung ke kantor desa. Pastikan menyertakan data lengkap dan bukti jika ada."
    
    # Status check
    if any(word in message_lower for word in ['status', 'cek', 'lacak', 'perkembangan']):
        return "Untuk mengecek status pengaduan, gunakan menu 'Lacak Pengaduan' dengan memasukkan ID pengaduan dan email yang Anda gunakan saat membuat laporan."
    
    # Contact info
    if any(word in message_lower for word in ['kontak', 'telepon', 'alamat', 'jam buka', 'kantor']):
        return "Kantor Desa Pulosarok buka Senin-Jumat 08:00-16:00, Sabtu 08:00-12:00. Telepon: (0274) 123-4567. Alamat: Jl. Desa Pulosarok No. 1, Kec. Pulosarok, Kab. Bantul."
    
    # Help
    if any(word in message_lower for word in ['bantuan', 'help', 'tolong', 'cara', 'bagaimana']):
        return "Saya bisa membantu Anda dengan: 1) Cara membuat pengaduan, 2) Melacak status pengaduan, 3) Informasi kontak desa, 4) Panduan penggunaan website. Apa yang ingin Anda ketahui?"
    
    # Thanks
    if any(word in message_lower for word in ['terima kasih', 'makasih', 'thanks', 'thank you']):
        return "Sama-sama! Senang bisa membantu Anda. Jika ada pertanyaan lain, jangan ragu untuk bertanya."
    
    # Goodbye
    if any(word in message_lower for word in ['selamat tinggal', 'bye', 'sampai jumpa', 'dadah']):
        return "Selamat tinggal! Terima kasih telah menggunakan layanan pengaduan Desa Pulosarok."
    
    # Default response
    return "Maaf, saya tidak mengerti pertanyaan Anda. Bisakah Anda menjelaskan lebih detail? Atau coba tanyakan tentang cara membuat pengaduan, mengecek status, atau informasi kontak desa."

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff
# Rate limiter removed - not needed
# Input validator removed - not needed
from django.core.exceptions import ValidationError


def complaint_form_view(request):
    """View untuk menampilkan dan memproses formulir pengaduan"""
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save()
            
            # Kirim notifikasi email ke pelapor
            send_complaint_notification(complaint, 'new')
            
            # Kirim notifikasi ke admin
            send_admin_notification(complaint, 'new')
            
            messages.success(request, f'Pengaduan berhasil dikirim! ID Pengaduan Anda: {complaint.complaint_id}')
            return redirect('complaints:complaint_success', complaint_id=complaint.complaint_id)
        else:
            messages.error(request, 'Terjadi kesalahan dalam pengisian form. Silakan periksa kembali.')
    else:
        form = ComplaintForm()
    
    categories = ComplaintCategory.objects.filter(is_active=True)
    context = {
        'form': form,
        'categories': categories,
        'page_title': 'Formulir Pengaduan'
    }
    return render(request, 'public/complaints/complaint_form.html', context)


def complaint_success_view(request, complaint_id):
    """View untuk menampilkan halaman sukses setelah pengaduan dikirim"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    context = {
        'complaint': complaint,
        'page_title': 'Pengaduan Berhasil Dikirim'
    }
    return render(request, 'public/complaints/complaint_success.html', context)


def complaint_tracking_view(request):
    """View untuk tracking status pengaduan"""
    complaint = None
    if request.method == 'POST':
        form = ComplaintTrackingForm(request.POST)
        if form.is_valid():
            complaint_id = form.cleaned_data['complaint_id']
            reporter_email = form.cleaned_data['reporter_email']
            
            try:
                complaint = Complaint.objects.get(
                    complaint_id=complaint_id,
                    reporter_email=reporter_email
                )
            except Complaint.DoesNotExist:
                messages.error(request, 'Pengaduan tidak ditemukan. Periksa kembali ID dan email Anda.')
    else:
        form = ComplaintTrackingForm()
    
    context = {
        'form': form,
        'complaint': complaint,
        'page_title': 'Lacak Status Pengaduan'
    }
    return render(request, 'public/complaints/complaint_tracking.html', context)


def complaint_list_view(request):
    """View untuk menampilkan daftar pengaduan (untuk admin)"""
    complaints = Complaint.objects.all().order_by('-created_at')
    
    # Filter berdasarkan parameter GET
    status = request.GET.get('status')
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if status:
        complaints = complaints.filter(status=status)
    
    if category:
        complaints = complaints.filter(category_id=category)
    
    if search:
        complaints = complaints.filter(
            Q(title__icontains=search) |
            Q(reporter_name__icontains=search) |
            Q(complaint_id__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(complaints, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ComplaintCategory.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_status': status,
        'current_category': category,
        'current_search': search,
        'page_title': 'Daftar Pengaduan'
    }
    return render(request, 'public/complaints/complaint_list.html', context)


def complaint_detail_view(request, complaint_id):
    """View untuk menampilkan detail pengaduan"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    updates = complaint.updates.all().order_by('-created_at')
    
    context = {
        'complaint': complaint,
        'updates': updates,
        'page_title': f'Detail Pengaduan {complaint.complaint_id}'
    }
    return render(request, 'public/complaints/complaint_detail.html', context)


# Chat System Views
@csrf_exempt
@require_http_methods(["POST"])
def chat_start_session(request):
    """API untuk memulai sesi chat baru"""
    try:
        data = json.loads(request.body)
        user_name = data.get('user_name', '')
        user_email = data.get('user_email', '')
        
        session = ChatSession.objects.create(
            user_name=user_name,
            user_email=user_email
        )
        
        # Kirim pesan selamat datang
        welcome_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content='Halo! Selamat datang di layanan pengaduan Desa Pulosarok. Bagaimana saya bisa membantu Anda hari ini?'
        )
        
        return JsonResponse({
            'success': True,
            'session_id': str(session.session_id),
            'welcome_message': welcome_message.content
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def contact_view(request):
    """View untuk menampilkan dan memproses formulir kontak"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            
            # Kirim notifikasi email ke pengirim
            send_contact_notification(contact, 'new')
            
            # Kirim notifikasi ke admin
            send_contact_admin_notification(contact, 'new')
            
            messages.success(request, f'Pesan berhasil dikirim! ID Pesan Anda: {contact.contact_id}')
            return redirect('complaints:contact_success', contact_id=contact.contact_id)
        else:
            messages.error(request, 'Terjadi kesalahan dalam pengisian form. Silakan periksa kembali.')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'page_title': 'Hubungi Kami'
    }
    return render(request, 'public/complaints/contact.html', context)


def contact_success_view(request, contact_id):
    """View untuk menampilkan halaman sukses setelah mengirim pesan kontak"""
    contact = get_object_or_404(Contact, contact_id=contact_id)
    context = {
        'contact': contact,
        'page_title': 'Pesan Berhasil Dikirim'
    }
    return render(request, 'public/complaints/contact_success.html', context)


def send_contact_notification(contact, notification_type):
    """Kirim notifikasi email ke pengirim pesan kontak"""
    try:
        if not contact.is_anonymous and contact.sender_email:
            subject = f'Konfirmasi Pesan Kontak - {contact.contact_id}'
            
            if notification_type == 'new':
                message = f"""
                Terima kasih telah menghubungi kami!
                
                Detail pesan Anda:
                ID Pesan: {contact.contact_id}
                Nama: {contact.sender_name}
                Email: {contact.sender_email}
                Jenis Pesan: {contact.get_subject_type_display()}
                Subjek: {contact.subject}
                
                Pesan Anda telah kami terima dan akan segera ditindaklanjuti.
                
                Terima kasih atas kepercayaan Anda.
                
                Salam,
                Tim Website Desa Pulosarok
                """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [contact.sender_email],
                fail_silently=True,
            )
    except Exception as e:
        print(f"Error sending contact notification: {e}")


def send_contact_admin_notification(contact, notification_type):
    """Kirim notifikasi email ke admin tentang pesan kontak baru"""
    try:
        admin_emails = getattr(settings, 'ADMIN_EMAIL_LIST', ['admin@pulosarok.com'])
        
        if notification_type == 'new':
            subject = f'Pesan Kontak Baru - {contact.contact_id}'
            message = f"""
            Pesan kontak baru telah diterima:
            
            ID Pesan: {contact.contact_id}
            Nama Pengirim: {contact.display_sender_name}
            Email: {contact.sender_email if not contact.is_anonymous else 'Anonim'}
            Telepon: {contact.sender_phone or 'Tidak ada'}
            Jenis Pesan: {contact.get_subject_type_display()}
            Subjek: {contact.subject}
            
            Pesan:
            {contact.message}
            
            Status: {contact.get_status_display()}
            Tanggal: {contact.created_at.strftime('%d/%m/%Y %H:%M')}
            
            Silakan login ke admin panel untuk menindaklanjuti.
            """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending admin contact notification: {e}")


@csrf_exempt
@require_http_methods(["POST"])
# Rate limiter removed - not needed
def chat_send_message(request):
    """API untuk mengirim pesan chat"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        message_content = data.get('message', '').strip()
        
        if not session_id or not message_content:
            return JsonResponse({
                'success': False,
                'error': 'Session ID dan pesan diperlukan'
            }, status=400)
        
        # Input validation removed - not needed
        
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Simpan pesan user
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message_content
        )
        
        # Generate response menggunakan AI sederhana
        bot_response = get_simple_ai_response(message_content)
        
        # Simpan response bot
        bot_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=bot_response
        )
        
        # Update session timestamp
        session.updated_at = timezone.now()
        session.save()
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'content': user_message.content,
                'timestamp': user_message.created_at.isoformat()
            },
            'bot_response': {
                'content': bot_message.content,
                'timestamp': bot_message.created_at.isoformat()
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET"])
def chat_get_messages(request, session_id):
    """API untuk mengambil riwayat pesan chat"""
    try:
        session = get_object_or_404(ChatSession, session_id=session_id)
        messages = session.messages.all().order_by('created_at')
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def chat_modal_view(request):
    """View untuk menampilkan modal chat"""
    return render(request, 'public/complaints/chat_modal.html')


# Utility Functions
def send_complaint_notification(complaint, notification_type):
    """Kirim notifikasi email ke pelapor"""
    try:
        if notification_type == 'new':
            subject = f'Pengaduan Anda Telah Diterima - ID: {complaint.complaint_id}'
            template = 'complaints/emails/complaint_received.html'
        elif notification_type == 'update':
            subject = f'Update Pengaduan - ID: {complaint.complaint_id}'
            template = 'complaints/emails/complaint_updated.html'
        elif notification_type == 'resolved':
            subject = f'Pengaduan Selesai - ID: {complaint.complaint_id}'
            template = 'complaints/emails/complaint_resolved.html'
        else:
            return
        
        context = {'complaint': complaint}
        html_message = render_to_string(template, context)
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[complaint.reporter_email],
            html_message=html_message,
            fail_silently=True
        )
        
        # Simpan notifikasi ke database
        Notification.objects.create(
            notification_type=f'complaint_{notification_type}',
            title=subject,
            message=html_message,
            recipient_email=complaint.reporter_email,
            complaint=complaint,
            is_sent=True,
            sent_at=timezone.now()
        )
        
    except Exception as e:
        print(f"Error sending notification: {e}")


def send_admin_notification(complaint, notification_type):
    """Kirim notifikasi ke admin"""
    try:
        admin_emails = getattr(settings, 'ADMIN_EMAILS', ['admin@pulosarok.go.id'])
        
        if notification_type == 'new':
            subject = f'Pengaduan Baru - {complaint.title}'
            message = f'Pengaduan baru telah diterima dari {complaint.reporter_name}.\n\nID: {complaint.complaint_id}\nKategori: {complaint.category}\nJudul: {complaint.title}'
        
        for email in admin_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True
            )
    
    except Exception as e:
        print(f"Error sending admin notification: {e}")


# API Views untuk AJAX
@require_http_methods(["GET"])
def api_complaint_stats(request):
    """API untuk statistik pengaduan"""
    try:
        stats = {
            'total': Complaint.objects.count(),
            'pending': Complaint.objects.filter(status='pending').count(),
            'in_review': Complaint.objects.filter(status='in_review').count(),
            'in_progress': Complaint.objects.filter(status='in_progress').count(),
            'resolved': Complaint.objects.filter(status='resolved').count(),
            'rejected': Complaint.objects.filter(status='rejected').count(),
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET"])
def api_categories(request):
    """API untuk mendapatkan daftar kategori"""
    try:
        categories = ComplaintCategory.objects.filter(is_active=True).values('id', 'name', 'description')
        
        return JsonResponse({
            'success': True,
            'categories': list(categories)
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# Admin Views
from django.contrib.auth.decorators import login_required

@login_required
def complaints_list(request):
    """View untuk menampilkan daftar pengaduan admin"""
    complaints = Complaint.objects.all().order_by('-created_at')
    
    # Filter berdasarkan status jika ada
    status_filter = request.GET.get('status')
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(complaints, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'complaints': page_obj,
        'status_choices': Complaint.STATUS_CHOICES,
        'current_status': status_filter,
    }
    return render(request, 'pulosarok/admin/complaints/list.html', context)

@login_required
def category_list(request):
    """View untuk menampilkan daftar kategori pengaduan"""
    categories = ComplaintCategory.objects.all().order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'pulosarok/admin/complaints/categories.html', context)

@login_required
def complaints_dashboard(request):
    """View untuk dashboard pengaduan admin"""
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='pending').count()
    resolved_complaints = Complaint.objects.filter(status='resolved').count()
    
    recent_complaints = Complaint.objects.order_by('-created_at')[:10]
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'recent_complaints': recent_complaints,
    }
    return render(request, 'pulosarok/admin/complaints/dashboard.html', context)


# ==================== ADMIN PANEL INTEGRATION ====================

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Avg, Sum, Max, Min
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from core.models import CustomUser
# from references.models import Penduduk  # COMMENTED OUT - references app disabled
# Using letters app models instead
try:
    from letters.models import Penduduk
except ImportError:
    Penduduk = None

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser

# ==================== ADMIN DASHBOARD ====================

@login_required
@user_passes_test(is_admin)
def admin_complaints_dashboard(request):
    """Admin dashboard for complaints management"""
    # Basic statistics
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='pending').count()
    in_review_complaints = Complaint.objects.filter(status='in_review').count()
    in_progress_complaints = Complaint.objects.filter(status='in_progress').count()
    resolved_complaints = Complaint.objects.filter(status='resolved').count()
    rejected_complaints = Complaint.objects.filter(status='rejected').count()
    
    # Priority statistics
    low_priority_complaints = Complaint.objects.filter(priority='low').count()
    medium_priority_complaints = Complaint.objects.filter(priority='medium').count()
    high_priority_complaints = Complaint.objects.filter(priority='high').count()
    urgent_priority_complaints = Complaint.objects.filter(priority='urgent').count()
    
    # Recent complaints
    recent_complaints = Complaint.objects.select_related('category').order_by('-created_at')[:10]
    
    # Category statistics with proper field names
    category_stats = ComplaintCategory.objects.annotate(
        total_complaints=Count('complaint'),
        pending_complaints=Count('complaint', filter=Q(complaint__status='pending')),
        in_progress_complaints=Count('complaint', filter=Q(complaint__status='in_progress')),
        resolved_complaints=Count('complaint', filter=Q(complaint__status='resolved'))
    ).order_by('-total_complaints')
    
    # Recent updates
    recent_updates = ComplaintUpdate.objects.select_related('complaint', 'updated_by').order_by('-created_at')[:10]
    
    # Monthly trends (last 12 months)
    from django.db.models.functions import TruncMonth
    monthly_trends = Complaint.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=365)
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Priority distribution
    priority_stats = Complaint.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    # Average resolution time
    resolved_with_time = Complaint.objects.filter(
        status__in=['resolved', 'closed'],
        resolved_at__isnull=False
    )
    
    avg_resolution_time = None
    if resolved_with_time.exists():
        total_time = sum([
            (c.resolved_at - c.created_at).total_seconds() / 3600  # in hours
            for c in resolved_with_time
        ])
        avg_resolution_time = total_time / resolved_with_time.count()
    
    context = {
        'title': 'Dashboard Pengaduan',
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'in_review_complaints': in_review_complaints,
        'in_progress_complaints': in_progress_complaints,
        'resolved_complaints': resolved_complaints,
        'rejected_complaints': rejected_complaints,
        'low_priority_complaints': low_priority_complaints,
        'medium_priority_complaints': medium_priority_complaints,
        'high_priority_complaints': high_priority_complaints,
        'urgent_priority_complaints': urgent_priority_complaints,
        'recent_complaints': recent_complaints,
        'recent_updates': recent_updates,
        'category_stats': category_stats,
        'monthly_trends': list(monthly_trends),
        'priority_stats': list(priority_stats),
        'avg_resolution_time': avg_resolution_time,
    }
    return render(request, 'admin_panel/complaints/dashboard.html', context)

# ==================== COMPLAINT MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_complaints_list(request):
    """Admin list view for complaints"""
    complaints = Complaint.objects.select_related('category').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        complaints = complaints.filter(status=status)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        complaints = complaints.filter(category_id=category_id)
    
    # Filter by priority
    priority = request.GET.get('priority')
    if priority:
        complaints = complaints.filter(priority=priority)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        complaints = complaints.filter(created_at__gte=parse_date(start_date))
    if end_date:
        complaints = complaints.filter(created_at__lte=parse_date(end_date))
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        complaints = complaints.filter(
            Q(complaint_id__icontains=search) |
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(reporter_name__icontains=search) |
            Q(reporter_email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(complaints, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = ComplaintCategory.objects.all()
    status_choices = Complaint.STATUS_CHOICES
    priority_choices = Complaint.PRIORITY_CHOICES
    
    context = {
        'title': 'Manajemen Pengaduan',
        'complaints': page_obj,
        'categories': categories,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'current_filters': {
            'status': status,
            'category': category_id,
            'priority': priority,
            'start_date': start_date,
            'end_date': end_date,
            'search': search,
        }
    }
    return render(request, 'admin_panel/complaints/list.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_complaint_create(request):
    """Create new complaint (admin)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            complaint = Complaint.objects.create(
                title=data.get('title'),
                description=data.get('description'),
                category_id=data.get('category_id'),
                priority=data.get('priority', 'medium'),
                reporter_name=data.get('reporter_name'),
                reporter_email=data.get('reporter_email'),
                reporter_phone=data.get('reporter_phone', ''),
                location=data.get('location', ''),
                status='pending'
            )
            
            # Send notifications
            send_complaint_notification(complaint, 'new')
            send_admin_notification(complaint, 'new')
            
            return JsonResponse({
                'success': True,
                'message': 'Pengaduan berhasil ditambahkan',
                'data': {
                    'id': complaint.id,
                    'complaint_id': complaint.complaint_id,
                    'title': complaint.title,
                    'status': complaint.get_status_display()
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # GET request - return form data
    categories = ComplaintCategory.objects.filter(is_active=True)
    return JsonResponse({
        'categories': [{'id': c.id, 'name': c.name} for c in categories],
        'priority_choices': Complaint.PRIORITY_CHOICES,
    })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_complaint_update(request, pk):
    """Update complaint"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_status = complaint.status
            
            complaint.title = data.get('title', complaint.title)
            complaint.description = data.get('description', complaint.description)
            complaint.category_id = data.get('category_id', complaint.category_id)
            complaint.priority = data.get('priority', complaint.priority)
            complaint.status = data.get('status', complaint.status)
            complaint.admin_notes = data.get('admin_notes', complaint.admin_notes)
            
            # Update resolution date if status changed to resolved/closed
            if old_status != complaint.status and complaint.status in ['resolved', 'closed']:
                complaint.resolved_at = timezone.now()
            
            complaint.save()
            
            # Create update record
            ComplaintUpdate.objects.create(
                complaint=complaint,
                status=complaint.status,
                notes=data.get('update_notes', ''),
                updated_by=request.user
            )
            
            # Send notification if status changed
            if old_status != complaint.status:
                send_complaint_notification(complaint, 'status_update')
            
            return JsonResponse({
                'success': True,
                'message': 'Pengaduan berhasil diperbarui',
                'data': {
                    'id': complaint.id,
                    'complaint_id': complaint.complaint_id,
                    'title': complaint.title,
                    'status': complaint.get_status_display()
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # GET request - return current data
    categories = ComplaintCategory.objects.filter(is_active=True)
    return JsonResponse({
        'complaint': {
            'id': complaint.id,
            'complaint_id': complaint.complaint_id,
            'title': complaint.title,
            'description': complaint.description,
            'category_id': complaint.category_id,
            'priority': complaint.priority,
            'status': complaint.status,
            'reporter_name': complaint.reporter_name,
            'reporter_email': complaint.reporter_email,
            'reporter_phone': complaint.reporter_phone,
            'location': complaint.location,
            'admin_notes': complaint.admin_notes,
            'created_at': complaint.created_at.isoformat(),
        },
        'categories': [{'id': c.id, 'name': c.name} for c in categories],
        'priority_choices': Complaint.PRIORITY_CHOICES,
        'status_choices': Complaint.STATUS_CHOICES,
    })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def admin_complaint_delete(request, pk):
    """Delete complaint"""
    try:
        complaint = get_object_or_404(Complaint, pk=pk)
        complaint_id = complaint.complaint_id
        title = complaint.title
        complaint.delete()
        return JsonResponse({
            'success': True,
            'message': f'Pengaduan {complaint_id} - {title} berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
def admin_complaint_detail(request, pk):
    """View complaint details with updates"""
    complaint = get_object_or_404(Complaint, pk=pk)
    updates = ComplaintUpdate.objects.filter(complaint=complaint).order_by('-created_at')
    
    context = {
        'title': f'Detail Pengaduan - {complaint.complaint_id}',
        'complaint': complaint,
        'updates': updates,
    }
    return render(request, 'admin_panel/complaints/detail.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_complaint_add_update(request, pk):
    """Add update to complaint"""
    try:
        complaint = get_object_or_404(Complaint, pk=pk)
        data = json.loads(request.body)
        
        # Create update
        update = ComplaintUpdate.objects.create(
            complaint=complaint,
            status=data.get('status', complaint.status),
            message=data.get('message', ''),
            updated_by=request.user
        )
        
        # Update complaint status if changed
        if data.get('status') and data.get('status') != complaint.status:
            complaint.status = data.get('status')
            if data.get('status') == 'resolved':
                complaint.resolved_at = timezone.now()
            complaint.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Update berhasil ditambahkan',
            'data': {
                'id': update.id,
                'status': update.status,
                'message': update.message,
                'updated_by': update.updated_by.username,
                'created_at': update.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menambahkan update: {str(e)}'
        }, status=400)

# ==================== CATEGORY MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_categories_list(request):
    """Admin categories list view"""
    categories = ComplaintCategory.objects.all().order_by('name')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        categories = categories.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(categories, 25)
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'search': search,
    }
    return render(request, 'admin_panel/complaints/categories.html', context)

@login_required
@user_passes_test(is_admin)
def admin_complaint_categories_list(request):
    """Admin complaint categories list view"""
    return admin_categories_list(request)

@login_required
@user_passes_test(is_admin)
def admin_verifications_list(request):
    """Admin verifications list view"""
    from .forms import VerificationSearchForm
    
    # Get all verifications with related data
    verifications = ComplaintVerification.objects.select_related(
        'complaint', 'verified_by'
    ).prefetch_related('complaint__category').order_by('-created_at')
    
    # Search and filter functionality
    search_form = VerificationSearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        status = search_form.cleaned_data.get('status')
        verification_type = search_form.cleaned_data.get('verification_type')
        priority = search_form.cleaned_data.get('priority')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if search:
            verifications = verifications.filter(
                Q(complaint__complaint_id__icontains=search) |
                Q(verification_notes__icontains=search) |
                Q(verification_result__icontains=search) |
                Q(complaint__title__icontains=search)
            )
        
        if status:
            verifications = verifications.filter(status=status)
        
        if verification_type:
            verifications = verifications.filter(verification_type=verification_type)
        
        if priority:
            verifications = verifications.filter(priority_level=priority)
        
        if date_from:
            verifications = verifications.filter(created_at__date__gte=date_from)
        
        if date_to:
            verifications = verifications.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(verifications, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_verifications = ComplaintVerification.objects.count()
    pending_verifications = ComplaintVerification.objects.filter(status='pending').count()
    in_progress_verifications = ComplaintVerification.objects.filter(status='in_progress').count()
    verified_verifications = ComplaintVerification.objects.filter(status='verified').count()
    rejected_verifications = ComplaintVerification.objects.filter(status='rejected').count()
    
    context = {
        'title': 'Manajemen Verifikasi Pengaduan',
        'page_obj': page_obj,
        'search_form': search_form,
        'total_verifications': total_verifications,
        'pending_verifications': pending_verifications,
        'in_progress_verifications': in_progress_verifications,
        'verified_verifications': verified_verifications,
        'rejected_verifications': rejected_verifications,
    }
    return render(request, 'admin_panel/complaints/verifications.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_verification_create(request, complaint_id):
    """Create new verification for complaint"""
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    
    if request.method == 'POST':
        from .forms import ComplaintVerificationForm
        form = ComplaintVerificationForm(request.POST)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.complaint = complaint
            verification.verified_by = request.user
            verification.save()
            
            # Update complaint status if needed
            if verification.status == 'verified':
                complaint.status = 'in_progress'
                complaint.save()
            
            messages.success(request, 'Verifikasi berhasil ditambahkan.')
            return redirect('admin_panel:verification_detail', pk=verification.pk)
    else:
        from .forms import ComplaintVerificationForm
        form = ComplaintVerificationForm()
    
    context = {
        'title': f'Buat Verifikasi - {complaint.complaint_id}',
        'complaint': complaint,
        'form': form,
    }
    return render(request, 'admin_panel/complaints/verification_form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_verification_detail(request, pk):
    """View verification details"""
    verification = get_object_or_404(ComplaintVerification, pk=pk)
    
    context = {
        'title': f'Detail Verifikasi - {verification.complaint.complaint_id}',
        'verification': verification,
    }
    return render(request, 'admin_panel/complaints/verification_detail.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_verification_update(request, pk):
    """Update verification"""
    verification = get_object_or_404(ComplaintVerification, pk=pk)
    
    if request.method == 'POST':
        from .forms import ComplaintVerificationForm
        form = ComplaintVerificationForm(request.POST, instance=verification)
        if form.is_valid():
            form.save()
            messages.success(request, 'Verifikasi berhasil diperbarui.')
            return redirect('admin_panel:verification_detail', pk=verification.pk)
    else:
        from .forms import ComplaintVerificationForm
        form = ComplaintVerificationForm(instance=verification)
    
    context = {
        'title': f'Edit Verifikasi - {verification.complaint.complaint_id}',
        'verification': verification,
        'form': form,
    }
    return render(request, 'admin_panel/complaints/verification_form.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def admin_verification_delete(request, pk):
    """Delete verification"""
    try:
        verification = get_object_or_404(ComplaintVerification, pk=pk)
        complaint_id = verification.complaint.pk
        verification.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Verifikasi berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus verifikasi: {str(e)}'
        }, status=400)

@login_required
@user_passes_test(is_admin)
def admin_verification_dashboard(request):
    """Verification dashboard with statistics"""
    # Get statistics
    total_verifications = ComplaintVerification.objects.count()
    pending_verifications = ComplaintVerification.objects.filter(status='pending').count()
    in_progress_verifications = ComplaintVerification.objects.filter(status='in_progress').count()
    verified_verifications = ComplaintVerification.objects.filter(status='verified').count()
    rejected_verifications = ComplaintVerification.objects.filter(status='rejected').count()
    requires_info_verifications = ComplaintVerification.objects.filter(status='requires_info').count()
    
    # Recent verifications
    recent_verifications = ComplaintVerification.objects.select_related(
        'complaint', 'verified_by'
    ).order_by('-created_at')[:10]
    
    # Verification types statistics
    verification_types = ComplaintVerification.objects.values('verification_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status distribution
    status_distribution = ComplaintVerification.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Follow-up required
    follow_up_required = ComplaintVerification.objects.filter(
        requires_follow_up=True,
        follow_up_date__lte=timezone.now()
    ).count()
    
    context = {
        'title': 'Dashboard Verifikasi Pengaduan',
        'total_verifications': total_verifications,
        'pending_verifications': pending_verifications,
        'in_progress_verifications': in_progress_verifications,
        'verified_verifications': verified_verifications,
        'rejected_verifications': rejected_verifications,
        'requires_info_verifications': requires_info_verifications,
        'recent_verifications': recent_verifications,
        'verification_types': verification_types,
        'status_distribution': status_distribution,
        'follow_up_required': follow_up_required,
    }
    return render(request, 'admin_panel/complaints/verification_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_category_create(request):
    """Create new complaint category"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category = ComplaintCategory.objects.create(
                name=data.get('name'),
                description=data.get('description', ''),
                is_active=data.get('is_active', True)
            )
            return JsonResponse({
                'success': True,
                'message': 'Kategori berhasil ditambahkan',
                'data': {
                    'id': category.id,
                    'name': category.name,
                    'is_active': category.is_active
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'message': 'Method not allowed'}, status=405)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_category_update(request, pk):
    """Update complaint category"""
    category = get_object_or_404(ComplaintCategory, pk=pk)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category.name = data.get('name', category.name)
            category.description = data.get('description', category.description)
            category.is_active = data.get('is_active', category.is_active)
            category.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Kategori berhasil diperbarui',
                'data': {
                    'id': category.id,
                    'name': category.name,
                    'is_active': category.is_active
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # GET request - return current data
    return JsonResponse({
        'category': {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'is_active': category.is_active,
        }
    })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def admin_category_delete(request, pk):
    """Delete complaint category"""
    try:
        category = get_object_or_404(ComplaintCategory, pk=pk)
        
        # Check if category has complaints
        if category.complaint_set.exists():
            return JsonResponse({
                'success': False,
                'message': 'Kategori tidak dapat dihapus karena masih memiliki pengaduan'
            })
        
        name = category.name
        category.delete()
        return JsonResponse({
            'success': True,
            'message': f'Kategori {name} berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# ==================== CHAT MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_chat_sessions_list(request):
    """Admin list view for chat sessions"""
    sessions = ChatSession.objects.annotate(
        message_count=Count('messages')
    ).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        sessions = sessions.filter(status=status)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        sessions = sessions.filter(
            Q(session_id__icontains=search) |
            Q(user_name__icontains=search) |
            Q(user_email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(sessions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Manajemen Sesi Chat',
        'sessions': page_obj,
        'status_choices': ChatSession.STATUS_CHOICES,
        'current_filters': {
            'status': status,
            'search': search,
        }
    }
    return render(request, 'admin_panel/complaints/chat_sessions.html', context)

@login_required
@user_passes_test(is_admin)
def admin_chat_session_detail(request, session_id):
    """View chat session details with messages"""
    session = get_object_or_404(ChatSession, session_id=session_id)
    messages = ChatMessage.objects.filter(session=session).order_by('created_at')
    
    context = {
        'title': f'Detail Sesi Chat - {session.session_id}',
        'session': session,
        'messages': messages,
    }
    return render(request, 'admin_panel/complaints/chat_detail.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_chat_session_update_status(request, session_id):
    """Update chat session status"""
    try:
        session = get_object_or_404(ChatSession, session_id=session_id)
        data = json.loads(request.body)
        
        session.status = data.get('status', session.status)
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Status sesi chat berhasil diperbarui',
            'data': {
                'session_id': session.session_id,
                'status': session.get_status_display()
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# ==================== NOTIFICATION MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_notifications_list(request):
    """Admin list view for notifications"""
    notifications = Notification.objects.select_related('complaint').order_by('-created_at')
    
    # Filter by type
    notification_type = request.GET.get('type')
    if notification_type:
        notifications = notifications.filter(type=notification_type)
    
    # Filter by read status
    is_read = request.GET.get('is_read')
    if is_read is not None:
        notifications = notifications.filter(is_read=is_read == 'true')
    
    # Pagination
    paginator = Paginator(notifications, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Manajemen Notifikasi',
        'notifications': page_obj,
        'type_choices': Notification.TYPE_CHOICES,
        'current_filters': {
            'type': notification_type,
            'is_read': is_read,
        }
    }
    return render(request, 'admin_panel/complaints/notifications.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_notification_mark_read(request, pk):
    """Mark notification as read"""
    try:
        notification = get_object_or_404(Notification, pk=pk)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notifikasi berhasil ditandai sebagai dibaca'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_notifications_mark_all_read(request):
    """Mark all notifications as read"""
    try:
        count = Notification.objects.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{count} notifikasi berhasil ditandai sebagai dibaca'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# ==================== CONTACT MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_contacts_list(request):
    """Admin list view for contacts"""
    contacts = Contact.objects.order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        contacts = contacts.filter(status=status)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        contacts = contacts.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(subject__icontains=search) |
            Q(message__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(contacts, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Manajemen Kontak',
        'contacts': page_obj,
        'status_choices': Contact.STATUS_CHOICES,
        'current_filters': {
            'status': status,
            'search': search,
        }
    }
    return render(request, 'admin_panel/complaints/contacts.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_contact_update(request, pk):
    """Update contact status and response"""
    contact = get_object_or_404(Contact, pk=pk)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            contact.status = data.get('status', contact.status)
            contact.admin_response = data.get('admin_response', contact.admin_response)
            contact.responded_at = timezone.now()
            contact.save()
            
            # Send response email if provided
            if contact.admin_response and contact.status == 'responded':
                send_contact_response_email(contact)
            
            return JsonResponse({
                'success': True,
                'message': 'Kontak berhasil diperbarui',
                'data': {
                    'id': contact.id,
                    'status': contact.get_status_display()
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # GET request - return current data
    return JsonResponse({
        'contact': {
            'id': contact.id,
            'name': contact.name,
            'email': contact.email,
            'subject': contact.subject,
            'message': contact.message,
            'status': contact.status,
            'admin_response': contact.admin_response,
            'created_at': contact.created_at.isoformat(),
        },
        'status_choices': Contact.STATUS_CHOICES,
    })

def send_contact_response_email(contact):
    """Send response email to contact"""
    try:
        subject = f'Re: {contact.subject}'
        message = f"""
        Halo {contact.name},
        
        Terima kasih telah menghubungi kami. Berikut adalah tanggapan kami:
        
        {contact.admin_response}
        
        Jika Anda memiliki pertanyaan lebih lanjut, jangan ragu untuk menghubungi kami kembali.
        
        Salam,
        Tim Website Desa
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [contact.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending contact response email: {e}")

# ==================== REPORTS AND ANALYTICS ====================

@login_required
@user_passes_test(is_admin)
def admin_complaints_reports(request):
    """Generate complaints reports and analytics"""
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    complaints_qs = Complaint.objects.all()
    if start_date:
        complaints_qs = complaints_qs.filter(created_at__gte=parse_date(start_date))
    if end_date:
        complaints_qs = complaints_qs.filter(created_at__lte=parse_date(end_date))
    
    # Basic statistics
    total_complaints = complaints_qs.count()
    status_breakdown = complaints_qs.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    priority_breakdown = complaints_qs.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    category_breakdown = complaints_qs.values(
        'category__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Monthly trends
    monthly_trends = complaints_qs.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Resolution time analysis
    resolved_complaints = complaints_qs.filter(
        status__in=['resolved', 'closed'],
        resolved_at__isnull=False
    )
    
    resolution_times = []
    for complaint in resolved_complaints:
        hours = (complaint.resolved_at - complaint.created_at).total_seconds() / 3600
        resolution_times.append(hours)
    
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    context = {
        'title': 'Laporan Pengaduan',
        'total_complaints': total_complaints,
        'status_breakdown': list(status_breakdown),
        'priority_breakdown': list(priority_breakdown),
        'category_breakdown': list(category_breakdown),
        'monthly_trends': list(monthly_trends),
        'avg_resolution_time': avg_resolution_time,
        'date_filters': {
            'start_date': start_date,
            'end_date': end_date,
        }
    }
    return render(request, 'admin_panel/complaints/reports.html', context)

@login_required
@user_passes_test(is_admin)
def admin_complaints_export(request):
    """Export complaints data to CSV"""
    import csv
    from django.http import HttpResponse
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    category_id = request.GET.get('category')
    
    complaints = Complaint.objects.select_related('category').all()
    
    if start_date:
        complaints = complaints.filter(created_at__gte=parse_date(start_date))
    if end_date:
        complaints = complaints.filter(created_at__lte=parse_date(end_date))
    if status:
        complaints = complaints.filter(status=status)
    if category_id:
        complaints = complaints.filter(category_id=category_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="complaints_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID Pengaduan', 'Judul', 'Kategori', 'Prioritas', 'Status',
        'Pelapor', 'Email', 'Telepon', 'Lokasi', 'Tanggal Dibuat',
        'Tanggal Diselesaikan', 'Deskripsi', 'Catatan Admin'
    ])
    
    for complaint in complaints:
        writer.writerow([
            complaint.complaint_id,
            complaint.title,
            complaint.category.name if complaint.category else '',
            complaint.get_priority_display(),
            complaint.get_status_display(),
            complaint.reporter_name,
            complaint.reporter_email,
            complaint.reporter_phone,
            complaint.location,
            complaint.created_at.strftime('%Y-%m-%d %H:%M'),
            complaint.resolved_at.strftime('%Y-%m-%d %H:%M') if complaint.resolved_at else '',
            complaint.description,
            complaint.admin_notes
        ])
    
    return response

# ==================== BULK OPERATIONS ====================

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_complaints_bulk_update(request):
    """Bulk update complaints status"""
    try:
        data = json.loads(request.body)
        complaint_ids = data.get('complaint_ids', [])
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        if not complaint_ids or not new_status:
            return JsonResponse({
                'success': False,
                'message': 'ID pengaduan dan status baru harus diisi'
            })
        
        complaints = Complaint.objects.filter(id__in=complaint_ids)
        updated_count = 0
        
        for complaint in complaints:
            old_status = complaint.status
            complaint.status = new_status
            
            if new_status in ['resolved', 'closed'] and not complaint.resolved_at:
                complaint.resolved_at = timezone.now()
            
            complaint.save()
            
            # Create update record
            ComplaintUpdate.objects.create(
                complaint=complaint,
                status=new_status,
                notes=notes,
                updated_by=request.user
            )
            
            # Send notification if status changed
            if old_status != new_status:
                send_complaint_notification(complaint, 'status_update')
            
            updated_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} pengaduan berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def admin_complaints_bulk_delete(request):
    """Bulk delete complaints"""
    try:
        data = json.loads(request.body)
        complaint_ids = data.get('complaint_ids', [])
        
        if not complaint_ids:
            return JsonResponse({
                'success': False,
                'message': 'ID pengaduan harus diisi'
            })
        
        deleted_count = Complaint.objects.filter(id__in=complaint_ids).delete()[0]
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} pengaduan berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# ==================== API ENDPOINTS ====================

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def admin_api_complaints_stats(request):
    """API endpoint for complaints statistics"""
    # Basic counts
    stats = {
        'total': Complaint.objects.count(),
        'pending': Complaint.objects.filter(status='pending').count(),
        'in_progress': Complaint.objects.filter(status='in_progress').count(),
        'resolved': Complaint.objects.filter(status='resolved').count(),
        'closed': Complaint.objects.filter(status='closed').count(),
    }
    
    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_stats = {
        'new_complaints': Complaint.objects.filter(created_at__gte=week_ago).count(),
        'resolved_complaints': Complaint.objects.filter(
            resolved_at__gte=week_ago
        ).count(),
    }
    
    # Priority distribution
    priority_stats = dict(Complaint.objects.values_list('priority').annotate(
        count=Count('id')
    ))
    
    return JsonResponse({
        'stats': stats,
        'recent': recent_stats,
        'priority': priority_stats,
    })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def admin_api_complaints_search(request):
    """API endpoint for complaints search"""
    query = request.GET.get('q', '')
    limit = int(request.GET.get('limit', 10))
    
    if not query:
        return JsonResponse({'results': []})
    
    complaints = Complaint.objects.filter(
        Q(complaint_id__icontains=query) |
        Q(title__icontains=query) |
        Q(reporter_name__icontains=query)
    ).select_related('category')[:limit]
    
    results = []
    for complaint in complaints:
        results.append({
            'id': complaint.id,
            'complaint_id': complaint.complaint_id,
            'title': complaint.title,
            'reporter_name': complaint.reporter_name,
            'status': complaint.get_status_display(),
            'category': complaint.category.name if complaint.category else '',
            'created_at': complaint.created_at.isoformat(),
        })
    
    return JsonResponse({'results': results})


@login_required
@user_passes_test(is_admin)
def export_complaints(request):
    """Export complaints data to CSV/Excel"""
    from django.http import HttpResponse
    import csv
    from django.db.models import Q
    
    # Get filter parameters
    status = request.GET.get('status')
    category = request.GET.get('category')
    priority = request.GET.get('priority')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search = request.GET.get('search')
    format_type = request.GET.get('format', 'csv')
    
    # Build query
    complaints = Complaint.objects.select_related('category').all()
    
    if status:
        complaints = complaints.filter(status=status)
    if category:
        complaints = complaints.filter(category_id=category)
    if priority:
        complaints = complaints.filter(priority=priority)
    if start_date:
        complaints = complaints.filter(created_at__gte=start_date)
    if end_date:
        complaints = complaints.filter(created_at__lte=end_date)
    if search:
        complaints = complaints.filter(
            Q(complaint_id__icontains=search) |
            Q(reporter_name__icontains=search) |
            Q(subject__icontains=search) |
            Q(description__icontains=search)
        )
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="complaints_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID Pengaduan', 'Nama Pelapor', 'Email', 'Telepon', 'Kategori',
            'Subjek', 'Deskripsi', 'Status', 'Prioritas', 'Tanggal Dibuat'
        ])
        
        for complaint in complaints:
            writer.writerow([
                str(complaint.complaint_id),
                complaint.reporter_name,
                complaint.reporter_email,
                complaint.reporter_phone,
                complaint.category.name if complaint.category else '',
                complaint.subject,
                complaint.description,
                complaint.get_status_display(),
                complaint.get_priority_display(),
                complaint.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    elif format_type == 'excel':
        # For Excel export, you might want to use openpyxl or xlsxwriter
        # For now, return CSV with Excel content type
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="complaints_export.xlsx"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID Pengaduan', 'Nama Pelapor', 'Email', 'Telepon', 'Kategori',
            'Subjek', 'Deskripsi', 'Status', 'Prioritas', 'Tanggal Dibuat'
        ])
        
        for complaint in complaints:
            writer.writerow([
                str(complaint.complaint_id),
                complaint.reporter_name,
                complaint.reporter_email,
                complaint.reporter_phone,
                complaint.category.name if complaint.category else '',
                complaint.subject,
                complaint.description,
                complaint.get_status_display(),
                complaint.get_priority_display(),
                complaint.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    else:
        return JsonResponse({'error': 'Format tidak didukung'}, status=400)
