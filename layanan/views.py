from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q
import json

# Import models from different apps
from documents.models import Document
from .models import LayananDocumentRequest
# from business.models import LayananJasa  # Temporarily disabled
from posyandu.models import PosyanduLocation, PosyanduSchedule
from tourism.models import TourismLocation, TourismEvent
from news.models import Announcement


class LayananIndexView(TemplateView):
    """Main layanan page with overview of all services"""
    template_name = 'public/layanan/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent announcements
        context['recent_announcements'] = Announcement.objects.filter(
            status='published'
        ).order_by('-created_at')[:3]
        
        # Get document types count
        context['document_types_count'] = len(LayananDocumentRequest.DOCUMENT_TYPE_CHOICES)
        
        # Get business services count
        context['business_services_count'] = LayananJasa.objects.filter(
            status='aktif'
        ).count()
        
        # Get posyandu locations count
        context['posyandu_locations_count'] = PosyanduLocation.objects.filter(
            is_active=True
        ).count()
        
        # Get tourism locations count
        context['tourism_locations_count'] = TourismLocation.objects.filter(
            is_active=True
        ).count()
        
        return context


class ChatLayananView(TemplateView):
    """Chat service page"""
    template_name = 'public/layanan/chat_layanan.html'


class DocumentServicesView(TemplateView):
    """Document services listing page"""
    template_name = 'public/layanan/document_services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all document types
        context['document_types'] = LayananDocumentRequest.DOCUMENT_TYPE_CHOICES
        
        # Get recent document requests (for stats)
        context['recent_requests'] = LayananDocumentRequest.objects.filter(
            status='pending'
        ).count()
        
        return context


class DocumentInfoView(TemplateView):
    """Document information page"""
    template_name = 'public/layanan/document_info.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_type = self.kwargs.get('document_type', '')
        
        if document_type:
            # Map URL parameters to document type choices
            type_mapping = {
                'surat_keterangan': 'Surat Keterangan',
                'surat_pengantar': 'Surat Pengantar',
                'surat_izin': 'Surat Izin',
                'surat_rekomendasi': 'Surat Rekomendasi',
                'surat_kepemilikan': 'Surat Kepemilikan',
                'surat_lainnya': 'Surat Lainnya',
            }
            
            # Get the mapped name or use the original parameter
            mapped_name = type_mapping.get(document_type, document_type)
            
            # Find the selected document type from choices
            selected_type = None
            for choice_value, choice_label in LayananDocumentRequest.DOCUMENT_TYPE_CHOICES:
                if mapped_name.lower() in choice_label.lower() or document_type.lower() in choice_label.lower():
                    selected_type = {'value': choice_value, 'label': choice_label}
                    break
            context['selected_document_type'] = selected_type
        
        # Get all document types for selection
        context['document_types'] = LayananDocumentRequest.DOCUMENT_TYPE_CHOICES
        
        return context


class DocumentRequestView(TemplateView):
    """Document request form page"""
    template_name = 'public/layanan/document_request.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_type = self.kwargs.get('document_type', '')
        
        if document_type:
            # Map URL parameters to document type choices
            type_mapping = {
                'surat_keterangan': 'Surat Keterangan',
                'surat_pengantar': 'Surat Pengantar',
                'surat_izin': 'Surat Izin',
                'surat_rekomendasi': 'Surat Rekomendasi',
                'surat_kepemilikan': 'Surat Kepemilikan',
                'surat_lainnya': 'Surat Lainnya',
            }
            
            # Get the mapped name or use the original parameter
            mapped_name = type_mapping.get(document_type, document_type)
            
            # Find the selected document type from choices
            selected_type = None
            for choice_value, choice_label in LayananDocumentRequest.DOCUMENT_TYPE_CHOICES:
                if mapped_name.lower() in choice_label.lower() or document_type.lower() in choice_label.lower():
                    selected_type = {'value': choice_value, 'label': choice_label}
                    break
            context['selected_document_type'] = selected_type
        
        # Get all document types for selection
        context['document_types'] = LayananDocumentRequest.DOCUMENT_TYPE_CHOICES
        
        return context


class DocumentRequestSubmitView(TemplateView):
    """Handle document request submission"""
    template_name = 'public/layanan/document_request_success.html'
    
    def post(self, request, *args, **kwargs):
        # Handle form submission
        full_name = request.POST.get('full_name')
        nik = request.POST.get('nik')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        document_type = request.POST.get('document_type')
        purpose = request.POST.get('purpose')
        description = request.POST.get('description')
        
        # Create document request
        try:
            LayananDocumentRequest.objects.create(
                full_name=full_name,
                nik=nik,
                phone=phone,
                email=email,
                address=address,
                document_type=document_type,
                purpose=purpose,
                description=description,
                status='pending'
            )
            messages.success(request, 'Permintaan dokumen berhasil diajukan!')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
        
        return self.get(request, *args, **kwargs)


class BusinessServicesView(TemplateView):
    """Business services listing page"""
    template_name = 'public/layanan/business_services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get business services
        context['business_services'] = LayananJasa.objects.filter(
            status='aktif'
        ).order_by('nama')
        
        return context


class HealthServicesView(TemplateView):
    """Health services listing page"""
    template_name = 'public/layanan/health_services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get posyandu locations
        context['posyandu_locations'] = PosyanduLocation.objects.filter(
            is_active=True
        ).order_by('name')
        
        # Get posyandu schedules
        context['posyandu_schedules'] = PosyanduSchedule.objects.all().order_by('schedule_date')
        
        return context


class TourismServicesView(TemplateView):
    """Tourism services listing page"""
    template_name = 'public/layanan/tourism_services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get tourism locations
        context['tourism_locations'] = TourismLocation.objects.filter(
            is_active=True
        ).order_by('title')
        
        # Get tourism events
        context['tourism_events'] = TourismEvent.objects.filter(
            is_active=True
        ).order_by('-start_date')
        
        return context


class ContactView(TemplateView):
    """Contact page"""
    template_name = 'public/layanan/contact.html'


class RequestStatusView(TemplateView):
    """Request status page"""
    template_name = 'public/layanan/request_status.html'


class PosyanduServicesView(TemplateView):
    """Posyandu services page"""
    template_name = 'public/layanan/posyandu_services.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get posyandu locations
        context['posyandu_locations'] = PosyanduLocation.objects.filter(
            is_active=True
        ).order_by('name')
        
        # Get posyandu schedules
        context['posyandu_schedules'] = PosyanduSchedule.objects.all().order_by('schedule_date')
        
        return context


@csrf_exempt
def api_document_types(request):
    """API endpoint for document types"""
    if request.method == 'GET':
        document_types = LayananDocumentRequest.DOCUMENT_TYPE_CHOICES
        data = {
            'success': True,
            'document_types': [
                {'value': choice[0], 'label': choice[1]} 
                for choice in document_types
            ]
        }
        return JsonResponse(data)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def api_chat_message(request):
    """API endpoint for chat messages"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Simple response logic
            response_message = "Terima kasih atas pesan Anda. Tim kami akan segera merespons."
            
            return JsonResponse({
                'success': True,
                'response': response_message
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def api_request_status(request):
    """API endpoint for request status"""
    if request.method == 'GET':
        nik = request.GET.get('nik', '')
        
        if nik:
            requests = LayananDocumentRequest.objects.filter(nik=nik).order_by('-created_at')
            data = {
                'success': True,
                'requests': [
                    {
                        'id': req.id,
                        'document_type': req.get_document_type_display(),
                        'status': req.get_status_display(),
                        'created_at': req.created_at.strftime('%d %B %Y'),
                        'purpose': req.purpose
                    }
                    for req in requests
                ]
            }
        else:
            data = {
                'success': False,
                'message': 'NIK tidak ditemukan'
            }
        
        return JsonResponse(data)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
