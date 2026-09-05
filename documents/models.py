from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

# Import Penduduk model - try references first, then letters as fallback
try:
    from references.models import Penduduk
    print("Documents models: Using references.models.Penduduk")
except ImportError:
    try:
        from letters.models import Penduduk
        print("Documents models: Using letters.models.Penduduk")
    except ImportError:
        Penduduk = None
        print("Documents models: No Penduduk model found")


class DocumentCategory(models.Model):
    """Simple document categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Kategori Dokumen'
        verbose_name_plural = 'Kategori Dokumen'
        ordering = ['name']


class Document(models.Model):
    """Simplified Document model for storing all types of documents"""
    
    CATEGORY_CHOICES = [
        ('surat_warga', 'Surat dari Warga'),
        ('surat_masuk', 'Surat Masuk'),
        ('surat_keluar', 'Surat Keluar'),
        ('surat_internal', 'Surat Internal'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Diajukan'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('completed', 'Selesai'),
        ('archived', 'Diarsipkan'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Rendah'),
        ('normal', 'Normal'),
        ('high', 'Tinggi'),
        ('urgent', 'Mendesak'),
    ]

    # Basic document info
    title = models.CharField(max_length=200, verbose_name='Judul Dokumen')
    document_number = models.CharField(max_length=50, blank=True, verbose_name='Nomor Dokumen')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='surat_warga', verbose_name='Kategori')
    document_category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Kategori Dokumen')
    
    # Content
    content = models.TextField(blank=True, verbose_name='Isi Dokumen')
    summary = models.TextField(blank=True, verbose_name='Ringkasan')
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Status')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='Prioritas')
    
    # People involved
    applicant = models.ForeignKey(Penduduk, on_delete=models.CASCADE, null=True, blank=True, related_name='documents', verbose_name='Pemohon')
    recipient = models.CharField(max_length=200, blank=True, verbose_name='Penerima')
    sender = models.CharField(max_length=200, blank=True, verbose_name='Pengirim')
    
    # Dates
    document_date = models.DateField(default=timezone.now, verbose_name='Tanggal Dokumen')
    submission_date = models.DateTimeField(null=True, blank=True, verbose_name='Tanggal Diajukan')
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name='Tanggal Selesai')
    
    # File attachment
    file_attachment = models.FileField(upload_to='documents/', blank=True, verbose_name='Lampiran')
    
    # Additional info
    notes = models.TextField(blank=True, verbose_name='Catatan')
    tags = models.CharField(max_length=500, blank=True, verbose_name='Tags', help_text='Pisahkan dengan koma')
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Dibuat Oleh')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Dibuat Pada')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Diupdate Pada')

    def __str__(self):
        return f'{self.document_number} - {self.title}' if self.document_number else self.title

    def get_status_display_color(self):
        """Get color for status badge"""
        colors = {
            'draft': 'secondary',
            'submitted': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'completed': 'primary',
            'archived': 'dark',
        }
        return colors.get(self.status, 'secondary')

    def get_priority_display_color(self):
        """Get color for priority badge"""
        colors = {
            'low': 'success',
            'normal': 'primary',
            'high': 'warning',
            'urgent': 'danger',
        }
        return colors.get(self.priority, 'primary')

    def get_category_display_color(self):
        """Get color for category badge"""
        colors = {
            'surat_warga': 'info',
            'surat_masuk': 'success',
            'surat_keluar': 'primary',
            'surat_internal': 'warning',
        }
        return colors.get(self.category, 'secondary')

    def get_tags_list(self):
        """Get tags as list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def set_tags_list(self, tags_list):
        """Set tags from list"""
        self.tags = ', '.join(tags_list)

    class Meta:
        verbose_name = 'Dokumen'
        verbose_name_plural = 'Dokumen'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['document_date']),
            models.Index(fields=['created_at']),
        ]


class DocumentComment(models.Model):
    """Simple comments for documents"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='Komentar')
    is_internal = models.BooleanField(default=False, verbose_name='Komentar Internal')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Komentar oleh {self.author.username} pada {self.document.title}'

    class Meta:
        verbose_name = 'Komentar Dokumen'
        verbose_name_plural = 'Komentar Dokumen'
        ordering = ['-created_at']


class DocumentAttachment(models.Model):
    """File attachments for documents"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='documents/attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.filename} - {self.document.title}'

    class Meta:
        verbose_name = 'Lampiran Dokumen'
        verbose_name_plural = 'Lampiran Dokumen'
        ordering = ['-uploaded_at']
