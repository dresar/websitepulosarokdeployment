from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import json

def check_staff_access(request):
    """Helper function to check if user is staff"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")
    return None

from .models import LayananFeedback, LayananFAQ, LayananContact, LayananService
from .forms import (
    FeedbackForm, FAQForm, ContactForm, ServiceForm,
    QuickFeedbackForm, QuickFAQForm, QuickContactForm, QuickServiceForm
)


@login_required
def layanan_dashboard(request):
    """Dashboard for layanan management"""
    staff_check = check_staff_access(request)
    if staff_check:
        return staff_check
    # Get statistics
    total_feedback = LayananFeedback.objects.count()
    monthly_feedback = LayananFeedback.objects.filter(
        created_at__gte=timezone.now().replace(day=1)
    ).count()
    unread_feedback = LayananFeedback.objects.filter(status='pending').count()
    
    total_faq = LayananFAQ.objects.count()
    active_faq = LayananFAQ.objects.filter(is_active=True).count()
    faq_categories = LayananFAQ.objects.values('category').distinct().count()
    
    total_contacts = LayananContact.objects.count()
    active_contacts = LayananContact.objects.filter(is_active=True).count()
    contact_departments = LayananContact.objects.values('department').distinct().count()
    
    total_services = LayananService.objects.count()
    active_services = LayananService.objects.filter(is_active=True).count()
    service_categories = LayananService.objects.values('category').distinct().count()
    
    # Recent activities
    recent_activities = []
    
    # Recent feedback
    recent_feedback = LayananFeedback.objects.order_by('-created_at')[:3]
    for feedback in recent_feedback:
        recent_activities.append({
            'type': 'feedback',
            'icon': 'comments',
            'title': f'Feedback dari {feedback.name}',
            'description': feedback.subject,
            'time': feedback.created_at.strftime('%d %b %Y, %H:%M')
        })
    
    # Recent FAQ
    recent_faq = LayananFAQ.objects.order_by('-created_at')[:2]
    for faq in recent_faq:
        recent_activities.append({
            'type': 'faq',
            'icon': 'question-circle',
            'title': 'FAQ Baru',
            'description': faq.question[:50] + '...',
            'time': faq.created_at.strftime('%d %b %Y, %H:%M')
        })
    
    # Recent contacts
    recent_contacts = LayananContact.objects.order_by('-created_at')[:2]
    for contact in recent_contacts:
        recent_activities.append({
            'type': 'contact',
            'icon': 'phone',
            'title': f'Kontak {contact.name}',
            'description': f'{contact.position} - {contact.department}',
            'time': contact.created_at.strftime('%d %b %Y, %H:%M')
        })
    
    # Recent services
    recent_services = LayananService.objects.order_by('-created_at')[:2]
    for service in recent_services:
        recent_activities.append({
            'type': 'service',
            'icon': 'cogs',
            'title': f'Layanan {service.name}',
            'description': service.description[:50] + '...',
            'time': service.created_at.strftime('%d %b %Y, %H:%M')
        })
    
    # Sort activities by time
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:5]
    
    context = {
        'total_feedback': total_feedback,
        'monthly_feedback': monthly_feedback,
        'unread_feedback': unread_feedback,
        'total_faq': total_faq,
        'active_faq': active_faq,
        'faq_categories': faq_categories,
        'total_contacts': total_contacts,
        'active_contacts': active_contacts,
        'contact_departments': contact_departments,
        'total_services': total_services,
        'active_services': active_services,
        'service_categories': service_categories,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'admin_panel/layanan/dashboard.html', context)


@login_required
def feedback_list(request):
    """List all feedback with filtering"""
    feedbacks = LayananFeedback.objects.all()
    
    # Filtering
    selected_status = request.GET.get('status', '')
    selected_rating = request.GET.get('rating', '')
    selected_category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    if selected_status:
        feedbacks = feedbacks.filter(status=selected_status)
    if selected_rating:
        feedbacks = feedbacks.filter(rating=selected_rating)
    if selected_category:
        feedbacks = feedbacks.filter(category=selected_category)
    if search:
        feedbacks = feedbacks.filter(
            Q(name__icontains=search) |
            Q(subject__icontains=search) |
            Q(message__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(feedbacks, 20)
    page_number = request.GET.get('page')
    feedbacks = paginator.get_page(page_number)
    
    context = {
        'feedbacks': feedbacks,
        'selected_status': selected_status,
        'selected_rating': selected_rating,
        'selected_category': selected_category,
        'search': search,
    }
    
    return render(request, 'admin_panel/layanan/feedback_list.html', context)


@login_required
def feedback_detail(request, pk):
    """Detail view for feedback"""
    feedback = get_object_or_404(LayananFeedback, pk=pk)
    
    # Mark as read if not already
    if feedback.status == 'pending':
        feedback.status = 'read'
        feedback.save()
    
    context = {
        'feedback': feedback,
    }
    
    return render(request, 'admin_panel/layanan/feedback_detail.html', context)


@login_required
def feedback_form(request):
    """Create or edit feedback"""
    feedback_id = request.GET.get('id')
    feedback = None
    
    if feedback_id:
        feedback = get_object_or_404(LayananFeedback, pk=feedback_id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Feedback berhasil disimpan!'
                })
            else:
                messages.success(request, 'Feedback berhasil disimpan!')
                return redirect('admin_panel:layanan:feedback_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Data tidak valid',
                    'errors': form.errors
                })
    else:
        form = FeedbackForm(instance=feedback)
    
    context = {
        'form': form,
        'feedback': feedback,
    }
    
    return render(request, 'admin_panel/layanan/feedback_form.html', context)


@login_required
def feedback_mark_read(request, pk):
    """Mark feedback as read"""
    feedback = get_object_or_404(LayananFeedback, pk=pk)
    feedback.status = 'read'
    feedback.save()
    messages.success(request, 'Feedback telah ditandai sebagai dibaca!')
    return redirect('admin_panel:layanan:feedback_detail', pk=pk)


@login_required
def feedback_reply(request, pk):
    """Reply to feedback"""
    feedback = get_object_or_404(LayananFeedback, pk=pk)
    
    if request.method == 'POST':
        reply = request.POST.get('reply', '')
        if reply:
            feedback.reply = reply
            feedback.status = 'replied'
            feedback.replied_at = timezone.now()
            feedback.save()
            messages.success(request, 'Balasan berhasil dikirim!')
            return redirect('admin_panel:layanan:feedback_detail', pk=pk)
    
    context = {
        'feedback': feedback,
    }
    
    return render(request, 'admin_panel/layanan/feedback_reply.html', context)


# FAQ Management
@login_required
def faq_list(request):
    """List all FAQ"""
    faqs = LayananFAQ.objects.all().order_by('order', 'created_at')
    
    # Filtering
    selected_category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    if selected_category:
        faqs = faqs.filter(category=selected_category)
    if search:
        faqs = faqs.filter(
            Q(question__icontains=search) |
            Q(answer__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(faqs, 20)
    page_number = request.GET.get('page')
    faqs = paginator.get_page(page_number)
    
    context = {
        'faqs': faqs,
        'selected_category': selected_category,
        'search': search,
    }
    
    return render(request, 'admin_panel/layanan/faq_list.html', context)


@login_required
def faq_form(request):
    """Create or edit FAQ"""
    faq_id = request.GET.get('id')
    faq = None
    
    if faq_id:
        faq = get_object_or_404(LayananFAQ, pk=faq_id)
    
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'FAQ berhasil disimpan!'
                })
            else:
                messages.success(request, 'FAQ berhasil disimpan!')
                return redirect('admin_panel:layanan:faq_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Data tidak valid',
                    'errors': form.errors
                })
    else:
        form = FAQForm(instance=faq)
    
    context = {
        'form': form,
        'faq': faq,
    }
    
    return render(request, 'admin_panel/layanan/faq_form.html', context)


# Contact Management
@login_required
def contact_list(request):
    """List all contacts"""
    contacts = LayananContact.objects.all().order_by('department', 'name')
    
    # Filtering
    selected_department = request.GET.get('department', '')
    selected_status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    if selected_department:
        contacts = contacts.filter(department=selected_department)
    if selected_status:
        if selected_status == 'active':
            contacts = contacts.filter(is_active=True)
        elif selected_status == 'inactive':
            contacts = contacts.filter(is_active=False)
    if search:
        contacts = contacts.filter(
            Q(name__icontains=search) |
            Q(position__icontains=search) |
            Q(department__icontains=search)
        )
    
    # Get unique departments for filter dropdown
    departments = LayananContact.objects.values_list('department', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    contacts = paginator.get_page(page_number)
    
    context = {
        'contacts': contacts,
        'selected_department': selected_department,
        'selected_status': selected_status,
        'search': search,
        'departments': departments,
    }
    
    return render(request, 'admin_panel/layanan/contact_list.html', context)


@login_required
def contact_form(request):
    """Create or edit contact"""
    contact_id = request.GET.get('id')
    contact = None
    
    if contact_id:
        contact = get_object_or_404(LayananContact, pk=contact_id)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Kontak berhasil disimpan!'
                })
            else:
                messages.success(request, 'Kontak berhasil disimpan!')
                return redirect('admin_panel:layanan:contact_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Data tidak valid',
                    'errors': form.errors
                })
    else:
        form = ContactForm(instance=contact)
    
    context = {
        'form': form,
        'contact': contact,
    }
    
    return render(request, 'admin_panel/layanan/contact_form.html', context)


# Service Management
@login_required
def service_list(request):
    """List all services"""
    services = LayananService.objects.all().order_by('order', 'name')
    
    # Filtering
    selected_category = request.GET.get('category', '')
    selected_status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    if selected_category:
        services = services.filter(category=selected_category)
    if selected_status:
        if selected_status == 'active':
            services = services.filter(is_active=True)
        elif selected_status == 'inactive':
            services = services.filter(is_active=False)
    if search:
        services = services.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(services, 20)
    page_number = request.GET.get('page')
    services = paginator.get_page(page_number)
    
    context = {
        'services': services,
        'selected_category': selected_category,
        'selected_status': selected_status,
        'search': search,
    }
    
    return render(request, 'admin_panel/layanan/service_list.html', context)


@login_required
def service_form(request):
    """Create or edit service"""
    service_id = request.GET.get('id')
    service = None
    
    if service_id:
        service = get_object_or_404(LayananService, pk=service_id)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Layanan berhasil disimpan!'
                })
            else:
                messages.success(request, 'Layanan berhasil disimpan!')
                return redirect('admin_panel:layanan:service_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Data tidak valid',
                    'errors': form.errors
                })
    else:
        form = ServiceForm(instance=service)
    
    context = {
        'form': form,
        'service': service,
    }
    
    return render(request, 'admin_panel/layanan/service_form.html', context)


# AJAX Views for Modal Operations
@csrf_exempt
@require_http_methods(["POST"])
def ajax_create_feedback(request):
    """AJAX endpoint for creating feedback via modal"""
    try:
        form = QuickFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Feedback berhasil dibuat!',
                'data': {
                    'id': feedback.id,
                    'name': feedback.name,
                    'subject': feedback.subject,
                    'status': feedback.get_status_display(),
                    'created_at': feedback.created_at.strftime('%d %b %Y, %H:%M')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Data tidak valid',
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ajax_create_faq(request):
    """AJAX endpoint for creating FAQ via modal"""
    try:
        form = QuickFAQForm(request.POST)
        if form.is_valid():
            faq = form.save()
            return JsonResponse({
                'success': True,
                'message': 'FAQ berhasil dibuat!',
                'data': {
                    'id': faq.id,
                    'question': faq.question,
                    'category': faq.get_category_display(),
                    'is_active': faq.is_active
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Data tidak valid',
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ajax_create_contact(request):
    """AJAX endpoint for creating contact via modal"""
    try:
        form = QuickContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Kontak berhasil dibuat!',
                'data': {
                    'id': contact.id,
                    'name': contact.name,
                    'position': contact.position,
                    'department': contact.department,
                    'phone': contact.phone
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Data tidak valid',
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ajax_create_service(request):
    """AJAX endpoint for creating service via modal"""
    try:
        form = QuickServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Layanan berhasil dibuat!',
                'data': {
                    'id': service.id,
                    'name': service.name,
                    'category': service.get_category_display(),
                    'is_active': service.is_active
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Data tidak valid',
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ajax_delete_item(request):
    """AJAX endpoint for deleting items"""
    try:
        data = json.loads(request.body)
        item_type = data.get('type')
        item_id = data.get('id')
        
        if item_type == 'feedback':
            item = get_object_or_404(LayananFeedback, pk=item_id)
        elif item_type == 'faq':
            item = get_object_or_404(LayananFAQ, pk=item_id)
        elif item_type == 'contact':
            item = get_object_or_404(LayananContact, pk=item_id)
        elif item_type == 'service':
            item = get_object_or_404(LayananService, pk=item_id)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Tipe item tidak valid'
            })
        
        item.delete()
        return JsonResponse({
            'success': True,
            'message': f'{item_type.title()} berhasil dihapus!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ajax_toggle_status(request):
    """AJAX endpoint for toggling item status"""
    try:
        data = json.loads(request.body)
        item_type = data.get('type')
        item_id = data.get('id')
        
        if item_type == 'faq':
            item = get_object_or_404(LayananFAQ, pk=item_id)
            item.is_active = not item.is_active
        elif item_type == 'contact':
            item = get_object_or_404(LayananContact, pk=item_id)
            item.is_active = not item.is_active
        elif item_type == 'service':
            item = get_object_or_404(LayananService, pk=item_id)
            item.is_active = not item.is_active
        else:
            return JsonResponse({
                'success': False,
                'message': 'Tipe item tidak valid'
            })
        
        item.save()
        return JsonResponse({
            'success': True,
            'message': f'Status {item_type} berhasil diubah!',
            'is_active': item.is_active
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })