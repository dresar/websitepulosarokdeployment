from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LayananFeedback(models.Model):
    """Model for storing user feedback about services"""
    CATEGORY_CHOICES = [
        ('complaint', 'Keluhan'),
        ('suggestion', 'Saran'),
        ('question', 'Pertanyaan'),
        ('praise', 'Pujian'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('read', 'Sudah Dibaca'),
        ('replied', 'Sudah Dibalas'),
        ('closed', 'Ditutup'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nama")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telepon")
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='suggestion',
        verbose_name="Kategori"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    subject = models.CharField(max_length=200, verbose_name="Subjek")
    message = models.TextField(verbose_name="Pesan")
    reply = models.TextField(blank=True, verbose_name="Balasan")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Dibalas Pada")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    
    class Meta:
        verbose_name = "Feedback Layanan"
        verbose_name_plural = "Feedback Layanan"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class LayananFAQ(models.Model):
    """Model for frequently asked questions"""
    CATEGORY_CHOICES = [
        ('general', 'Umum'),
        ('documents', 'Dokumen'),
        ('services', 'Layanan'),
        ('technical', 'Teknis'),
    ]
    
    question = models.TextField(verbose_name="Pertanyaan")
    answer = models.TextField(verbose_name="Jawaban")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name="Kategori"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    order = models.PositiveIntegerField(default=0, verbose_name="Urutan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    
    class Meta:
        verbose_name = "FAQ Layanan"
        verbose_name_plural = "FAQ Layanan"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.question[:50] + "..." if len(self.question) > 50 else self.question


class LayananContact(models.Model):
    """Model for contact information"""
    name = models.CharField(max_length=100, default="Kontak", verbose_name="Nama")
    position = models.CharField(max_length=100, default="Staff", verbose_name="Jabatan")
    phone = models.CharField(max_length=20, default="0000000000", verbose_name="Telepon")
    email = models.EmailField(default="kontak@desa.id", verbose_name="Email")
    department = models.CharField(max_length=100, default="Umum", verbose_name="Departemen")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    notes = models.TextField(blank=True, verbose_name="Catatan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    
    class Meta:
        verbose_name = "Kontak Layanan"
        verbose_name_plural = "Kontak Layanan"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.name} - {self.position}"


class LayananService(models.Model):
    """Model for service information"""
    CATEGORY_CHOICES = [
        ('documents', 'Dokumen'),
        ('health', 'Kesehatan'),
        ('business', 'Bisnis'),
        ('tourism', 'Pariwisata'),
        ('other', 'Lainnya'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nama Layanan")
    description = models.TextField(verbose_name="Deskripsi")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Kategori"
    )
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icon")
    url = models.URLField(blank=True, verbose_name="URL")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    order = models.PositiveIntegerField(default=0, verbose_name="Urutan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    
    class Meta:
        verbose_name = "Layanan"
        verbose_name_plural = "Layanan"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.name


class LayananDocumentRequest(models.Model):
    """Model for layanan document requests"""
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('cancelled', 'Dibatalkan'),
    ]
    
    # Personal Information
    full_name = models.CharField(max_length=200, verbose_name="Nama Lengkap")
    nik = models.CharField(max_length=16, verbose_name="NIK")
    phone = models.CharField(max_length=20, verbose_name="Nomor Telepon")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(verbose_name="Alamat Lengkap")
    
    # Document Information
    DOCUMENT_TYPE_CHOICES = [
        ('surat_keterangan', 'Surat Keterangan'),
        ('surat_pengantar', 'Surat Pengantar'),
        ('surat_izin', 'Surat Izin'),
        ('surat_rekomendasi', 'Surat Rekomendasi'),
        ('surat_kepemilikan', 'Surat Kepemilikan'),
        ('surat_lainnya', 'Surat Lainnya'),
    ]
    
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        default='surat_keterangan',
        verbose_name="Jenis Dokumen"
    )
    purpose = models.CharField(max_length=200, verbose_name="Tujuan Penggunaan")
    description = models.TextField(blank=True, verbose_name="Keterangan Tambahan")
    
    # File Uploads
    ktp_file = models.FileField(upload_to='layanan/ktp/', blank=True, verbose_name="Fotokopi KTP")
    kk_file = models.FileField(upload_to='layanan/kk/', blank=True, verbose_name="Fotokopi KK")
    additional_file = models.FileField(upload_to='layanan/additional/', blank=True, verbose_name="Dokumen Tambahan")
    
    # Status and Processing
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    rejection_reason = models.TextField(blank=True, verbose_name="Alasan Penolakan")
    processed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Diproses Oleh"
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Diproses Pada")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    
    class Meta:
        verbose_name = "Permintaan Dokumen Layanan"
        verbose_name_plural = "Permintaan Dokumen Layanan"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.get_document_type_display()}"
