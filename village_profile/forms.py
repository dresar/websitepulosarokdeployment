from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import VillageHistory, VillageHistoryPhoto, VillageProfile, VillageGeography, VillageDemography, VillageOfficial, VillageFacility, VillagePhoto, VillageStatistic, VillageProfilePageHeader


class VillageHistoryForm(forms.ModelForm):
    """Form untuk Sejarah Desa"""
    
    class Meta:
        model = VillageHistory
        fields = [
            'title', 'slug', 'summary', 'content', 'history_type',
            'year_start', 'year_end', 'period_start', 'period_end',
            'featured_image', 'source', 'author', 'is_featured', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Masukkan judul sejarah...'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'URL slug (otomatis dari judul)'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Ringkasan singkat sejarah...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 10,
                'placeholder': 'Isi lengkap sejarah desa...'
            }),
            'history_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'year_start': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Tahun mulai (contoh: 1945)'
            }),
            'year_end': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Tahun berakhir (opsional)'
            }),
            'period_start': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'period_end': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'featured_image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'source': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Sumber informasi...'
            }),
            'author': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nama penulis/peneliti...'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
        labels = {
            'title': 'Judul Sejarah',
            'slug': 'URL Slug',
            'summary': 'Ringkasan',
            'content': 'Isi Sejarah',
            'history_type': 'Jenis Sejarah',
            'year_start': 'Tahun Mulai',
            'year_end': 'Tahun Berakhir',
            'period_start': 'Periode Mulai',
            'period_end': 'Periode Berakhir',
            'featured_image': 'Gambar Utama',
            'source': 'Sumber',
            'author': 'Penulis',
            'is_featured': 'Tampilkan di Beranda',
            'is_active': 'Status Aktif'
        }
        help_texts = {
            'slug': 'URL slug akan dibuat otomatis dari judul jika dikosongkan',
            'summary': 'Ringkasan singkat yang akan ditampilkan di daftar sejarah',
            'history_type': 'Pilih jenis/kategori sejarah',
            'year_start': 'Tahun dimulainya peristiwa sejarah',
            'year_end': 'Tahun berakhirnya peristiwa (opsional)',
            'period_start': 'Tanggal mulai periode (opsional)',
            'period_end': 'Tanggal akhir periode (opsional)',
            'source': 'Sumber referensi informasi sejarah',
            'author': 'Nama penulis atau peneliti',
            'is_featured': 'Centang untuk menampilkan di halaman utama',
            'is_active': 'Centang untuk mengaktifkan sejarah ini'
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError('Judul sejarah harus diisi.')
        if len(title) < 5:
            raise ValidationError('Judul sejarah minimal 5 karakter.')
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise ValidationError('Isi sejarah harus diisi.')
        if len(content) < 50:
            raise ValidationError('Isi sejarah minimal 50 karakter.')
        return content
    
    def clean_year_start(self):
        year_start = self.cleaned_data.get('year_start')
        if year_start:
            current_year = timezone.now().year
            if year_start > current_year:
                raise ValidationError('Tahun mulai tidak boleh lebih dari tahun sekarang.')
            if year_start < 1000:
                raise ValidationError('Tahun mulai tidak valid.')
        return year_start
    
    def clean_year_end(self):
        year_end = self.cleaned_data.get('year_end')
        year_start = self.cleaned_data.get('year_start')
        
        if year_end:
            current_year = timezone.now().year
            if year_end > current_year:
                raise ValidationError('Tahun berakhir tidak boleh lebih dari tahun sekarang.')
            if year_start and year_end < year_start:
                raise ValidationError('Tahun berakhir tidak boleh lebih kecil dari tahun mulai.')
        return year_end
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        
        if period_start and period_end:
            if period_end < period_start:
                raise ValidationError('Periode berakhir tidak boleh lebih awal dari periode mulai.')
        
        return cleaned_data


class VillageHistoryPhotoForm(forms.ModelForm):
    """Form untuk Foto Sejarah Desa"""
    
    class Meta:
        model = VillageHistoryPhoto
        fields = [
            'history', 'image', 'caption', 'description', 'photographer',
            'photo_date', 'location', 'is_featured', 'is_active', 'display_order'
        ]
        widgets = {
            'history': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Keterangan singkat foto...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Deskripsi detail foto...'
            }),
            'photographer': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nama fotografer...'
            }),
            'photo_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Lokasi pengambilan foto...'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '1'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
        labels = {
            'history': 'Sejarah Terkait',
            'image': 'File Foto',
            'caption': 'Keterangan Foto',
            'description': 'Deskripsi',
            'photographer': 'Fotografer',
            'photo_date': 'Tanggal Foto',
            'location': 'Lokasi',
            'display_order': 'Urutan Tampil',
            'is_featured': 'Foto Utama',
            'is_active': 'Status Aktif'
        }
        help_texts = {
            'caption': 'Keterangan singkat yang akan ditampilkan di bawah foto',
            'description': 'Deskripsi detail tentang foto ini',
            'photographer': 'Nama orang yang mengambil foto',
            'photo_date': 'Tanggal pengambilan foto',
            'location': 'Lokasi dimana foto diambil',
            'display_order': 'Urutan tampil foto (angka kecil tampil lebih dulu)',
            'is_featured': 'Centang jika ini foto utama untuk sejarah ini',
            'is_active': 'Centang untuk mengaktifkan foto ini'
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validasi ukuran file (maksimal 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Ukuran file foto maksimal 5MB.')
            
            # Validasi format file
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if image.content_type not in allowed_formats:
                raise ValidationError('Format file harus JPEG, PNG, atau GIF.')
        
        return image
    
    def clean_display_order(self):
        display_order = self.cleaned_data.get('display_order')
        if display_order and display_order < 1:
            raise ValidationError('Urutan tampil minimal 1.')
        return display_order


class VillageHistorySearchForm(forms.Form):
    """Form untuk pencarian sejarah desa"""
    
    search_query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Cari sejarah desa...'
        }),
        label='Kata Kunci'
    )
    
    history_type = forms.ChoiceField(
        choices=[('', 'Semua Jenis')] + VillageHistory.HISTORY_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        label='Jenis Sejarah'
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
        }),
        label='Hanya yang Ditampilkan di Beranda'
    )
    
    is_active_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
        }),
        label='Hanya yang Aktif'
    )


class VillageProfileForm(forms.ModelForm):
    """Form untuk Profil Desa"""
    
    class Meta:
        model = VillageProfile
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nama desa...'
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kode desa...'
            }),
            'district': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kecamatan...'
            }),
            'regency': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kabupaten...'
            }),
            'province': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Provinsi...'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kode pos...'
            }),
            'village_head': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nama kepala desa...'
            }),
            'established_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'area': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Luas wilayah (km²)...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Deskripsi desa...'
            }),
            'vision': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Visi desa...'
            }),
            'mission': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 5,
                'placeholder': 'Misi desa...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nomor telepon...'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Email desa...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Website desa...'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Nama desa harus diisi.')
        if len(name) < 3:
            raise ValidationError('Nama desa minimal 3 karakter.')
        return name
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            # Generate code from name if not provided
            name = self.cleaned_data.get('name', '')
            code = name.lower().replace(' ', '_').replace('-', '_')
        return code
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Basic email validation
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValidationError('Format email tidak valid.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove non-digit characters for validation
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) < 10:
                raise ValidationError('Nomor telepon minimal 10 digit.')
        return phone
    
    def clean_area(self):
        area = self.cleaned_data.get('area')
        if area is not None and area <= 0:
            raise ValidationError('Luas wilayah harus lebih dari 0.')
        return area


class VillageGeographyForm(forms.ModelForm):
    """Form untuk Geografi Desa"""
    
    class Meta:
        model = VillageGeography
        fields = '__all__'
        widgets = {
            'village': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': 'any',
                'placeholder': 'Latitude...'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': 'any',
                'placeholder': 'Longitude...'
            }),
            'altitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ketinggian (mdpl)...'
            }),
            'climate': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Iklim...'
            }),
            'rainfall': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Curah hujan (mm/tahun)...'
            }),
            'temperature_min': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Suhu minimum (°C)...'
            }),
            'temperature_max': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Suhu maksimum (°C)...'
            }),
            'topography': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Topografi...'
            }),
            'soil_type': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Jenis tanah...'
            }),
            'boundary_north': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Batas utara...'
            }),
            'boundary_south': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Batas selatan...'
            }),
            'boundary_east': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Batas timur...'
            }),
            'boundary_west': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Batas barat...'
            })
        }
    
    def clean_latitude(self):
        latitude = self.cleaned_data.get('latitude')
        if latitude is not None:
            if latitude < -90 or latitude > 90:
                raise ValidationError('Latitude harus antara -90 dan 90 derajat.')
        return latitude
    
    def clean_longitude(self):
        longitude = self.cleaned_data.get('longitude')
        if longitude is not None:
            if longitude < -180 or longitude > 180:
                raise ValidationError('Longitude harus antara -180 dan 180 derajat.')
        return longitude
    
    def clean_rainfall(self):
        rainfall = self.cleaned_data.get('rainfall')
        if rainfall is not None and rainfall < 0:
            raise ValidationError('Curah hujan tidak boleh negatif.')
        return rainfall
    
    def clean_temperature_min(self):
        temp_min = self.cleaned_data.get('temperature_min')
        temp_max = self.cleaned_data.get('temperature_max')
        if temp_min is not None and temp_max is not None:
            if temp_min > temp_max:
                raise ValidationError('Suhu minimum tidak boleh lebih besar dari suhu maksimum.')
        return temp_min


class VillageDemographyForm(forms.ModelForm):
    """Form untuk Demografi Desa"""
    
    class Meta:
        model = VillageDemography
        fields = '__all__'
        widgets = {
            'village': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Tahun data...'
            }),
            'total_population': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Total penduduk...'
            }),
            'male_population': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Penduduk laki-laki...'
            }),
            'female_population': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Penduduk perempuan...'
            }),
            'total_families': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Total keluarga...'
            }),
            'population_density': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Kepadatan penduduk...'
            }),
            'growth_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Tingkat pertumbuhan (%)...'
            })
        }
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            current_year = timezone.now().year
            if year > current_year:
                raise ValidationError('Tahun data tidak boleh lebih dari tahun sekarang.')
            if year < 1900:
                raise ValidationError('Tahun data tidak valid.')
        return year
    
    def clean_total_population(self):
        total_pop = self.cleaned_data.get('total_population')
        male_pop = self.cleaned_data.get('male_population')
        female_pop = self.cleaned_data.get('female_population')
        
        if total_pop is not None and total_pop < 0:
            raise ValidationError('Total populasi tidak boleh negatif.')
        
        if male_pop is not None and female_pop is not None and total_pop is not None:
            if male_pop + female_pop != total_pop:
                raise ValidationError('Jumlah laki-laki + perempuan harus sama dengan total populasi.')
        
        return total_pop
    
    def clean_male_population(self):
        male_pop = self.cleaned_data.get('male_population')
        if male_pop is not None and male_pop < 0:
            raise ValidationError('Populasi laki-laki tidak boleh negatif.')
        return male_pop
    
    def clean_female_population(self):
        female_pop = self.cleaned_data.get('female_population')
        if female_pop is not None and female_pop < 0:
            raise ValidationError('Populasi perempuan tidak boleh negatif.')
        return female_pop
    
    def clean_population_density(self):
        density = self.cleaned_data.get('population_density')
        if density is not None and density < 0:
            raise ValidationError('Kepadatan penduduk tidak boleh negatif.')
        return density


class VillageOfficialForm(forms.ModelForm):
    """Form untuk Perangkat Desa"""
    
    class Meta:
        model = VillageOfficial
        fields = '__all__'
        widgets = {
            'village': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nama lengkap...'
            }),
            'position': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'custom_position': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Jabatan khusus...'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'education': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Pendidikan terakhir...'
            }),
            'experience': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Pengalaman kerja...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nomor telepon...'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Email...'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Alamat...'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Urutan tampil...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Nama perangkat desa harus diisi.')
        if len(name) < 2:
            raise ValidationError('Nama perangkat desa minimal 2 karakter.')
        return name
    
    def clean_position(self):
        position = self.cleaned_data.get('position')
        if not position:
            raise ValidationError('Jabatan harus dipilih.')
        return position
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Basic email validation
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValidationError('Format email tidak valid.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove non-digit characters for validation
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) < 10:
                raise ValidationError('Nomor telepon minimal 10 digit.')
        return phone
    
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('Tanggal mulai jabatan tidak boleh lebih besar dari tanggal akhir jabatan.')
        
        return start_date


class VillageFacilityForm(forms.ModelForm):
    """Form untuk Fasilitas Desa"""
    
    class Meta:
        model = VillageFacility
        fields = '__all__'
        widgets = {
            'village': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nama fasilitas...'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'condition': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Deskripsi fasilitas...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Lokasi fasilitas...'
            }),
            'capacity': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kapasitas...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'manager': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Pengelola...'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kontak person...'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nomor telepon kontak...'
            }),
            'operational_hours': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Jam operasional...'
            }),
            'built_year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Tahun dibangun...'
            }),
            'last_renovation': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Nama fasilitas harus diisi.')
        if len(name) < 3:
            raise ValidationError('Nama fasilitas minimal 3 karakter.')
        return name
    
    def clean_type(self):
        facility_type = self.cleaned_data.get('type')
        if not facility_type:
            raise ValidationError('Jenis fasilitas harus dipilih.')
        return facility_type
    
    def clean_condition(self):
        condition = self.cleaned_data.get('condition')
        if not condition:
            raise ValidationError('Kondisi fasilitas harus dipilih.')
        return condition
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location:
            raise ValidationError('Lokasi fasilitas harus diisi.')
        return location
    
    def clean_built_year(self):
        built_year = self.cleaned_data.get('built_year')
        if built_year:
            current_year = timezone.now().year
            if built_year > current_year:
                raise ValidationError('Tahun dibangun tidak boleh lebih dari tahun sekarang.')
            if built_year < 1900:
                raise ValidationError('Tahun dibangun tidak valid.')
        return built_year
    
    def clean_contact_phone(self):
        contact_phone = self.cleaned_data.get('contact_phone')
        if contact_phone:
            # Remove non-digit characters for validation
            phone_digits = ''.join(filter(str.isdigit, contact_phone))
            if len(phone_digits) < 10:
                raise ValidationError('Nomor telepon kontak minimal 10 digit.')
        return contact_phone


class VillagePhotoForm(forms.ModelForm):
    """Form untuk Foto Desa"""
    
    class Meta:
        model = VillagePhoto
        fields = '__all__'
        widgets = {
            'village': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Judul foto...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Deskripsi foto...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'photo_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'photographer': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nama fotografer...'
            }),
            'photo_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Lokasi pengambilan foto...'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Urutan tampil...'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
        labels = {
            'village': 'Desa',
            'title': 'Judul Foto',
            'description': 'Deskripsi',
            'image': 'File Foto',
            'photo_type': 'Jenis Foto',
            'photographer': 'Fotografer',
            'photo_date': 'Tanggal Foto',
            'location': 'Lokasi',
            'display_order': 'Urutan Tampil',
            'is_featured': 'Foto Utama',
            'is_active': 'Status Aktif'
        }
        help_texts = {
            'title': 'Judul yang akan ditampilkan untuk foto ini',
            'description': 'Deskripsi detail tentang foto',
            'photo_type': 'Kategori atau jenis foto',
            'photographer': 'Nama orang yang mengambil foto',
            'photo_date': 'Tanggal pengambilan foto',
            'location': 'Lokasi dimana foto diambil',
            'display_order': 'Urutan tampil foto (angka kecil tampil lebih dulu)',
            'is_featured': 'Centang jika ini foto utama',
            'is_active': 'Centang untuk mengaktifkan foto ini'
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validasi ukuran file (maksimal 10MB)
            if image.size > 10 * 1024 * 1024:
                raise ValidationError('Ukuran file foto maksimal 10MB.')
            
            # Validasi format file
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_formats:
                raise ValidationError('Format file harus JPEG, PNG, GIF, atau WebP.')
        
        return image
    
    def clean_display_order(self):
        display_order = self.cleaned_data.get('display_order')
        if display_order and display_order < 0:
            raise ValidationError('Urutan tampil tidak boleh negatif.')
        return display_order
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError('Judul foto harus diisi.')
        if len(title) < 3:
            raise ValidationError('Judul foto minimal 3 karakter.')
        return title
    
    def clean_photo_type(self):
        photo_type = self.cleaned_data.get('photo_type')
        if not photo_type:
            raise ValidationError('Jenis foto harus dipilih.')
        return photo_type


class VillageStatisticForm(forms.ModelForm):
    """Form untuk Statistik Desa"""
    
    class Meta:
        model = VillageStatistic
        fields = '__all__'
        widgets = {
            'village': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Tahun data...'
            }),
            'total_dusun': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Jumlah dusun...'
            }),
            'total_rt': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Jumlah RT...'
            }),
            'total_rw': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Jumlah RW...'
            }),
            'total_umkm': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Jumlah UMKM...'
            }),
            'poverty_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Tingkat kemiskinan (%)...'
            }),
            'unemployment_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Tingkat pengangguran (%)...'
            }),
            'road_length': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Panjang jalan (km)...'
            }),
            'electricity_coverage': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Cakupan listrik (%)...'
            }),
            'water_coverage': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Cakupan air bersih (%)...'
            })
        }
        labels = {
            'village': 'Desa',
            'year': 'Tahun Data',
            'total_dusun': 'Jumlah Dusun',
            'total_rt': 'Jumlah RT',
            'total_rw': 'Jumlah RW',
            'total_umkm': 'Jumlah UMKM',
            'poverty_rate': 'Tingkat Kemiskinan (%)',
            'unemployment_rate': 'Tingkat Pengangguran (%)',
            'road_length': 'Panjang Jalan (km)',
            'electricity_coverage': 'Cakupan Listrik (%)',
            'water_coverage': 'Cakupan Air Bersih (%)'
        }
        help_texts = {
            'year': 'Tahun data statistik ini',
            'total_dusun': 'Jumlah dusun di desa',
            'total_rt': 'Jumlah Rukun Tetangga',
            'total_rw': 'Jumlah Rukun Warga',
            'total_umkm': 'Jumlah Usaha Mikro, Kecil, dan Menengah',
            'poverty_rate': 'Persentase penduduk miskin',
            'unemployment_rate': 'Persentase pengangguran',
            'road_length': 'Total panjang jalan dalam kilometer',
            'electricity_coverage': 'Persentase rumah yang teraliri listrik',
            'water_coverage': 'Persentase rumah yang memiliki akses air bersih'
        }
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            current_year = timezone.now().year
            if year > current_year:
                raise ValidationError('Tahun data tidak boleh lebih dari tahun sekarang.')
            if year < 1900:
                raise ValidationError('Tahun data tidak valid.')
        return year
    
    def clean_poverty_rate(self):
        poverty_rate = self.cleaned_data.get('poverty_rate')
        if poverty_rate is not None:
            if poverty_rate < 0 or poverty_rate > 100:
                raise ValidationError('Tingkat kemiskinan harus antara 0 dan 100.')
        return poverty_rate
    
    def clean_unemployment_rate(self):
        unemployment_rate = self.cleaned_data.get('unemployment_rate')
        if unemployment_rate is not None:
            if unemployment_rate < 0 or unemployment_rate > 100:
                raise ValidationError('Tingkat pengangguran harus antara 0 dan 100.')
        return unemployment_rate
    
    def clean_total_dusun(self):
        total_dusun = self.cleaned_data.get('total_dusun')
        if total_dusun is not None and total_dusun < 0:
            raise ValidationError('Jumlah dusun tidak boleh negatif.')
        return total_dusun
    
    def clean_total_rt(self):
        total_rt = self.cleaned_data.get('total_rt')
        if total_rt is not None and total_rt < 0:
            raise ValidationError('Jumlah RT tidak boleh negatif.')
        return total_rt
    
    def clean_total_rw(self):
        total_rw = self.cleaned_data.get('total_rw')
        if total_rw is not None and total_rw < 0:
            raise ValidationError('Jumlah RW tidak boleh negatif.')
        return total_rw
    
    def clean_total_umkm(self):
        total_umkm = self.cleaned_data.get('total_umkm')
        if total_umkm is not None and total_umkm < 0:
            raise ValidationError('Jumlah UMKM tidak boleh negatif.')
        return total_umkm
    
    def clean_road_length(self):
        road_length = self.cleaned_data.get('road_length')
        if road_length is not None and road_length < 0:
            raise ValidationError('Panjang jalan tidak boleh negatif.')
        return road_length
    
    def clean_electricity_coverage(self):
        electricity_coverage = self.cleaned_data.get('electricity_coverage')
        if electricity_coverage is not None:
            if electricity_coverage < 0 or electricity_coverage > 100:
                raise ValidationError('Cakupan listrik harus antara 0 dan 100.')
        return electricity_coverage
    
    def clean_water_coverage(self):
        water_coverage = self.cleaned_data.get('water_coverage')
        if water_coverage is not None:
            if water_coverage < 0 or water_coverage > 100:
                raise ValidationError('Cakupan air bersih harus antara 0 dan 100.')
        return water_coverage


class VillageProfilePageHeaderForm(forms.ModelForm):
    """Form untuk Header Halaman Profil Desa"""
    
    class Meta:
        model = VillageProfilePageHeader
        fields = '__all__'
        widgets = {
            'village': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'page_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Judul halaman...'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Subjudul halaman...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Deskripsi halaman...'
            }),
            'background_image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
        labels = {
            'village': 'Desa',
            'page_type': 'Jenis Halaman',
            'title': 'Judul Halaman',
            'subtitle': 'Subjudul',
            'description': 'Deskripsi',
            'background_image': 'Gambar Latar Belakang',
            'is_active': 'Status Aktif'
        }
        help_texts = {
            'page_type': 'Jenis halaman yang akan menggunakan header ini',
            'title': 'Judul utama yang akan ditampilkan di header',
            'subtitle': 'Subjudul atau tagline halaman',
            'description': 'Deskripsi singkat tentang halaman',
            'background_image': 'Gambar latar belakang untuk header',
            'is_active': 'Centang untuk mengaktifkan header ini'
        }
    
    def clean_background_image(self):
        background_image = self.cleaned_data.get('background_image')
        if background_image:
            # Validasi ukuran file (maksimal 5MB)
            if background_image.size > 5 * 1024 * 1024:
                raise ValidationError('Ukuran file gambar maksimal 5MB.')
            
            # Validasi format file
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if background_image.content_type not in allowed_formats:
                raise ValidationError('Format file harus JPEG, PNG, GIF, atau WebP.')
        
        return background_image
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError('Judul halaman harus diisi.')
        if len(title) < 3:
            raise ValidationError('Judul halaman minimal 3 karakter.')
        return title
    
    def clean_page_type(self):
        page_type = self.cleaned_data.get('page_type')
        if not page_type:
            raise ValidationError('Jenis halaman harus dipilih.')
        return page_type


# Form untuk pencarian dan filter
class VillageProfileSearchForm(forms.Form):
    """Form untuk pencarian profil desa"""
    
    search_query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Cari profil desa...'
        }),
        label='Kata Kunci'
    )
    
    province = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Provinsi...'
        }),
        label='Provinsi'
    )
    
    regency = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Kabupaten...'
        }),
        label='Kabupaten'
    )
    
    is_active_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
        }),
        label='Hanya yang Aktif'
    )