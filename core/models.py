from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.utils import timezone
from django.core.cache import cache
import os
import shutil


class MenuPermission(models.Model):
    """Permission model for admin panel menu access"""
    MODULE_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('references', 'Data Referensi'),
        ('beneficiaries', 'Penerima Bantuan'),
        ('business', 'Usaha'),
        ('complaints', 'Keluhan'),
        ('documents', 'Dokumen'),
        ('tourism', 'Wisata'),
        ('posyandu', 'Posyandu'),
        ('news', 'Berita'),
        ('village_profile', 'Profil Desa'),
        ('organization', 'Organisasi'),
        ('layanan', 'Layanan'),
        ('reports', 'Laporan'),
        ('settings', 'Pengaturan'),
    ]
    
    ACTION_CHOICES = [
        ('view', 'Lihat'),
        ('add', 'Tambah'),
        ('change', 'Ubah'),
        ('delete', 'Hapus'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    codename = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Menu Permission'
        verbose_name_plural = 'Menu Permissions'
        unique_together = ['module', 'action']
    
    def __str__(self):
        return f"{self.get_module_display()} - {self.get_action_display()}"


class Role(models.Model):
    """Role model for multi-role authentication system"""
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('data_manager', 'Data Manager'),
        ('beneficiary_manager', 'Manager Penerima Bantuan'),
        ('business_manager', 'Manager Usaha'),
        ('complaint_manager', 'Manager Keluhan'),
        ('document_manager', 'Manager Dokumen'),
        ('tourism_manager', 'Manager Wisata'),
        ('posyandu_manager', 'Manager Posyandu'),
        ('news_manager', 'Manager Berita'),
        ('village_profile_manager', 'Manager Profil Desa'),
        ('organization_manager', 'Manager Organisasi'),
        ('karang_taruna_manager', 'Manager Karang Taruna'),
        ('kepemudaan_manager', 'Manager Kepemudaan'),
        ('pkk_manager', 'Manager PKK'),
        ('lembaga_adat_manager', 'Manager Lembaga Adat'),
        ('perangkat_desa_manager', 'Manager Perangkat Desa'),
        ('village_staff', 'Staff Desa'),
        ('moderator', 'Moderator'),
        ('viewer', 'Viewer'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    menu_permissions = models.ManyToManyField(MenuPermission, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['display_name']
    
    def __str__(self):
        return self.display_name
    
    def has_menu_permission(self, module, action):
        """Check if role has permission for module and action"""
        return self.menu_permissions.filter(module=module, action=action, is_active=True).exists()


class CustomUser(AbstractUser):
    """Extended user model for village staff"""
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_village_staff = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role, through='UserRole', through_fields=('user', 'role'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.position}"
    
    def has_role(self, role_name):
        """Check if user has specific role"""
        return self.roles.filter(name=role_name, is_active=True).exists()
    
    def get_active_roles(self):
        """Get all active roles for user"""
        return self.roles.filter(is_active=True)
    
    def has_menu_permission(self, module, action):
        """Check if user has menu permission"""
        for role in self.get_active_roles():
            if role.has_menu_permission(module, action):
                return True
        return False
    
    def get_menu_permissions(self):
        """Get all menu permissions for user"""
        permissions = set()
        for role in self.get_active_roles():
            for perm in role.menu_permissions.filter(is_active=True):
                permissions.add(perm)
        return permissions


class UserRole(models.Model):
    """Through model for User-Role relationship"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'role']
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
    
    def __str__(self):
        return f"{self.user.username} - {self.role.display_name}"


class UserProfile(models.Model):
    """Additional profile information for users"""
    GENDER_CHOICES = [
        ('M', 'Laki-laki'),
        ('F', 'Perempuan'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_id = models.CharField(max_length=64, unique=True, blank=True, help_text="Secure unique profile identifier")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True, help_text="Foto profil pengguna")
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Nomor telepon")
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()
    
    def generate_secure_profile_id(self):
        """Generate a secure, unique profile ID"""
        import secrets
        import hashlib
        import time
        
        # Create a unique string combining user data and timestamp
        unique_string = f"{self.user.id}_{self.user.username}_{time.time()}_{secrets.token_hex(16)}"
        
        # Generate SHA-256 hash for security
        secure_id = hashlib.sha256(unique_string.encode()).hexdigest()
        
        # Add a prefix for identification
        return f"PROF_{secure_id[:32]}"
    
    def save(self, *args, **kwargs):
        """Override save to generate secure profile ID if not exists"""
        if not self.profile_id:
            self.profile_id = self.generate_secure_profile_id()
        super().save(*args, **kwargs)


class LoginHistory(models.Model):
    """Model untuk menyimpan riwayat login pengguna"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField(help_text="Alamat IP saat login")
    user_agent = models.TextField(help_text="User agent browser")
    browser = models.CharField(max_length=50, blank=True, null=True, help_text="Nama browser")
    os = models.CharField(max_length=50, blank=True, null=True, help_text="Sistem operasi")
    device = models.CharField(max_length=50, blank=True, null=True, help_text="Jenis perangkat")
    location = models.CharField(max_length=100, blank=True, null=True, help_text="Lokasi berdasarkan IP")
    login_time = models.DateTimeField(auto_now_add=True, help_text="Waktu login")
    logout_time = models.DateTimeField(blank=True, null=True, help_text="Waktu logout")
    is_successful = models.BooleanField(default=True, help_text="Apakah login berhasil")
    failure_reason = models.CharField(max_length=200, blank=True, null=True, help_text="Alasan gagal login")

    class Meta:
        ordering = ['-login_time']
        verbose_name = 'Riwayat Login'
        verbose_name_plural = 'Riwayat Login'

    def __str__(self):
        return f"{self.user.username} - {self.login_time.strftime('%d/%m/%Y %H:%M')}"

    @property
    def session_duration(self):
        """Calculate session duration in minutes"""
        if self.logout_time and self.login_time:
            duration = self.logout_time - self.login_time
            return duration.total_seconds() / 60
        return None


class WebsiteSettings(models.Model):
    """Unified website settings model - minimal and efficient"""
    THEME_CHOICES = [
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('auto', 'Auto (System)')
    ]
    
    LANGUAGE_CHOICES = [
        ('id', 'Bahasa Indonesia'),
        ('en', 'English'),
        ('jv', 'Bahasa Jawa')
    ]
    
    # Basic Website Info
    site_name = models.CharField(max_length=200, default='Website Desa Pulosarok')
    site_description = models.TextField(blank=True, null=True, help_text="Deskripsi singkat website yang akan ditampilkan di halaman utama")
    site_logo = models.ImageField(upload_to='website/', blank=True, null=True)
    site_favicon = models.ImageField(upload_to='website/', blank=True, null=True)
    
    # Contact Information
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)
    
    # Social Media
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    
    # Appearance
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    primary_color = models.CharField(max_length=7, default='#3B82F6')
    secondary_color = models.CharField(max_length=7, default='#10B981')
    
    # Localization
    default_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='id')
    timezone = models.CharField(max_length=50, default='Asia/Jakarta')
    
    # SEO Settings
    meta_keywords = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True)
    
    # System Settings
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, null=True)
    allow_registration = models.BooleanField(default=False)
    max_file_upload_size = models.IntegerField(default=10)
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Website Settings'
        verbose_name_plural = 'Website Settings'
    
    def __str__(self):
        return f"Website Settings - {self.site_name}"
    
    @classmethod
    def get_settings(cls):
        """Get or create website settings singleton"""
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'Website Desa Pulosarok'
            }
        )
        return settings


class HeroImage(models.Model):
    """Model sederhana untuk gambar hero"""
    PAGE_CHOICES = [
        ('home', 'Homepage'),
        ('events', 'Kegiatan'),
        ('news', 'Berita'),
        ('tourism', 'Wisata'),
        ('umkm', 'UMKM'),
        ('organization', 'Organisasi'),
        ('correspondence', 'Surat Menyurat'),
        ('gallery', 'Galeri'),
        ('complaints', 'Keluhan'),
        ('layanan', 'Layanan'),
        ('posyandu', 'Posyandu'),
        ('bantuna', 'Bantuna'),
        ('business', 'Bisnis'),
        ('koperasi', 'Koperasi'),
        ('bumg', 'BUMG'),
        ('layanan_jasa', 'Layanan Jasa'),
    ]
    
    name = models.CharField(max_length=200, help_text='Nama gambar hero')
    page = models.CharField(max_length=20, choices=PAGE_CHOICES, default='home', help_text='Halaman yang menggunakan gambar ini')
    image = models.ImageField(upload_to='hero_images/%Y/%m/%d/', help_text='Gambar hero')
    is_active = models.BooleanField(default=True, help_text='Status aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hero Image'
        verbose_name_plural = 'Hero Images'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_page_display()}"


# Duplicate WebsiteSettings model removed - using the first one above
class WebsiteSettingsDuplicate(models.Model):
    """DUPLICATE MODEL - TO BE REMOVED"""
    
    # Website Basic Info
    site_name = models.CharField(max_length=200, default='Website Desa Pulosarok', verbose_name='Nama Website')
    site_tagline = models.CharField(max_length=300, default='Desa Digital Terdepan di Aceh Singkil', verbose_name='Tagline Website')
    site_description = models.TextField(default='Website resmi Desa Pulosarok, Kecamatan Singkil, Kabupaten Aceh Singkil, Aceh', verbose_name='Deskripsi Website')
    site_keywords = models.CharField(max_length=500, default='desa pulosarok, aceh singkil, website desa, pemerintahan desa', verbose_name='Keywords SEO')
    
    # Contact Information
    contact_phone = models.CharField(max_length=20, default='0852-1234-5678', verbose_name='Nomor Telepon')
    contact_email = models.EmailField(default='info@pulosarok.desa.id', verbose_name='Email Kontak')
    contact_address = models.TextField(default='Desa Pulosarok, Kecamatan Singkil, Kabupaten Aceh Singkil, Aceh', verbose_name='Alamat Lengkap')
    contact_whatsapp = models.CharField(max_length=20, default='0852-1234-5678', verbose_name='WhatsApp')
    
    # Social Media
    facebook_url = models.URLField(blank=True, null=True, verbose_name='Facebook')
    instagram_url = models.URLField(blank=True, null=True, verbose_name='Instagram')
    youtube_url = models.URLField(blank=True, null=True, verbose_name='YouTube')
    twitter_url = models.URLField(blank=True, null=True, verbose_name='Twitter')
    
    # Logo & Branding
    logo = models.ImageField(upload_to='settings/logo/', blank=True, null=True, verbose_name='Logo Website')
    favicon = models.ImageField(upload_to='settings/favicon/', blank=True, null=True, verbose_name='Favicon')
    
    # Cache Settings
    enable_cache = models.BooleanField(default=True, verbose_name='Aktifkan Cache')
    cache_duration = models.PositiveIntegerField(default=300, verbose_name='Durasi Cache (detik)')
    enable_static_cache = models.BooleanField(default=True, verbose_name='Cache Static Files')
    
    # Media Settings
    max_upload_size = models.PositiveIntegerField(default=10, verbose_name='Maksimal Ukuran Upload (MB)')
    allowed_image_formats = models.CharField(max_length=200, default='jpg,jpeg,png,gif,webp', verbose_name='Format Gambar Diizinkan')
    allowed_document_formats = models.CharField(max_length=200, default='pdf,doc,docx,xls,xlsx', verbose_name='Format Dokumen Diizinkan')
    enable_image_compression = models.BooleanField(default=True, verbose_name='Kompresi Gambar Otomatis')
    image_quality = models.PositiveIntegerField(default=85, verbose_name='Kualitas Gambar (%)')
    
    # Security Settings
    enable_maintenance_mode = models.BooleanField(default=False, verbose_name='Mode Maintenance')
    maintenance_message = models.TextField(default='Website sedang dalam perbaikan. Terima kasih atas pengertian Anda.', verbose_name='Pesan Maintenance')
    enable_ssl_redirect = models.BooleanField(default=True, verbose_name='Redirect ke HTTPS')
    max_login_attempts = models.PositiveIntegerField(default=5, verbose_name='Maksimal Percobaan Login')
    
    # Performance Settings
    enable_gzip_compression = models.BooleanField(default=True, verbose_name='Kompresi GZIP')
    enable_minify_css = models.BooleanField(default=True, verbose_name='Minify CSS')
    enable_minify_js = models.BooleanField(default=True, verbose_name='Minify JavaScript')
    enable_cdn = models.BooleanField(default=False, verbose_name='Gunakan CDN')
    cdn_url = models.URLField(blank=True, null=True, verbose_name='URL CDN')
    
    # Analytics & Tracking
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='Google Analytics ID')
    google_tag_manager_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='Google Tag Manager ID')
    facebook_pixel_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='Facebook Pixel ID')
    
    # Email Settings
    smtp_host = models.CharField(max_length=200, blank=True, null=True, verbose_name='SMTP Host')
    smtp_port = models.PositiveIntegerField(default=587, verbose_name='SMTP Port')
    smtp_username = models.CharField(max_length=200, blank=True, null=True, verbose_name='SMTP Username')
    smtp_password = models.CharField(max_length=200, blank=True, null=True, verbose_name='SMTP Password')
    smtp_use_tls = models.BooleanField(default=True, verbose_name='Gunakan TLS')
    
    # Notification Settings
    enable_email_notifications = models.BooleanField(default=True, verbose_name='Notifikasi Email')
    enable_sms_notifications = models.BooleanField(default=False, verbose_name='Notifikasi SMS')
    admin_email = models.EmailField(default='admin@pulosarok.desa.id', verbose_name='Email Admin')
    
    # Backup Settings
    enable_auto_backup = models.BooleanField(default=True, verbose_name='Backup Otomatis')
    backup_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Harian'),
        ('weekly', 'Mingguan'),
        ('monthly', 'Bulanan'),
    ], default='daily', verbose_name='Frekuensi Backup')
    backup_retention_days = models.PositiveIntegerField(default=30, verbose_name='Retensi Backup (hari)')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pengaturan Website'
        verbose_name_plural = 'Pengaturan Website'
    
    def __str__(self):
        return f"Pengaturan Website - {self.site_name}"
    
    def save(self, *args, **kwargs):
        # Clear cache when settings are updated
        cache.clear()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create website settings"""
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={}
        )
        return settings
    
    def clear_cache(self):
        """Clear all cache"""
        cache.clear()
        return True
    
    def clear_static_files(self):
        """Clear static files cache"""
        try:
            from django.conf import settings
            static_root = settings.STATIC_ROOT
            if os.path.exists(static_root):
                shutil.rmtree(static_root)
                os.makedirs(static_root, exist_ok=True)
            return True
        except Exception as e:
            return False
    
    def clear_media_cache(self):
        """Clear media files cache"""
        try:
            from django.conf import settings
            media_root = settings.MEDIA_ROOT
            # Clear only cache files, not all media
            cache_dirs = ['cache', 'thumbnails', 'compressed']
            for cache_dir in cache_dirs:
                cache_path = os.path.join(media_root, cache_dir)
                if os.path.exists(cache_path):
                    shutil.rmtree(cache_path)
            return True
        except Exception as e:
            return False


