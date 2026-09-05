from django import forms
from .models import Business, BusinessCategory, UKM, Koperasi, BUMG, LayananJasa

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            'name', 'business_type', 'category', 'description', 'address', 
            'phone', 'email', 'website', 'status', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'business-form-control'}),
            'business_type': forms.Select(attrs={'class': 'business-form-control'}),
            'category': forms.Select(attrs={'class': 'business-form-control'}),
            'description': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'business-form-control'}),
            'email': forms.EmailInput(attrs={'class': 'business-form-control'}),
            'website': forms.URLInput(attrs={'class': 'business-form-control'}),
            'status': forms.Select(attrs={'class': 'business-form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'business-form-control'}),
        }

class UKMForm(forms.ModelForm):
    class Meta:
        model = UKM
        fields = [
            'nama_usaha', 'pemilik', 'nik_pemilik', 'alamat_usaha', 'alamat_pemilik',
            'jenis_usaha', 'skala_usaha', 'modal_awal', 'omzet_bulanan', 'jumlah_karyawan',
            'tanggal_mulai', 'nomor_izin', 'telepon', 'email', 'produk_utama', 'target_pasar',
            'status', 'keterangan'
        ]
        widgets = {
            'nama_usaha': forms.TextInput(attrs={'class': 'business-form-control'}),
            'pemilik': forms.TextInput(attrs={'class': 'business-form-control penduduk-autocomplete'}),
            'nik_pemilik': forms.TextInput(attrs={'class': 'business-form-control'}),
            'alamat_usaha': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 2}),
            'alamat_pemilik': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 2}),
            'jenis_usaha': forms.TextInput(attrs={'class': 'business-form-control'}),
            'skala_usaha': forms.Select(attrs={'class': 'business-form-control'}),
            'modal_awal': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'omzet_bulanan': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'jumlah_karyawan': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'tanggal_mulai': forms.DateInput(attrs={'class': 'business-form-control', 'type': 'date'}),
            'nomor_izin': forms.TextInput(attrs={'class': 'business-form-control'}),
            'telepon': forms.TextInput(attrs={'class': 'business-form-control'}),
            'email': forms.EmailInput(attrs={'class': 'business-form-control'}),
            'produk_utama': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 2}),
            'target_pasar': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'business-form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 3}),
        }

class KoperasiForm(forms.ModelForm):
    class Meta:
        model = Koperasi
        fields = [
            'nama', 'nomor_badan_hukum', 'tanggal_berdiri', 'alamat',
            'ketua', 'sekretaris', 'bendahara', 'jumlah_anggota', 
            'modal_dasar', 'modal_disetor', 'jenis_koperasi',
            'telepon', 'email', 'status', 'keterangan'
        ]
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'business-form-control'}),
            'nomor_badan_hukum': forms.TextInput(attrs={'class': 'business-form-control'}),
            'tanggal_berdiri': forms.DateInput(attrs={'class': 'business-form-control', 'type': 'date'}),
            'alamat': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 2}),
            'ketua': forms.TextInput(attrs={'class': 'business-form-control'}),
            'sekretaris': forms.TextInput(attrs={'class': 'business-form-control'}),
            'bendahara': forms.TextInput(attrs={'class': 'business-form-control'}),
            'jumlah_anggota': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'modal_dasar': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'modal_disetor': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'jenis_koperasi': forms.TextInput(attrs={'class': 'business-form-control'}),
            'telepon': forms.TextInput(attrs={'class': 'business-form-control'}),
            'email': forms.EmailInput(attrs={'class': 'business-form-control'}),
            'status': forms.Select(attrs={'class': 'business-form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 3}),
        }

class BUMGForm(forms.ModelForm):
    class Meta:
        model = BUMG
        fields = [
            'nama', 'nomor_sk', 'tanggal_sk', 'alamat', 'direktur', 'komisaris',
            'modal_dasar', 'modal_disetor', 'bidang_usaha', 'telepon', 'email', 
            'website', 'status', 'keterangan'
        ]
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'business-form-control'}),
            'nomor_sk': forms.TextInput(attrs={'class': 'business-form-control'}),
            'tanggal_sk': forms.DateInput(attrs={'class': 'business-form-control', 'type': 'date'}),
            'alamat': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 2}),
            'direktur': forms.TextInput(attrs={'class': 'business-form-control'}),
            'komisaris': forms.TextInput(attrs={'class': 'business-form-control'}),
            'modal_dasar': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'modal_disetor': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'bidang_usaha': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 2}),
            'telepon': forms.TextInput(attrs={'class': 'business-form-control'}),
            'email': forms.EmailInput(attrs={'class': 'business-form-control'}),
            'website': forms.URLInput(attrs={'class': 'business-form-control'}),
            'status': forms.Select(attrs={'class': 'business-form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 3}),
        }

class LayananJasaForm(forms.ModelForm):
    class Meta:
        model = LayananJasa
        fields = [
            'nama', 'penyedia', 'alamat', 'telepon', 'email', 'kategori', 'deskripsi',
            'pengalaman', 'harga_min', 'harga_max', 'satuan_harga', 'waktu_layanan', 
            'area_layanan', 'rating', 'website', 'keunggulan', 'syarat_ketentuan', 
            'sertifikat', 'status', 'keterangan'
        ]
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'business-form-control'}),
            'penyedia': forms.TextInput(attrs={'class': 'business-form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 2}),
            'telepon': forms.TextInput(attrs={'class': 'business-form-control'}),
            'email': forms.EmailInput(attrs={'class': 'business-form-control'}),
            'kategori': forms.TextInput(attrs={'class': 'business-form-control'}),
            'deskripsi': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 3}),
            'pengalaman': forms.TextInput(attrs={'class': 'business-form-control'}),
            'harga_min': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'harga_max': forms.NumberInput(attrs={'class': 'business-form-control'}),
            'satuan_harga': forms.TextInput(attrs={'class': 'business-form-control'}),
            'waktu_layanan': forms.TextInput(attrs={'class': 'business-form-control'}),
            'area_layanan': forms.TextInput(attrs={'class': 'business-form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'business-form-control', 'step': '0.1'}),
            'website': forms.URLInput(attrs={'class': 'business-form-control'}),
            'keunggulan': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 3}),
            'syarat_ketentuan': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 3}),
            'sertifikat': forms.TextInput(attrs={'class': 'business-form-control'}),
            'status': forms.Select(attrs={'class': 'business-form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'business-form-control', 'rows': 3}),
        }
