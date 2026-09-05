from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test

from .models import Document, DocumentCategory, DocumentComment
from .forms import DocumentForm, DocumentCategoryForm, DocumentCommentForm

# Import Penduduk model - try references first, then letters as fallback
try:
    from references.models import Penduduk
    print("Documents views: Using references.models.Penduduk")
except ImportError:
    try:
        from letters.models import Penduduk
        print("Documents views: Using letters.models.Penduduk")
    except ImportError:
        Penduduk = None
        print("Documents views: No Penduduk model found")


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
def documents_dashboard(request):
    """Documents dashboard with statistics"""
    # Get basic statistics
    total_documents = Document.objects.count()
    draft_documents = Document.objects.filter(status='draft').count()
    submitted_documents = Document.objects.filter(status='submitted').count()
    approved_documents = Document.objects.filter(status='approved').count()
    
    # Get recent documents
    recent_documents = Document.objects.select_related('applicant', 'created_by').order_by('-created_at')[:5]
    
    # Get category statistics
    category_stats = []
    for category, label in Document.CATEGORY_CHOICES:
        count = Document.objects.filter(category=category).count()
        category_stats.append({
            'category': category,
            'label': label,
            'count': count
        })
    
    context = {
        'page_title': 'Dashboard Dokumen',
        'total_documents': total_documents,
        'draft_documents': draft_documents,
        'submitted_documents': submitted_documents,
        'approved_documents': approved_documents,
        'recent_documents': recent_documents,
        'category_stats': category_stats,
    }
    
    return render(request, 'admin_panel/documents/dashboard.html', context)


@login_required
def documents_list(request):
    """List all documents with filtering and search"""
    # Get filter parameters
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    page = request.GET.get('page', 1)
        
    # Build queryset
    documents = Document.objects.select_related('applicant', 'created_by', 'document_category').all()
        
    # Apply filters
    if category:
        documents = documents.filter(category=category)
    if status:
        documents = documents.filter(status=status)
    if search:
        documents = documents.filter(
            Q(title__icontains=search) |
            Q(document_number__icontains=search) |
            Q(content__icontains=search) |
            Q(applicant__name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_obj = paginator.get_page(page)
        
    context = {
        'page_title': 'Daftar Dokumen',
        'documents': page_obj,
        'categories': Document.CATEGORY_CHOICES,
        'statuses': Document.STATUS_CHOICES,
        'current_category': category,
        'current_status': status,
        'current_search': search,
    }
    
    return render(request, 'admin_panel/documents/documents_list.html', context)


@login_required
def document_detail(request, pk):
    """View document details"""
    document = get_object_or_404(Document, pk=pk)
    comments = DocumentComment.objects.filter(document=document).order_by('-created_at')
    
    context = {
        'page_title': f'Detail Dokumen - {document.title}',
        'document': document,
        'comments': comments,
    }
    
    return render(request, 'admin_panel/documents/document_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def document_create(request):
    """Create new document"""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.created_by = request.user
            
            # Handle applicant_id if provided
            applicant_id = request.POST.get('applicant_id')
            if applicant_id and Penduduk:
                try:
                    applicant = Penduduk.objects.get(id=applicant_id)
                    document.applicant = applicant
                except Penduduk.DoesNotExist:
                    pass
            
            document.save()
            messages.success(request, 'Dokumen berhasil dibuat!')
            return redirect('admin_panel:document_detail', pk=document.pk)
    else:
        form = DocumentForm()
    
    context = {
        'page_title': 'Tambah Dokumen Baru',
        'form': form,
    }
    
    return render(request, 'admin_panel/documents/document_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def document_edit(request, pk):
    """Edit document"""
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            # Handle applicant_id if provided
            applicant_id = request.POST.get('applicant_id')
            if applicant_id and Penduduk:
                try:
                    applicant = Penduduk.objects.get(id=applicant_id)
                    document.applicant = applicant
                except Penduduk.DoesNotExist:
                    pass
            elif not applicant_id:
                document.applicant = None
            
            form.save()
            messages.success(request, 'Dokumen berhasil diperbarui!')
            return redirect('admin_panel:document_detail', pk=document.pk)
    else:
        form = DocumentForm(instance=document)
    
    context = {
        'page_title': f'Edit Dokumen - {document.title}',
        'form': form,
        'document': document,
    }
    
    return render(request, 'admin_panel/documents/document_form.html', context)


@login_required
@require_http_methods(["POST"])
def document_delete(request, pk):
    """Delete document"""
    document = get_object_or_404(Document, pk=pk)
    document.delete()
    messages.success(request, 'Dokumen berhasil dihapus!')
    return redirect('admin_panel:documents_list')


@login_required
@require_http_methods(["GET", "POST"])
def document_comment_add(request, pk):
    """Add comment to document"""
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        form = DocumentCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.document = document
            comment.user = request.user
            comment.save()
            messages.success(request, 'Komentar berhasil ditambahkan!')
            return redirect('admin_panel:document_detail', pk=document.pk)
    else:
        form = DocumentCommentForm()
    
    context = {
        'page_title': f'Tambah Komentar - {document.title}',
        'form': form,
        'document': document,
    }
    
    return render(request, 'admin_panel/documents/document_comment_form.html', context)


@login_required
def document_categories_list(request):
    """List document categories"""
    categories = DocumentCategory.objects.all()
    
    context = {
        'page_title': 'Kategori Dokumen',
        'categories': categories,
    }
    
    return render(request, 'admin_panel/documents/categories_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def document_category_create(request):
    """Create document category"""
    if request.method == 'POST':
        form = DocumentCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori dokumen berhasil dibuat!')
            return redirect('admin_panel:document_categories_list')
    else:
        form = DocumentCategoryForm()
    
    context = {
        'page_title': 'Tambah Kategori Dokumen',
        'form': form,
    }
    
    return render(request, 'admin_panel/documents/category_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def document_category_edit(request, pk):
    """Edit document category"""
    category = get_object_or_404(DocumentCategory, pk=pk)
    
    if request.method == 'POST':
        form = DocumentCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori dokumen berhasil diperbarui!')
            return redirect('admin_panel:document_categories_list')
    else:
        form = DocumentCategoryForm(instance=category)
    
    context = {
        'page_title': f'Edit Kategori - {category.name}',
        'form': form,
        'category': category,
    }
    
    return render(request, 'admin_panel/documents/category_form.html', context)


@login_required
@require_http_methods(["POST"])
def document_category_delete(request, pk):
    """Delete document category"""
    category = get_object_or_404(DocumentCategory, pk=pk)
    category.delete()
    messages.success(request, 'Kategori dokumen berhasil dihapus!')
    return redirect('admin_panel:document_categories_list')


@login_required
def api_documents_stats(request):
    """API endpoint for document statistics"""
    try:
        stats = {
            'total': Document.objects.count(),
            'draft': Document.objects.filter(status='draft').count(),
            'submitted': Document.objects.filter(status='submitted').count(),
            'approved': Document.objects.filter(status='approved').count(),
            'rejected': Document.objects.filter(status='rejected').count(),
            'completed': Document.objects.filter(status='completed').count(),
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_penduduk_search(request):
    """API endpoint for searching penduduk"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return JsonResponse({
                'success': True,
                'penduduk': []
            })
        
        if not Penduduk:
            return JsonResponse({
                'success': True,
                'penduduk': []
            })
        
        # Search penduduk by name or NIK
        penduduk_list = Penduduk.objects.filter(
            Q(name__icontains=query) | Q(nik__icontains=query)
        )[:10]
        
        penduduk_data = []
        for penduduk in penduduk_list:
            penduduk_data.append({
                'id': penduduk.id,
                'name': penduduk.name,
                'nik': penduduk.nik,
                'alamat': getattr(penduduk, 'alamat', ''),
            })
        
        return JsonResponse({
            'success': True,
            'penduduk': penduduk_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def document_preview(request, pk):
    """Preview document attachment"""
    document = get_object_or_404(Document, pk=pk)
    
    if not document.file_attachment:
        messages.error(request, 'Dokumen tidak memiliki lampiran untuk di-preview.')
        return redirect('admin_panel:document_detail', pk=document.pk)
    
    # Get file extension
    file_name = document.file_attachment.name
    file_extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
    
    # Determine file type and preview capability
    preview_type = None
    if file_extension in ['pdf']:
        preview_type = 'pdf'
    elif file_extension in ['doc', 'docx']:
        preview_type = 'word'
    elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
        preview_type = 'image'
    elif file_extension in ['xls', 'xlsx']:
        preview_type = 'excel'
    else:
        messages.warning(request, f'Preview tidak tersedia untuk file tipe .{file_extension}')
        return redirect('admin_panel:document_detail', pk=document.pk)
    
    context = {
        'page_title': f'Preview - {document.title}',
        'document': document,
        'preview_type': preview_type,
        'file_url': document.file_attachment.url,
        'file_name': file_name,
        'file_extension': file_extension,
    }
    
    return render(request, 'admin_panel/documents/document_preview.html', context)
