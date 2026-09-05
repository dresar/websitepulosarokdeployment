from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class VillageProfilePageHeader(models.Model):
    title = models.CharField(
        max_length=200, 
        default='Profil Desa', 
        verbose_name="Judul Halaman"
    )
    description = models.TextField(
        default='Mengenal lebih dekat sejarah, budaya, dan kehidupan masyarakat desa kami.',
        verbose_name="Deskripsi Halaman"
    )
    background_image = models.ImageField(
        upload_to='village_profile/page_headers/', 
        blank=True, 
        null=True, 
        verbose_name="Gambar Background"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Header Halaman Profil Desa"
        verbose_name_plural = "Header Halaman Profil Desa"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# Enhanced Village History models with multi-photo support


class VillageHistory(models.Model):
    """Enhanced Village History with comprehensive features"""
    HISTORY_TYPE_CHOICES = [
        ('FOUNDING', 'Sejarah Berdiri'),
        ('DEVELOPMENT', 'Perkembangan'),
        ('CULTURE', 'Budaya & Tradisi'),
        ('ECONOMY', 'Ekonomi'),
        ('SOCIAL', 'Sosial'),
        ('GOVERNMENT', 'Pemerintahan'),
        ('OTHER', 'Lainnya'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Judul")
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="Slug")
    summary = models.TextField(max_length=500, blank=True, null=True, verbose_name="Ringkasan", 
                              help_text="Ringkasan singkat sejarah (maksimal 500 karakter)")
    content = models.TextField(verbose_name="Konten Lengkap")
    history_type = models.CharField(max_length=20, choices=HISTORY_TYPE_CHOICES, default='OTHER', verbose_name="Jenis Sejarah")
    
    # Period information
    period_start = models.CharField(max_length=50, blank=True, null=True, verbose_name="Periode Mulai")
    period_end = models.CharField(max_length=50, blank=True, null=True, verbose_name="Periode Berakhir")
    year_start = models.IntegerField(blank=True, null=True, verbose_name="Tahun Mulai",
                                   validators=[MinValueValidator(1000), MaxValueValidator(2100)])
    year_end = models.IntegerField(blank=True, null=True, verbose_name="Tahun Berakhir",
                                 validators=[MinValueValidator(1000), MaxValueValidator(2100)])
    
    # Main image
    featured_image = models.ImageField(upload_to='village_history/featured/', blank=True, null=True, 
                                     verbose_name="Gambar Utama")
    featured_image_caption = models.CharField(max_length=200, blank=True, null=True, 
                                            verbose_name="Keterangan Gambar Utama")
    
    # Additional information
    source = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sumber",
                            help_text="Sumber informasi sejarah")
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name="Penulis")
    
    # Status and metadata
    is_featured = models.BooleanField(default=False, verbose_name="Unggulan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Jumlah Dilihat")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Sejarah Desa"
        verbose_name_plural = "Sejarah Desa"
        ordering = ['-is_featured', 'year_start', 'period_start']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['history_type']),
            models.Index(fields=['year_start']),
        ]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def period_display(self):
        """Display period in a readable format"""
        if self.year_start and self.year_end:
            return f"{self.year_start} - {self.year_end}"
        elif self.year_start:
            return f"Sejak {self.year_start}"
        elif self.period_start and self.period_end:
            return f"{self.period_start} - {self.period_end}"
        elif self.period_start:
            return self.period_start
        return "Periode tidak diketahui"
    
    @property
    def photo_count(self):
        """Get total number of photos"""
        return self.photos.filter(is_active=True).count()


class VillageHistoryPhoto(models.Model):
    """Multiple photos for Village History"""
    history = models.ForeignKey(VillageHistory, on_delete=models.CASCADE, related_name='photos', verbose_name="Sejarah")
    image = models.ImageField(upload_to='village_history/photos/', verbose_name="Foto")
    caption = models.CharField(max_length=200, blank=True, null=True, verbose_name="Keterangan")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    
    # Photo metadata
    photographer = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fotografer")
    photo_date = models.DateField(blank=True, null=True, verbose_name="Tanggal Foto")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="Lokasi")
    
    # Display options
    is_featured = models.BooleanField(default=False, verbose_name="Foto Unggulan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Urutan Tampil")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Foto Sejarah"
        verbose_name_plural = "Foto Sejarah"
        ordering = ['display_order', '-is_featured', 'created_at']
        indexes = [
            models.Index(fields=['history', 'is_active']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return f"Foto: {self.history.title} - {self.caption or 'Tanpa keterangan'}"


class VillageProfile(models.Model):
    """Main village profile information"""
    name = models.CharField(max_length=100, verbose_name="Nama Desa")
    code = models.CharField(max_length=20, unique=True, verbose_name="Kode Desa")
    district = models.CharField(max_length=100, verbose_name="Kecamatan")
    regency = models.CharField(max_length=100, verbose_name="Kabupaten")
    province = models.CharField(max_length=100, verbose_name="Provinsi")
    postal_code = models.CharField(max_length=10, verbose_name="Kode Pos")
    established_date = models.DateField(blank=True, null=True, verbose_name="Tanggal Berdiri")
    area = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Luas Wilayah (km²)")
    description = models.TextField(verbose_name="Deskripsi Desa")
    profile_description = models.TextField(blank=True, null=True, verbose_name="Profil Desa", 
                                         help_text="Deskripsi singkat profil desa yang akan ditampilkan di bagian atas")
    
    # Vision and Mission
    vision = models.TextField(verbose_name="Visi")
    mission = models.TextField(verbose_name="Misi", help_text="Pisahkan setiap misi dengan baris baru")
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telepon")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    
    # Logo and Images
    logo = models.ImageField(upload_to='village_profile/logo/', blank=True, null=True, verbose_name="Logo Desa")
    profile_image = models.ImageField(upload_to='village_profile/profile/', blank=True, null=True, verbose_name="Gambar Profil Desa")
    
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Profil Desa"
        verbose_name_plural = "Profil Desa"

    def __str__(self):
        return self.name
    
    @property
    def mission_list(self):
        """Return mission as a list"""
        return [m.strip() for m in self.mission.split('\n') if m.strip()]
    
    @property
    def village_head(self):
        """Get village head from officials"""
        try:
            head_official = self.officials.filter(
                position='KEPALA_DESA',
                is_active=True
            ).first()
            return head_official.name if head_official else 'Belum ditentukan'
        except:
            return 'Belum ditentukan'


class VillageGeography(models.Model):
    """Village geography and location information"""
    village = models.OneToOneField(VillageProfile, on_delete=models.CASCADE, related_name='geography', verbose_name="Desa")
    
    # Coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Lintang")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Bujur")
    altitude = models.IntegerField(verbose_name="Ketinggian (mdpl)")
    
    # Climate
    climate = models.CharField(max_length=100, verbose_name="Iklim")
    rainfall = models.IntegerField(verbose_name="Curah Hujan (mm/tahun)")
    temperature_min = models.IntegerField(verbose_name="Suhu Minimum (°C)")
    temperature_max = models.IntegerField(verbose_name="Suhu Maksimum (°C)")
    
    # Topography
    topography = models.CharField(max_length=100, verbose_name="Topografi")
    soil_type = models.CharField(max_length=100, verbose_name="Jenis Tanah")
    
    # Boundaries
    boundary_north = models.CharField(max_length=100, verbose_name="Batas Utara")
    boundary_south = models.CharField(max_length=100, verbose_name="Batas Selatan")
    boundary_east = models.CharField(max_length=100, verbose_name="Batas Timur")
    boundary_west = models.CharField(max_length=100, verbose_name="Batas Barat")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Geografi Desa"
        verbose_name_plural = "Geografi Desa"

    def __str__(self):
        return f"Geografi {self.village.name}"
    
    @property
    def temperature_range(self):
        return f"{self.temperature_min}-{self.temperature_max}"
    
    @property
    def boundaries(self):
        return {
            'north': self.boundary_north,
            'south': self.boundary_south,
            'east': self.boundary_east,
            'west': self.boundary_west
        }


class VillageDemography(models.Model):
    """Village demographic information"""
    village = models.OneToOneField(VillageProfile, on_delete=models.CASCADE, related_name='demography', verbose_name="Desa")
    
    # Population data
    total_population = models.PositiveIntegerField(verbose_name="Total Penduduk")
    male_population = models.PositiveIntegerField(verbose_name="Penduduk Laki-laki")
    female_population = models.PositiveIntegerField(verbose_name="Penduduk Perempuan")
    total_families = models.PositiveIntegerField(verbose_name="Jumlah Keluarga")
    
    # Density and growth
    population_density = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Kepadatan Penduduk (jiwa/km²)")
    growth_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Tingkat Pertumbuhan (%)")
    
    # Age groups
    age_0_14 = models.PositiveIntegerField(default=0, verbose_name="Usia 0-14 tahun")
    age_15_64 = models.PositiveIntegerField(default=0, verbose_name="Usia 15-64 tahun")
    age_65_plus = models.PositiveIntegerField(default=0, verbose_name="Usia 65+ tahun")
    
    # Education levels
    education_none = models.PositiveIntegerField(default=0, verbose_name="Tidak Sekolah")
    education_elementary = models.PositiveIntegerField(default=0, verbose_name="SD")
    education_junior = models.PositiveIntegerField(default=0, verbose_name="SMP")
    education_senior = models.PositiveIntegerField(default=0, verbose_name="SMA")
    education_higher = models.PositiveIntegerField(default=0, verbose_name="Perguruan Tinggi")
    
    # Employment
    employed = models.PositiveIntegerField(default=0, verbose_name="Bekerja")
    unemployed = models.PositiveIntegerField(default=0, verbose_name="Tidak Bekerja")
    
    year = models.IntegerField(verbose_name="Tahun Data")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Demografi Desa"
        verbose_name_plural = "Demografi Desa"
        unique_together = ['village', 'year']

    def __str__(self):
        return f"Demografi {self.village.name} - {self.year}"


class VillageOfficial(models.Model):
    """Village government officials"""
    POSITION_CHOICES = [
        ('KEPALA_DESA', 'Kepala Desa'),
        ('SEKRETARIS', 'Sekretaris Desa'),
        ('BENDAHARA', 'Bendahara Desa'),
        ('KAUR_PEMERINTAHAN', 'Kaur Pemerintahan'),
        ('KAUR_PEMBANGUNAN', 'Kaur Pembangunan'),
        ('KAUR_KESRA', 'Kaur Kesejahteraan Rakyat'),
        ('KAUR_UMUM', 'Kaur Umum'),
        ('KAUR_KEUANGAN', 'Kaur Keuangan'),
        ('KADUS', 'Kepala Dusun'),
        ('RT', 'Ketua RT'),
        ('RW', 'Ketua RW'),
        ('LAINNYA', 'Lainnya'),
    ]
    
    village = models.ForeignKey(VillageProfile, on_delete=models.CASCADE, related_name='officials', verbose_name="Desa")
    # penduduk = models.ForeignKey('references.Penduduk', on_delete=models.SET_NULL, blank=True, null=True,
    #                              related_name='official_positions', verbose_name="Data Penduduk")  # COMMENTED OUT - references app disabled
    name = models.CharField(max_length=100, verbose_name="Nama")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name="Jabatan")
    custom_position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Jabatan Khusus", 
                                     help_text="Isi jika memilih 'Lainnya' pada jabatan")
    
    # Personal information
    photo = models.ImageField(upload_to='village_officials/', blank=True, null=True, verbose_name="Foto")
    nik = models.CharField(max_length=16, blank=True, null=True, verbose_name="NIK")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Tanggal Lahir")
    birth_place = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tempat Lahir")
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name="Jenis Kelamin")
    religion = models.CharField(max_length=50, blank=True, null=True, verbose_name="Agama")
    education = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pendidikan")
    occupation = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pekerjaan")
    marital_status = models.CharField(max_length=15, blank=True, null=True, verbose_name="Status Perkawinan")
    experience = models.TextField(blank=True, null=True, verbose_name="Pengalaman")
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telepon")
    mobile = models.CharField(max_length=20, blank=True, null=True, verbose_name="Handphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Alamat")
    dusun = models.CharField(max_length=100, blank=True, null=True, verbose_name="Dusun")
    lorong = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lorong")
    rt_number = models.CharField(max_length=3, blank=True, null=True, verbose_name="Nomor RT")
    rw_number = models.CharField(max_length=3, blank=True, null=True, verbose_name="Nomor RW")
    house_number = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nomor Rumah")
    postal_code = models.CharField(max_length=5, blank=True, null=True, verbose_name="Kode Pos")
    
    # Employment details
    start_date = models.DateField(verbose_name="Tanggal Mulai Jabatan")
    end_date = models.DateField(blank=True, null=True, verbose_name="Tanggal Berakhir Jabatan")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Urutan Tampil")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Perangkat Desa"
        verbose_name_plural = "Perangkat Desa"
        ordering = ['display_order', 'position', 'name']

    def __str__(self):
        return f"{self.name} - {self.get_position_display()}"
    
    @property
    def position_display(self):
        return self.custom_position if self.position == 'LAINNYA' and self.custom_position else self.get_position_display()


class VillagePhoto(models.Model):
    """Village photos gallery"""
    PHOTO_TYPE_CHOICES = [
        ('LANDSCAPE', 'Pemandangan'),
        ('BUILDING', 'Bangunan'),
        ('ACTIVITY', 'Kegiatan'),
        ('CULTURE', 'Budaya'),
        ('FACILITY', 'Fasilitas'),
        ('EVENT', 'Acara'),
        ('PEOPLE', 'Masyarakat'),
        ('NATURE', 'Alam'),
        ('OTHER', 'Lainnya'),
    ]
    
    village = models.ForeignKey(VillageProfile, on_delete=models.CASCADE, related_name='photos', verbose_name="Desa")
    title = models.CharField(max_length=200, verbose_name="Judul Foto")
    image = models.ImageField(upload_to='village_photos/', verbose_name="Foto")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPE_CHOICES, default='OTHER', verbose_name="Jenis Foto")
    
    # Photo metadata
    photographer = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fotografer")
    photo_date = models.DateField(blank=True, null=True, verbose_name="Tanggal Foto")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="Lokasi")
    tags = models.CharField(max_length=500, blank=True, null=True, verbose_name="Tag")
    
    # Display options
    is_featured = models.BooleanField(default=False, verbose_name="Foto Unggulan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Urutan Tampil")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Jumlah Dilihat")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Foto Desa"
        verbose_name_plural = "Foto Desa"
        ordering = ['-is_featured', 'display_order', '-created_at']
        indexes = [
            models.Index(fields=['village', 'is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['photo_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.village.name}"


class VillageFacility(models.Model):
    """Village facilities and infrastructure"""
    FACILITY_TYPE_CHOICES = [
        ('PENDIDIKAN', 'Pendidikan'),
        ('KESEHATAN', 'Kesehatan'),
        ('IBADAH', 'Ibadah'),
        ('OLAHRAGA', 'Olahraga'),
        ('UMUM', 'Umum'),
        ('PEMERINTAHAN', 'Pemerintahan'),
        ('EKONOMI', 'Ekonomi'),
        ('TRANSPORTASI', 'Transportasi'),
        ('LAINNYA', 'Lainnya'),
    ]
    
    CONDITION_CHOICES = [
        ('BAIK', 'Baik'),
        ('CUKUP', 'Cukup'),
        ('RUSAK', 'Rusak'),
        ('RENOVASI', 'Dalam Renovasi'),
    ]
    
    village = models.ForeignKey(VillageProfile, on_delete=models.CASCADE, related_name='facilities', verbose_name="Desa")
    name = models.CharField(max_length=100, verbose_name="Nama Fasilitas")
    type = models.CharField(max_length=20, choices=FACILITY_TYPE_CHOICES, verbose_name="Jenis Fasilitas")
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='BAIK', verbose_name="Kondisi")
    
    # Details
    description = models.TextField(verbose_name="Deskripsi")
    location = models.CharField(max_length=200, verbose_name="Lokasi")
    capacity = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kapasitas")
    
    # Images
    image = models.ImageField(upload_to='village_facilities/', blank=True, null=True, verbose_name="Gambar")
    
    # Management
    manager = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pengelola")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="Penanggung Jawab")
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telepon Kontak")
    
    # Operational details
    operational_hours = models.CharField(max_length=100, blank=True, null=True, verbose_name="Jam Operasional")
    built_year = models.IntegerField(blank=True, null=True, verbose_name="Tahun Dibangun")
    last_renovation = models.DateField(blank=True, null=True, verbose_name="Renovasi Terakhir")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_public = models.BooleanField(default=True, verbose_name="Fasilitas Umum")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Fasilitas Desa"
        verbose_name_plural = "Fasilitas Desa"
        ordering = ['type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class VillageMap(models.Model):
    """Village maps and spatial information"""
    village = models.OneToOneField(VillageProfile, on_delete=models.CASCADE, related_name='map', verbose_name="Desa")
    
    # Map files
    map_image = models.ImageField(upload_to='village_maps/', blank=True, null=True, verbose_name="Gambar Peta")
    map_file = models.FileField(upload_to='village_maps/files/', blank=True, null=True, verbose_name="File Peta")
    
    # Map details
    scale = models.CharField(max_length=50, blank=True, null=True, verbose_name="Skala Peta")
    projection = models.CharField(max_length=100, blank=True, null=True, verbose_name="Proyeksi")
    coordinate_system = models.CharField(max_length=100, blank=True, null=True, verbose_name="Sistem Koordinat")
    
    # Metadata
    created_by = models.CharField(max_length=100, blank=True, null=True, verbose_name="Dibuat Oleh")
    source = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sumber")
    year_created = models.IntegerField(blank=True, null=True, verbose_name="Tahun Pembuatan")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Peta Desa"
        verbose_name_plural = "Peta Desa"

    def __str__(self):
        return f"Peta {self.village.name}"


class VillageStatistic(models.Model):
    """Village statistics and key indicators"""
    village = models.ForeignKey(VillageProfile, on_delete=models.CASCADE, related_name='statistics', verbose_name="Desa")
    
    # Basic counts
    total_dusun = models.PositiveIntegerField(default=0, verbose_name="Jumlah Dusun")
    total_rt = models.PositiveIntegerField(default=0, verbose_name="Jumlah RT")
    total_rw = models.PositiveIntegerField(default=0, verbose_name="Jumlah RW")
    total_facilities = models.PositiveIntegerField(default=0, verbose_name="Total Fasilitas")
    total_umkm = models.PositiveIntegerField(default=0, verbose_name="Total UMKM")
    
    # Economic indicators
    poverty_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Tingkat Kemiskinan (%)")
    unemployment_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Tingkat Pengangguran (%)")
    
    # Infrastructure
    road_length = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Panjang Jalan (km)")
    electricity_coverage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Cakupan Listrik (%)")
    water_coverage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Cakupan Air Bersih (%)")
    
    year = models.IntegerField(verbose_name="Tahun Data")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Statistik Desa"
        verbose_name_plural = "Statistik Desa"
        unique_together = ['village', 'year']
        ordering = ['-year']

    def __str__(self):
        return f"Statistik {self.village.name} - {self.year}"
