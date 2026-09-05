from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Import Penduduk from references app
try:
    from references.models import Penduduk
    print("Business app: Using references.models.Penduduk")
except ImportError as e:
    print(f"Business app: Could not import references.models.Penduduk: {e}")
    # Fallback to letters app if references is not available
    try:
        from letters.models import Penduduk
        print("Business app: Using letters.models.Penduduk")
    except ImportError as e2:
        print(f"Business app: Could not import letters.models.Penduduk: {e2}")
        # Temporary Penduduk model for business app
        class Penduduk(models.Model):
            nama = models.CharField(max_length=200)
            nik = models.CharField(max_length=16, unique=True)
            alamat = models.TextField(blank=True)
            telepon = models.CharField(max_length=20, blank=True)
            email = models.EmailField(blank=True)
            created_at = models.DateTimeField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)
            
            class Meta:
                verbose_name = 'Penduduk'
                verbose_name_plural = 'Penduduk'
            
            def __str__(self):
                return self.nama

User = get_user_model()

class BusinessCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Kategori Bisnis'
        verbose_name_plural = 'Kategori Bisnis'

class Business(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('umkm', 'UMKM'),
        ('koperasi', 'Koperasi'),
        ('bumg', 'BUMG'),
        ('layanan_jasa', 'Layanan Jasa'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Menunggu Persetujuan'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('inactive', 'Tidak Aktif'),
    ]

    name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE, related_name='businesses')
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Bisnis'
        verbose_name_plural = 'Bisnis'

class BusinessOwner(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='owners')
    owner = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='businesses')
    is_primary = models.BooleanField(default=True)
    ownership_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.nama} - {self.business.name}"

    class Meta:
        verbose_name = 'Pemilik Bisnis'
        verbose_name_plural = 'Pemilik Bisnis'

class BusinessProduct(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Produk Bisnis'
        verbose_name_plural = 'Produk Bisnis'

class BusinessFinance(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='finance')
    initial_capital = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monthly_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monthly_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Finance - {self.business.name}"

    class Meta:
        verbose_name = 'Keuangan Bisnis'
        verbose_name_plural = 'Keuangan Bisnis'

# UMKM Model
class UKM(models.Model):
    SKALA_CHOICES = [
        ('mikro', 'Mikro'),
        ('kecil', 'Kecil'),
        ('menengah', 'Menengah'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('pending', 'Menunggu Persetujuan'),
    ]

    nama_usaha = models.CharField(max_length=200)
    pemilik = models.CharField(max_length=200)
    nik_pemilik = models.CharField(max_length=16, blank=True)
    jenis_usaha = models.CharField(max_length=200)
    skala_usaha = models.CharField(max_length=20, choices=SKALA_CHOICES)
    tanggal_mulai = models.DateField()
    nomor_izin = models.CharField(max_length=100, blank=True)
    alamat_usaha = models.TextField()
    alamat_pemilik = models.TextField()
    telepon = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    modal_awal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    omzet_bulanan = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    jumlah_karyawan = models.PositiveIntegerField(default=0)
    produk_utama = models.TextField()
    target_pasar = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_usaha

    def get_skala_usaha_display(self):
        return dict(self.SKALA_CHOICES).get(self.skala_usaha, self.skala_usaha)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    class Meta:
        verbose_name = 'UMKM'
        verbose_name_plural = 'UMKM'

# Koperasi Model
class Koperasi(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('pending', 'Menunggu Persetujuan'),
    ]

    nama = models.CharField(max_length=200, verbose_name="Nama Koperasi", default="Koperasi")
    ketua = models.CharField(max_length=200)
    sekretaris = models.CharField(max_length=200, blank=True)
    bendahara = models.CharField(max_length=200, blank=True)
    alamat = models.TextField()
    telepon = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    tanggal_berdiri = models.DateField()
    nomor_badan_hukum = models.CharField(max_length=100, blank=True)
    jenis_koperasi = models.CharField(max_length=100, blank=True, verbose_name="Jenis Koperasi")
    jumlah_anggota = models.PositiveIntegerField(default=0)
    modal_dasar = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Modal Dasar")
    modal_disetor = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Modal Disetor")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    class Meta:
        verbose_name = 'Koperasi'
        verbose_name_plural = 'Koperasi'

# BUMG Model
class BUMG(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('pending', 'Menunggu Persetujuan'),
    ]

    nama = models.CharField(max_length=200)
    nomor_sk = models.CharField(max_length=100, blank=True)
    tanggal_sk = models.DateField()
    alamat = models.TextField()
    direktur = models.CharField(max_length=100)
    komisaris = models.CharField(max_length=100, blank=True)
    modal_dasar = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    modal_disetor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    bidang_usaha = models.TextField()
    telepon = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    class Meta:
        verbose_name = 'BUMG'
        verbose_name_plural = 'BUMG'

# Layanan Jasa Model
class LayananJasa(models.Model):
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('tidak_aktif', 'Tidak Aktif'),
        ('pending', 'Menunggu Persetujuan'),
    ]

    nama = models.CharField(max_length=200, verbose_name="Nama Layanan")
    penyedia = models.CharField(max_length=200)
    alamat = models.TextField()
    telepon = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    kategori = models.CharField(max_length=200, verbose_name="Kategori Layanan")
    deskripsi = models.TextField(verbose_name="Deskripsi Layanan")
    deskripsi_layanan = models.TextField(blank=True, verbose_name="Deskripsi Layanan (Lama)")
    tarif_layanan = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Tarif Layanan")
    jam_operasional = models.CharField(max_length=100, blank=True, verbose_name="Jam Operasional")
    pengalaman = models.CharField(max_length=100, blank=True, verbose_name="Pengalaman")
    harga_min = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Harga Minimum")
    harga_max = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Harga Maksimum")
    satuan_harga = models.CharField(max_length=50, blank=True, verbose_name="Satuan Harga")
    waktu_layanan = models.CharField(max_length=100, blank=True, verbose_name="Waktu Layanan")
    area_layanan = models.CharField(max_length=200, blank=True, verbose_name="Area Layanan")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Rating")
    website = models.URLField(blank=True, verbose_name="Website")
    keunggulan = models.TextField(blank=True, verbose_name="Keunggulan")
    syarat_ketentuan = models.TextField(blank=True, verbose_name="Syarat & Ketentuan")
    sertifikat = models.CharField(max_length=200, blank=True, verbose_name="Sertifikat")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    keterangan = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    class Meta:
        verbose_name = 'Layanan Jasa'
        verbose_name_plural = 'Layanan Jasa'

# Aset Model
class Aset(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    acquisition_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Aset'
        verbose_name_plural = 'Aset'

# Business Page Header Model
class BusinessPageHeader(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(upload_to='business_headers/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Header Halaman Bisnis'
        verbose_name_plural = 'Header Halaman Bisnis'

# Jenis Koperasi Model
class JenisKoperasi(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    deskripsi = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = 'Jenis Koperasi'
        verbose_name_plural = 'Jenis Koperasi'