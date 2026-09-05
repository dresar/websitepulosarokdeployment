from django.db import models
from django.utils import timezone
from django.conf import settings


class ReferencesPageHeader(models.Model):
    title = models.CharField(max_length=200, default='Data Referensi')
    description = models.TextField(blank=True, default='Informasi lengkap mengenai data referensi dan kependudukan desa')
    background_image = models.ImageField(upload_to='page_headers/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Header Halaman Referensi - {self.title}'

    class Meta:
        verbose_name = 'Header Halaman Referensi'
        verbose_name_plural = 'Header Halaman Referensi'


class Dusun(models.Model):
    """Dusun/Hamlet reference data"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    area_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Area in hectares")
    population_count = models.IntegerField(default=0, help_text="Auto-calculated from residents")
    kepala_dusun = models.ForeignKey('Penduduk', on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='dusun_led', verbose_name="Kepala Dusun")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dusun"
        verbose_name_plural = "Dusun"

    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_population_count(self):
        """Calculate population count from residents"""
        return self.residents.filter(
            is_active=True, 
            is_alive=True
        ).count()
    
    def get_rt_count(self):
        """Calculate RT count from lorong data"""
        return self.lorongs.filter(is_active=True).values('rt_number').distinct().count()
    
    def get_lorong_count(self):
        """Calculate lorong count"""
        return self.lorongs.filter(is_active=True).count()
    
    def save(self, *args, **kwargs):
        """Auto-calculate population count on save"""
        super().save(*args, **kwargs)
        # Update population count after save
        self.population_count = self.get_population_count()
        super().save(update_fields=['population_count'])


class Lorong(models.Model):
    """Lorong/Street reference data"""
    dusun = models.ForeignKey(Dusun, on_delete=models.CASCADE, related_name='lorongs')
    nama_lorong = models.CharField(max_length=100, default='')
    kode = models.CharField(max_length=15)
    ketua_lorong = models.CharField(max_length=100)
    rt_number = models.CharField(max_length=3, blank=True, null=True, verbose_name="Nomor RT")
    description = models.TextField(blank=True, null=True)
    length = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Length in meters")
    house_count = models.IntegerField(default=0, help_text="Auto-calculated from residents")
    population_count = models.IntegerField(default=0, help_text="Auto-calculated from residents")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lorong"
        verbose_name_plural = "Lorong"
        unique_together = ['dusun', 'kode']

    def __str__(self):
        return f"{self.nama_lorong} - {self.dusun.name}"
    
    def get_population_count(self):
        """Calculate population count from residents"""
        return self.residents.filter(
            is_active=True, 
            is_alive=True
        ).count()
    
    def get_house_count(self):
        """Calculate house count from residents (unique houses)"""
        return self.residents.filter(
            is_active=True, 
            is_alive=True
        ).values('rt_number').distinct().count()
    
    def save(self, *args, **kwargs):
        """Auto-calculate population and house count on save"""
        super().save(*args, **kwargs)
        # Update counts after save
        self.population_count = self.get_population_count()
        self.house_count = self.get_house_count()
        super().save(update_fields=['population_count', 'house_count'])


class RW(models.Model):
    """RW (Rukun Warga) reference data"""
    dusun = models.ForeignKey(Dusun, on_delete=models.CASCADE, related_name='rws')
    rw_number = models.CharField(max_length=3, verbose_name="Nomor RW")
    ketua_rw = models.ForeignKey('Penduduk', on_delete=models.SET_NULL, blank=True, null=True, 
                                related_name='rw_led', verbose_name="Ketua RW")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    population_count = models.IntegerField(default=0, help_text="Auto-calculated from residents")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RW"
        verbose_name_plural = "RW"
        unique_together = ['dusun', 'rw_number']

    def __str__(self):
        return f"RW {self.rw_number} - {self.dusun.name}"
    
    def get_population_count(self):
        """Calculate population count from residents in this RW"""
        return self.residents.filter(
            is_active=True, 
            is_alive=True
        ).count()
    
    def get_rt_count(self):
        """Calculate RT count in this RW"""
        return self.rts.filter(is_active=True).count()
    
    def save(self, *args, **kwargs):
        """Auto-calculate population count on save"""
        super().save(*args, **kwargs)
        # Update population count after save
        self.population_count = self.get_population_count()
        super().save(update_fields=['population_count'])


class RT(models.Model):
    """RT (Rukun Tetangga) reference data"""
    rw = models.ForeignKey(RW, on_delete=models.CASCADE, related_name='rts')
    rt_number = models.CharField(max_length=3, verbose_name="Nomor RT")
    ketua_rt = models.ForeignKey('Penduduk', on_delete=models.SET_NULL, blank=True, null=True, 
                                related_name='rt_led', verbose_name="Ketua RT")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    population_count = models.IntegerField(default=0, help_text="Auto-calculated from residents")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RT"
        verbose_name_plural = "RT"
        unique_together = ['rw', 'rt_number']

    def __str__(self):
        return f"RT {self.rt_number} RW {self.rw.rw_number} - {self.rw.dusun.name}"
    
    def get_population_count(self):
        """Calculate population count from residents in this RT"""
        return self.residents.filter(
            is_active=True, 
            is_alive=True
        ).count()
    
    def save(self, *args, **kwargs):
        """Auto-calculate population count on save"""
        super().save(*args, **kwargs)
        # Update population count after save
        self.population_count = self.get_population_count()
        super().save(update_fields=['population_count'])


class Keluarga(models.Model):
    """Family reference data"""
    dusun = models.ForeignKey(Dusun, on_delete=models.CASCADE, related_name='keluarga')
    nama_kepala_keluarga = models.CharField(max_length=100)
    nomor_kk = models.CharField(max_length=16, unique=True)
    rt = models.CharField(max_length=3)
    rw = models.CharField(max_length=3)
    alamat = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Keluarga"
        verbose_name_plural = "Keluarga"

    def __str__(self):
        return f"{self.nama_kepala_keluarga} - {self.nomor_kk}"


class Penduduk(models.Model):
    """Population/Resident data with comprehensive information"""
    GENDER_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('BELUM_KAWIN', 'Belum Kawin'),
        ('KAWIN', 'Kawin'),
        ('CERAI_HIDUP', 'Cerai Hidup'),
        ('CERAI_MATI', 'Cerai Mati'),
    ]
    
    RELIGION_CHOICES = [
        ('Islam', 'Islam'),
        ('Kristen Protestan', 'Kristen Protestan'),
        ('Kristen Katolik', 'Kristen Katolik'),
        ('Hindu', 'Hindu'),
        ('Buddha', 'Buddha'),
        ('Konghucu', 'Konghucu'),
        ('Kepercayaan', 'Kepercayaan'),
    ]
    
    EDUCATION_CHOICES = [
        ('TIDAK_BELUM_SEKOLAH', 'Tidak/Belum Sekolah'),
        ('BELUM_TAMAT_SD', 'Belum Tamat SD/Sederajat'),
        ('TAMAT_SD', 'Tamat SD/Sederajat'),
        ('SLTP', 'SLTP/Sederajat'),
        ('SLTA', 'SLTA/Sederajat'),
        ('D1', 'D1'),
        ('D2', 'D2'),
        ('D3', 'D3'),
        ('D4_S1', 'D4/S1'),
        ('S2', 'S2'),
        ('S3', 'S3'),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
    ]
    
    CITIZENSHIP_CHOICES = [
        ('WNI', 'WNI'),
        ('WNA', 'WNA'),
    ]
    
    RELATIONSHIP_CHOICES = [
        ('KEPALA_KELUARGA', 'Kepala Keluarga'),
        ('ISTRI', 'Istri'),
        ('ANAK', 'Anak'),
        ('MENANTU', 'Menantu'),
        ('CUCU', 'Cucu'),
        ('ORANG_TUA', 'Orang Tua'),
        ('MERTUA', 'Mertua'),
        ('FAMILI_LAIN', 'Famili Lain'),
        ('PEMBANTU', 'Pembantu'),
        ('LAINNYA', 'Lainnya'),
    ]

    # Basic Identity
    nik = models.CharField(max_length=16, unique=True, verbose_name="NIK")
    name = models.CharField(max_length=100, verbose_name="Nama Lengkap")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Jenis Kelamin")
    
    # Birth Information
    birth_place = models.CharField(max_length=100, verbose_name="Tempat Lahir")
    birth_date = models.DateField(verbose_name="Tanggal Lahir")
    
    # Family Information
    kk_number = models.CharField(max_length=16, blank=True, null=True, verbose_name="Nomor Kartu Keluarga")
    family_head = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='family_members', verbose_name="Kepala Keluarga")
    relationship_to_head = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES, blank=True, null=True, 
                                          verbose_name="Hubungan dengan Kepala Keluarga")
    
    # Personal Information
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES, verbose_name="Agama")
    education = models.CharField(max_length=50, choices=EDUCATION_CHOICES, blank=True, null=True, verbose_name="Pendidikan")
    occupation = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pekerjaan")
    marital_status = models.CharField(max_length=15, choices=MARITAL_STATUS_CHOICES, verbose_name="Status Perkawinan")
    
    # Physical Information
    blood_type = models.CharField(max_length=2, choices=BLOOD_TYPE_CHOICES, blank=True, null=True, verbose_name="Golongan Darah")
    height = models.PositiveIntegerField(blank=True, null=True, help_text="Tinggi badan dalam cm", verbose_name="Tinggi Badan")
    weight = models.PositiveIntegerField(blank=True, null=True, help_text="Berat badan dalam kg", verbose_name="Berat Badan")
    
    # Contact Information
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Nomor Telepon")
    mobile_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Nomor HP")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Address Information
    dusun = models.ForeignKey(Dusun, on_delete=models.CASCADE, related_name='residents', verbose_name="Dusun")
    lorong = models.ForeignKey(Lorong, on_delete=models.CASCADE, related_name='residents', blank=True, null=True, verbose_name="Lorong")
    rw = models.ForeignKey('RW', on_delete=models.CASCADE, related_name='residents', blank=True, null=True, verbose_name="RW")
    rt = models.ForeignKey('RT', on_delete=models.CASCADE, related_name='residents', blank=True, null=True, verbose_name="RT")
    rt_number = models.CharField(max_length=3, blank=True, null=True, verbose_name="Nomor RT")
    rw_number = models.CharField(max_length=3, blank=True, null=True, verbose_name="Nomor RW")
    house_number = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nomor Rumah")
    address = models.TextField(verbose_name="Alamat Lengkap")
    postal_code = models.CharField(max_length=5, blank=True, null=True, verbose_name="Kode Pos")
    
    # Citizenship & Identity
    citizenship = models.CharField(max_length=3, choices=CITIZENSHIP_CHOICES, default='WNI', verbose_name="Kewarganegaraan")
    passport_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Nomor Paspor")
    passport_expiry = models.DateField(blank=True, null=True, verbose_name="Berlaku Hingga")
    
    # Additional Information
    emergency_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kontak Darurat")
    emergency_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telepon Darurat")
    emergency_relationship = models.CharField(max_length=50, blank=True, null=True, verbose_name="Hubungan dengan Kontak Darurat")
    
    # Photo
    photo = models.ImageField(upload_to='penduduk_photos/', blank=True, null=True, verbose_name="Foto")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_alive = models.BooleanField(default=True, verbose_name="Masih Hidup")
    death_date = models.DateField(blank=True, null=True, verbose_name="Tanggal Meninggal")
    death_place = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tempat Meninggal")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, 
                                  related_name='created_penduduk', verbose_name="Dibuat Oleh")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, 
                                  related_name='updated_penduduk', verbose_name="Diperbarui Oleh")

    class Meta:
        verbose_name = "Penduduk"
        verbose_name_plural = "Penduduk"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.nik})"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        if self.death_date:
            end_date = self.death_date
        else:
            end_date = today
        return end_date.year - self.birth_date.year - ((end_date.month, end_date.day) < (self.birth_date.month, self.birth_date.day))
    
    @property
    def full_address(self):
        """Get complete formatted address"""
        address_parts = []
        if self.house_number:
            address_parts.append(f"No. {self.house_number}")
        if self.rt_number:
            address_parts.append(f"RT {self.rt_number}")
        if self.rw_number:
            address_parts.append(f"RW {self.rw_number}")
        if self.lorong:
            address_parts.append(f"Lorong {self.lorong.nama_lorong}")
        address_parts.append(f"Dusun {self.dusun.name}")
        address_parts.append(self.address)
        if self.postal_code:
            address_parts.append(f"Kode Pos {self.postal_code}")
        return ", ".join(filter(None, address_parts))
    
    @property
    def is_family_head(self):
        """Check if this person is a family head"""
        return self.family_members.exists()
    
    @property
    def family_size(self):
        """Get family size including self"""
        if self.family_head:
            return self.family_head.family_members.count() + 1
        elif self.is_family_head:
            return self.family_members.count() + 1
        return 1


class Pelajar(models.Model):
    """Student reference data"""
    JENJANG_CHOICES = [
        ('SD', 'SD/Sederajat'),
        ('SMP', 'SMP/Sederajat'),
        ('SMA', 'SMA/SMK/Sederajat'),
        ('PT', 'Perguruan Tinggi')
    ]

    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('lulus', 'Lulus'),
        ('pindah', 'Pindah'),
        ('putus', 'Putus Sekolah')
    ]

    penduduk = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='data_pelajar')
    jenjang = models.CharField(max_length=5, choices=JENJANG_CHOICES)
    sekolah = models.CharField(max_length=100)
    tahun_masuk = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aktif')
    keterangan = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_pelajar')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='updated_pelajar')

    class Meta:
        verbose_name = "Pelajar"
        verbose_name_plural = "Pelajar"
        ordering = ['penduduk__name']

    def __str__(self):
        return f"{self.penduduk.name} - {self.get_jenjang_display()} - {self.sekolah}"

class Family(models.Model):
    """Family unit information"""
    FAMILY_STATUS_CHOICES = [
        ('NORMAL', 'Keluarga Normal'),
        ('MISKIN', 'Keluarga Miskin'),
        ('PRASEJAHTERA', 'Keluarga Prasejahtera'),
        ('SEJAHTERA', 'Keluarga Sejahtera'),
        ('SEJAHTERA_1', 'Keluarga Sejahtera 1'),
        ('SEJAHTERA_2', 'Keluarga Sejahtera 2'),
        ('SEJAHTERA_3', 'Keluarga Sejahtera 3'),
        ('SEJAHTERA_3_PLUS', 'Keluarga Sejahtera 3+'),
    ]
    
    kk_number = models.CharField(max_length=16, unique=True, verbose_name="Nomor Kartu Keluarga")
    head = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='headed_families', verbose_name="Kepala Keluarga")
    family_status = models.CharField(max_length=20, choices=FAMILY_STATUS_CHOICES, default='NORMAL', verbose_name="Status Keluarga")
    total_members = models.PositiveIntegerField(default=1, verbose_name="Jumlah Anggota")
    total_income = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Total pendapatan keluarga per bulan", verbose_name="Total Pendapatan")
    address = models.TextField(verbose_name="Alamat Keluarga")
    dusun = models.ForeignKey(Dusun, on_delete=models.CASCADE, verbose_name="Dusun")
    lorong = models.ForeignKey(Lorong, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Lorong")
    rt_number = models.CharField(max_length=3, blank=True, null=True, verbose_name="Nomor RT")
    rw_number = models.CharField(max_length=3, blank=True, null=True, verbose_name="Nomor RW")
    house_number = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nomor Rumah")
    postal_code = models.CharField(max_length=5, blank=True, null=True, verbose_name="Kode Pos")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Nomor Telepon")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Keluarga"
        verbose_name_plural = "Keluarga"

    def __str__(self):
        return f"KK {self.kk_number} - {self.head.name}"
    
    @property
    def full_address(self):
        """Get complete formatted address"""
        address_parts = []
        if self.house_number:
            address_parts.append(f"No. {self.house_number}")
        if self.rt_number:
            address_parts.append(f"RT {self.rt_number}")
        if self.rw_number:
            address_parts.append(f"RW {self.rw_number}")
        if self.lorong:
            address_parts.append(f"Lorong {self.lorong.nama_lorong}")
        address_parts.append(f"Dusun {self.dusun.name}")
        address_parts.append(self.address)
        if self.postal_code:
            address_parts.append(f"Kode Pos {self.postal_code}")
        return ", ".join(filter(None, address_parts))


class DisabilitasType(models.Model):
    """Disability type reference"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Jenis Disabilitas"
        verbose_name_plural = "Jenis Disabilitas"

    def __str__(self):
        return self.name


class DisabilitasData(models.Model):
    """Disability data for residents"""
    SEVERITY_CHOICES = [
        ('RINGAN', 'Ringan'),
        ('SEDANG', 'Sedang'),
        ('BERAT', 'Berat'),
    ]

    penduduk = models.ForeignKey(Penduduk, on_delete=models.CASCADE, related_name='disabilities')
    disability_type = models.ForeignKey(DisabilitasType, on_delete=models.CASCADE)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    description = models.TextField(blank=True, null=True)
    diagnosis_date = models.DateField(blank=True, null=True)
    needs_assistance = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Data Disabilitas"
        verbose_name_plural = "Data Disabilitas"
        unique_together = ['penduduk', 'disability_type']

    def __str__(self):
        return f"{self.penduduk.name} - {self.disability_type.name}"


class ReligionReference(models.Model):
    """Religion reference data"""
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agama"
        verbose_name_plural = "Agama"

    def __str__(self):
        return self.name
