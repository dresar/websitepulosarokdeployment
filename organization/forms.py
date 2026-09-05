from django import forms
from .models import LembagaAdat, PenggerakPKK, Kepemudaan, KarangTaruna
from village_profile.models import VillageOfficial
# from references.models import Penduduk  # COMMENTED OUT - references app disabled
# Using letters app models instead
try:
    from letters.models import Penduduk
except ImportError:
    Penduduk = None

class PerangkatDesaForm(forms.ModelForm):
    
    class Meta:
        model = VillageOfficial
        fields = ['village', 'name', 'position', 'custom_position', 'photo', 'nik', 'birth_date', 'birth_place', 
                 'gender', 'religion', 'education', 'occupation', 'marital_status', 'experience',
                 'phone', 'mobile', 'email', 'address', 'dusun', 'lorong', 'rt_number', 'rw_number',
                 'house_number', 'postal_code', 'start_date', 'end_date', 'is_active', 'display_order']
        widgets = {
            'village': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Lengkap'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'custom_position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jabatan Khusus'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
            'nik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIK'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'birth_place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tempat Lahir'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Agama'}),
            'education': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pendidikan'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pekerjaan'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Pengalaman'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telepon'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Handphone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat'}),
            'dusun': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dusun'}),
            'lorong': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lorong'}),
            'rt_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RT'}),
            'rw_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RW'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor Rumah'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kode Pos'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Urutan Tampil'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['village'].required = True
        self.fields['name'].required = True
        self.fields['position'].required = True
        self.fields['start_date'].required = True
        
        # Set default value for display_order
        if not self.instance.pk:  # Only for new instances
            self.fields['display_order'].initial = 0
        
        # Populate village choices
        try:
            from village_profile.models import VillageProfile
            self.fields['village'].queryset = VillageProfile.objects.all()
        except ImportError:
            pass
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError('Tanggal berakhir jabatan harus setelah tanggal mulai jabatan.')
        
        return cleaned_data

class LembagaAdatForm(forms.ModelForm):
    class Meta:
        model = LembagaAdat
        fields = ['nama_lembaga', 'jenis_lembaga', 'ketua', 'sekretaris', 'bendahara', 
                 'tanggal_terbentuk', 'alamat_sekretariat', 'deskripsi', 'kegiatan_rutin', 
                 'jumlah_anggota', 'status', 'kontak_phone', 'foto_kegiatan']
        widgets = {
            'nama_lembaga': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Lembaga'}),
            'jenis_lembaga': forms.Select(attrs={'class': 'form-control'}),
            'ketua': forms.Select(attrs={'class': 'form-control'}),
            'sekretaris': forms.Select(attrs={'class': 'form-control'}),
            'bendahara': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_terbentuk': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'alamat_sekretariat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alamat Sekretariat'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deskripsi Lembaga'}),
            'kegiatan_rutin': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Kegiatan Rutin'}),
            'jumlah_anggota': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah Anggota'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'kontak_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor Telepon'}),
            'foto_kegiatan': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['nama_lembaga'].required = True
        self.fields['jenis_lembaga'].required = True
        self.fields['ketua'].required = True
        self.fields['status'].required = True
        self.fields['tanggal_terbentuk'].required = True
        
        # Set default value for jumlah_anggota
        if not self.instance.pk:  # Only for new instances
            self.fields['jumlah_anggota'].initial = 0
        
        # Populate choices for ForeignKey fields
        if Penduduk:
            self.fields['ketua'].queryset = Penduduk.objects.all()
            self.fields['sekretaris'].queryset = Penduduk.objects.all()
            self.fields['bendahara'].queryset = Penduduk.objects.all()
            
            # Add empty choice for optional fields
            self.fields['sekretaris'].empty_label = "Pilih Sekretaris (Opsional)"
            self.fields['bendahara'].empty_label = "Pilih Bendahara (Opsional)"

class PenggerakPKKForm(forms.ModelForm):
    class Meta:
        model = PenggerakPKK
        fields = ['penduduk', 'jabatan', 'nomor_anggota', 'tanggal_bergabung', 'tanggal_keluar', 
                 'status', 'keahlian', 'pengalaman_organisasi', 'prestasi', 'foto_profil', 
                 'kontak_whatsapp', 'alamat_lengkap', 'email', 'deskripsi_tugas', 'sk_pengangkatan',
                 'tanggal_mulai_tugas', 'tanggal_selesai_tugas']
        widgets = {
            'penduduk': forms.Select(attrs={'class': 'form-control'}),
            'jabatan': forms.Select(attrs={'class': 'form-control'}),
            'nomor_anggota': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor Anggota'}),
            'tanggal_bergabung': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_keluar': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'keahlian': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Keahlian yang dimiliki'}),
            'pengalaman_organisasi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Pengalaman Organisasi'}),
            'prestasi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Prestasi'}),
            'foto_profil': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
            'kontak_whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor WhatsApp'}),
            'alamat_lengkap': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alamat Lengkap'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'deskripsi_tugas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deskripsi Tugas'}),
            'sk_pengangkatan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor SK Pengangkatan'}),
            'tanggal_mulai_tugas': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_selesai_tugas': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['penduduk'].required = True
        self.fields['jabatan'].required = True
        self.fields['tanggal_mulai_tugas'].required = True
        self.fields['status'].required = True
        
        # Populate choices for ForeignKey fields
        if Penduduk:
            self.fields['penduduk'].queryset = Penduduk.objects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        tanggal_bergabung = cleaned_data.get('tanggal_bergabung')
        tanggal_keluar = cleaned_data.get('tanggal_keluar')
        
        if tanggal_bergabung and tanggal_keluar:
            if tanggal_keluar <= tanggal_bergabung:
                raise forms.ValidationError('Tanggal keluar harus setelah tanggal bergabung.')
        
        return cleaned_data

class KepemudaanForm(forms.ModelForm):
    class Meta:
        model = Kepemudaan
        fields = ['nama_organisasi', 'jenis_organisasi', 'ketua', 'sekretaris', 'bendahara', 
                 'tanggal_terbentuk', 'jumlah_anggota_aktif', 'rentang_usia', 
                 'kegiatan_rutin', 'prestasi', 'alamat_sekretariat', 'status', 
                 'kontak_phone', 'email', 'foto_kegiatan', 'deskripsi']
        widgets = {
            'nama_organisasi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Organisasi'}),
            'jenis_organisasi': forms.Select(attrs={'class': 'form-control'}),
            'ketua': forms.Select(attrs={'class': 'form-control'}),
            'sekretaris': forms.Select(attrs={'class': 'form-control'}),
            'bendahara': forms.Select(attrs={'class': 'form-control'}),
            'tanggal_terbentuk': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'jumlah_anggota_aktif': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah Anggota Aktif'}),
            'rentang_usia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 15-30 tahun'}),
            'kegiatan_rutin': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Kegiatan Rutin'}),
            'prestasi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Prestasi'}),
            'alamat_sekretariat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alamat Sekretariat'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'kontak_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor Telepon'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'foto_kegiatan': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deskripsi'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['nama_organisasi'].required = True
        self.fields['jenis_organisasi'].required = True
        self.fields['ketua'].required = True
        self.fields['status'].required = True
        self.fields['tanggal_terbentuk'].required = True
        
        # Populate choices for ForeignKey fields
        if Penduduk:
            self.fields['ketua'].queryset = Penduduk.objects.all()
            self.fields['sekretaris'].queryset = Penduduk.objects.all()
            self.fields['bendahara'].queryset = Penduduk.objects.all()
            
            # Add empty choice for optional fields
            self.fields['sekretaris'].empty_label = "Pilih Sekretaris (Opsional)"
            self.fields['bendahara'].empty_label = "Pilih Bendahara (Opsional)"

class KarangTarunaForm(forms.ModelForm):
    class Meta:
        model = KarangTaruna
        fields = ['penduduk', 'jabatan', 'nomor_anggota', 'tanggal_bergabung', 'tanggal_keluar', 
                 'status', 'bidang_keahlian', 'pengalaman_organisasi', 'prestasi_individu', 
                 'kontribusi', 'foto_profil', 'kontak_whatsapp', 'email_pribadi', 'alamat_lengkap', 
                 'pendidikan_terakhir', 'pekerjaan', 'is_pengurus_inti']
        widgets = {
            'penduduk': forms.Select(attrs={'class': 'form-control'}),
            'jabatan': forms.Select(attrs={'class': 'form-control'}),
            'nomor_anggota': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor Anggota'}),
            'tanggal_bergabung': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_keluar': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'bidang_keahlian': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Bidang Keahlian'}),
            'pengalaman_organisasi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Pengalaman Organisasi'}),
            'prestasi_individu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Prestasi Individu'}),
            'kontribusi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Kontribusi'}),
            'foto_profil': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
            'kontak_whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor WhatsApp'}),
            'email_pribadi': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Pribadi'}),
            'alamat_lengkap': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alamat Lengkap'}),
            'pendidikan_terakhir': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pendidikan Terakhir'}),
            'pekerjaan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pekerjaan'}),
            'is_pengurus_inti': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['penduduk'].required = True
        self.fields['jabatan'].required = True
        self.fields['tanggal_bergabung'].required = True
        self.fields['status'].required = True
        
        # Populate choices for ForeignKey fields
        if Penduduk:
            self.fields['penduduk'].queryset = Penduduk.objects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        tanggal_bergabung = cleaned_data.get('tanggal_bergabung')
        tanggal_keluar = cleaned_data.get('tanggal_keluar')
        
        if tanggal_bergabung and tanggal_keluar:
            if tanggal_keluar <= tanggal_bergabung:
                raise forms.ValidationError('Tanggal keluar harus setelah tanggal bergabung.')
        
        return cleaned_data