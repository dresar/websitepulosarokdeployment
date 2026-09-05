from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.core.validators import EmailValidator
import uuid


class ComplaintCategory(models.Model):
    """Kategori pengaduan"""
    name = models.CharField(max_length=100, verbose_name='Nama Kategori')
    description = models.TextField(blank=True, verbose_name='Deskripsi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Kategori Pengaduan'
        verbose_name_plural = 'Kategori Pengaduan'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Complaint(models.Model):
    """Model untuk pengaduan masyarakat"""
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('in_review', 'Sedang Ditinjau'),
        ('in_progress', 'Sedang Diproses'),
        ('resolved', 'Selesai'),
        ('rejected', 'Ditolak'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Rendah'),
        ('medium', 'Sedang'),
        ('high', 'Tinggi'),
        ('urgent', 'Mendesak'),
    ]
    
    # Identifikasi
    complaint_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='ID Pengaduan')
    
    # Data Pelapor
    reporter_name = models.CharField(max_length=200, verbose_name='Nama Pelapor')
    reporter_email = models.EmailField(validators=[EmailValidator()], verbose_name='Email Pelapor')
    reporter_phone = models.CharField(max_length=20, blank=True, verbose_name='Nomor Telepon')
    reporter_address = models.TextField(blank=True, verbose_name='Alamat Pelapor')
    
    # Detail Pengaduan
    category = models.ForeignKey(ComplaintCategory, on_delete=models.CASCADE, verbose_name='Kategori')
    title = models.CharField(max_length=200, verbose_name='Judul Pengaduan')
    description = models.TextField(verbose_name='Deskripsi Pengaduan')
    location = models.CharField(max_length=200, blank=True, verbose_name='Lokasi Kejadian')
    incident_date = models.DateTimeField(blank=True, null=True, verbose_name='Tanggal Kejadian')
    
    # Status dan Prioritas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='Prioritas')
    
    # File Pendukung
    attachment = models.FileField(upload_to='complaints/attachments/', blank=True, null=True, verbose_name='File Lampiran')
    
    # Penanganan
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Ditugaskan Kepada')
    admin_notes = models.TextField(blank=True, verbose_name='Catatan Admin')
    resolution = models.TextField(blank=True, verbose_name='Penyelesaian')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Dibuat')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Tanggal Diperbarui')
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name='Tanggal Selesai')
    
    # Rating dan Feedback
    rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name='Rating')
    feedback = models.TextField(blank=True, verbose_name='Feedback Pelapor')
    
    class Meta:
        verbose_name = 'Pengaduan'
        verbose_name_plural = 'Pengaduan'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.complaint_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
    
    @property
    def priority_display(self):
        return dict(self.PRIORITY_CHOICES)[self.priority]


class ComplaintUpdate(models.Model):
    """Update status pengaduan"""
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='updates', verbose_name='Pengaduan')
    status = models.CharField(max_length=20, choices=Complaint.STATUS_CHOICES, verbose_name='Status')
    message = models.TextField(verbose_name='Pesan Update')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Diperbarui Oleh')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Update')
    
    class Meta:
        verbose_name = 'Update Pengaduan'
        verbose_name_plural = 'Update Pengaduan'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update {self.complaint.complaint_id} - {self.status}"


class ChatSession(models.Model):
    """Sesi chat untuk sistem chat otomatis"""
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_name = models.CharField(max_length=100, blank=True, verbose_name='Nama Pengguna')
    user_email = models.EmailField(blank=True, verbose_name='Email Pengguna')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sesi Chat'
        verbose_name_plural = 'Sesi Chat'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat {self.session_id} - {self.user_name or 'Anonymous'}"


class ChatMessage(models.Model):
    """Pesan dalam chat"""
    MESSAGE_TYPES = [
        ('user', 'Pengguna'),
        ('bot', 'Bot'),
        ('admin', 'Admin'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='Sesi Chat')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, verbose_name='Tipe Pesan')
    content = models.TextField(verbose_name='Isi Pesan')
    is_read = models.BooleanField(default=False, verbose_name='Sudah Dibaca')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Pesan Chat'
        verbose_name_plural = 'Pesan Chat'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."


class ChatIntent(models.Model):
    """Intent untuk machine learning chat bot"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Nama Intent')
    description = models.TextField(blank=True, verbose_name='Deskripsi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Intent Chat'
        verbose_name_plural = 'Intent Chat'
    
    def __str__(self):
        return self.name


class ChatPattern(models.Model):
    """Pattern untuk mengenali intent"""
    intent = models.ForeignKey(ChatIntent, on_delete=models.CASCADE, related_name='patterns', verbose_name='Intent')
    pattern = models.CharField(max_length=200, verbose_name='Pattern')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    
    class Meta:
        verbose_name = 'Pattern Chat'
        verbose_name_plural = 'Pattern Chat'
    
    def __str__(self):
        return f"{self.intent.name}: {self.pattern}"


class ChatResponse(models.Model):
    """Response untuk setiap intent"""
    intent = models.ForeignKey(ChatIntent, on_delete=models.CASCADE, related_name='responses', verbose_name='Intent')
    response = models.TextField(verbose_name='Response')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    
    class Meta:
        verbose_name = 'Response Chat'
        verbose_name_plural = 'Response Chat'
    
    def __str__(self):
        return f"{self.intent.name}: {self.response[:50]}..."


class Notification(models.Model):
    """Notifikasi sistem"""
    NOTIFICATION_TYPES = [
        ('complaint_new', 'Pengaduan Baru'),
        ('complaint_update', 'Update Pengaduan'),
        ('complaint_resolved', 'Pengaduan Selesai'),
        ('chat_new', 'Chat Baru'),
        ('system', 'Sistem'),
    ]
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='Tipe Notifikasi')
    title = models.CharField(max_length=200, verbose_name='Judul')
    message = models.TextField(verbose_name='Pesan')
    recipient_email = models.EmailField(verbose_name='Email Penerima')
    is_sent = models.BooleanField(default=False, verbose_name='Sudah Dikirim')
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name='Tanggal Dikirim')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Relasi opsional
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Pengaduan')
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Sesi Chat')
    
    class Meta:
        verbose_name = 'Notifikasi'
        verbose_name_plural = 'Notifikasi'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient_email}"


class ComplaintVerification(models.Model):
    """Model untuk verifikasi pengaduan"""
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Menunggu Verifikasi'),
        ('in_progress', 'Sedang Diverifikasi'),
        ('verified', 'Terverifikasi'),
        ('rejected', 'Ditolak'),
        ('requires_info', 'Memerlukan Informasi Tambahan'),
    ]
    
    VERIFICATION_TYPES = [
        ('initial', 'Verifikasi Awal'),
        ('field', 'Verifikasi Lapangan'),
        ('document', 'Verifikasi Dokumen'),
        ('follow_up', 'Tindak Lanjut'),
        ('final', 'Verifikasi Final'),
    ]
    
    # Relasi
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='verifications', verbose_name='Pengaduan')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Diverifikasi Oleh')
    
    # Detail Verifikasi
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES, default='initial', verbose_name='Jenis Verifikasi')
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending', verbose_name='Status Verifikasi')
    
    # Hasil Verifikasi
    verification_notes = models.TextField(verbose_name='Catatan Verifikasi')
    verification_result = models.TextField(blank=True, verbose_name='Hasil Verifikasi')
    supporting_evidence = models.TextField(blank=True, verbose_name='Bukti Pendukung')
    
    # Tindakan
    recommended_action = models.TextField(blank=True, verbose_name='Rekomendasi Tindakan')
    priority_level = models.CharField(max_length=20, choices=Complaint.PRIORITY_CHOICES, default='medium', verbose_name='Tingkat Prioritas')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Dibuat')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Tanggal Diperbarui')
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name='Tanggal Diverifikasi')
    
    # Follow-up
    requires_follow_up = models.BooleanField(default=False, verbose_name='Memerlukan Tindak Lanjut')
    follow_up_date = models.DateTimeField(blank=True, null=True, verbose_name='Tanggal Tindak Lanjut')
    follow_up_notes = models.TextField(blank=True, verbose_name='Catatan Tindak Lanjut')
    
    class Meta:
        verbose_name = 'Verifikasi Pengaduan'
        verbose_name_plural = 'Verifikasi Pengaduan'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verifikasi {self.complaint.complaint_id} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if self.status == 'verified' and not self.verified_at:
            self.verified_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def status_display(self):
        return dict(self.VERIFICATION_STATUS_CHOICES)[self.status]
    
    @property
    def type_display(self):
        return dict(self.VERIFICATION_TYPES)[self.verification_type]


class Contact(models.Model):
    """Model untuk pesan kontak dari masyarakat"""
    STATUS_CHOICES = [
        ('new', 'Baru'),
        ('read', 'Sudah Dibaca'),
        ('replied', 'Sudah Dibalas'),
        ('closed', 'Ditutup'),
    ]
    
    SUBJECT_CHOICES = [
        ('general', 'Pertanyaan Umum'),
        ('service', 'Layanan Desa'),
        ('complaint', 'Keluhan'),
        ('suggestion', 'Saran'),
        ('information', 'Permintaan Informasi'),
        ('other', 'Lainnya'),
    ]
    
    # Identifikasi
    contact_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='ID Kontak')
    
    # Data Pengirim
    sender_name = models.CharField(max_length=200, verbose_name='Nama Pengirim')
    sender_email = models.EmailField(validators=[EmailValidator()], verbose_name='Email Pengirim')
    sender_phone = models.CharField(max_length=20, blank=True, verbose_name='Nomor Telepon')
    is_anonymous = models.BooleanField(default=False, verbose_name='Anonim')
    
    # Detail Pesan
    subject_type = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general', verbose_name='Jenis Subjek')
    subject = models.CharField(max_length=200, verbose_name='Subjek')
    message = models.TextField(verbose_name='Pesan')
    
    # Status dan Penanganan
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Status')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Ditugaskan Kepada')
    admin_notes = models.TextField(blank=True, verbose_name='Catatan Admin')
    reply_message = models.TextField(blank=True, verbose_name='Balasan')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Dibuat')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Tanggal Diperbarui')
    read_at = models.DateTimeField(blank=True, null=True, verbose_name='Tanggal Dibaca')
    replied_at = models.DateTimeField(blank=True, null=True, verbose_name='Tanggal Dibalas')
    
    class Meta:
        verbose_name = 'Pesan Kontak'
        verbose_name_plural = 'Pesan Kontak'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contact_id} - {self.subject}"
    
    def save(self, *args, **kwargs):
        if self.status == 'read' and not self.read_at:
            self.read_at = timezone.now()
        elif self.status == 'replied' and not self.replied_at:
            self.replied_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
    
    @property
    def subject_type_display(self):
        return dict(self.SUBJECT_CHOICES)[self.subject_type]
    
    @property
    def display_name(self):
        return 'Anonim' if self.is_anonymous else self.sender_name
