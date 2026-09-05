from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from .models import Dusun, Lorong, Penduduk, DisabilitasType, DisabilitasData, ReligionReference, Family, RW, RT


class DusunForm(forms.ModelForm):
    class Meta:
        model = Dusun
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'area_size': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'name': 'Nama Dusun',
            'code': 'Kode Dusun',
            'area_size': 'Luas Area (Hektar)',
            'population_count': 'Jumlah Penduduk',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }


class LorongForm(forms.ModelForm):
    class Meta:
        model = Lorong
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'length': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'name': 'Nama Lorong',
            'code': 'Kode Lorong',
            'dusun': 'Dusun',
            'length': 'Panjang (Meter)',
            'house_count': 'Jumlah Rumah',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }


class PendudukForm(forms.ModelForm):
    class Meta:
        model = Penduduk
        fields = '__all__'
        exclude = ['created_by', 'updated_by']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'passport_expiry': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'height': forms.NumberInput(attrs={'min': '0', 'max': '300'}),
            'weight': forms.NumberInput(attrs={'min': '0', 'max': '500'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '08123456789'}),
            'mobile_number': forms.TextInput(attrs={'placeholder': '08123456789'}),
            'rt_number': forms.TextInput(attrs={'maxlength': '3'}),
            'rw_number': forms.TextInput(attrs={'maxlength': '3'}),
            'postal_code': forms.TextInput(attrs={'maxlength': '5'}),
        }
    
    def clean_nik(self):
        nik = self.cleaned_data.get('nik')
        if nik:
            # Check NIK format (16 digits)
            if not nik.isdigit() or len(nik) != 16:
                raise ValidationError('NIK harus berupa 16 digit angka.')
            
            # Check for duplicate NIK
            queryset = Penduduk.objects.filter(nik=nik)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError('NIK sudah terdaftar dalam sistem.')
        return nik
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            if birth_date > today:
                raise ValidationError('Tanggal lahir tidak boleh di masa depan.')
            
            # Check if age is reasonable (not more than 150 years)
            age = today.year - birth_date.year
            if age > 150:
                raise ValidationError('Usia tidak boleh lebih dari 150 tahun.')
        return birth_date
    
    def clean_kk_number(self):
        kk_number = self.cleaned_data.get('kk_number')
        if kk_number:
            # Check KK number format (16 digits)
            if not kk_number.isdigit() or len(kk_number) != 16:
                raise ValidationError('Nomor KK harus berupa 16 digit angka.')
        return kk_number
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, phone))
            # Check if it's a valid Indonesian phone number
            if not phone.startswith(('08', '62')) or len(phone) < 10:
                raise ValidationError('Nomor telepon tidak valid. Gunakan format 08xxxxxxxxx atau 62xxxxxxxxx.')
        return phone
    
    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if mobile:
            # Remove any non-digit characters
            mobile = ''.join(filter(str.isdigit, mobile))
            # Check if it's a valid Indonesian mobile number
            if not mobile.startswith(('08', '62')) or len(mobile) < 10:
                raise ValidationError('Nomor HP tidak valid. Gunakan format 08xxxxxxxxx atau 62xxxxxxxxx.')
        return mobile
    
    def clean(self):
        cleaned_data = super().clean()
        death_date = cleaned_data.get('death_date')
        is_alive = cleaned_data.get('is_alive')
        birth_date = cleaned_data.get('birth_date')
        
        # Validate death date logic
        if death_date and is_alive:
            raise ValidationError('Tidak bisa memasukkan tanggal meninggal jika status masih hidup.')
        
        if not is_alive and not death_date:
            raise ValidationError('Tanggal meninggal harus diisi jika status tidak hidup.')
        
        if death_date and birth_date and death_date <= birth_date:
            raise ValidationError('Tanggal meninggal harus setelah tanggal lahir.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Auto-grouping: if KK number is provided, handle family creation/linking
        if instance.kk_number:
            try:
                # Find existing family with same KK number
                family = Family.objects.get(kk_number=instance.kk_number)
                if family.head and not instance.family_head:
                    # If family has a head and this person doesn't have family_head set
                    instance.family_head = family.head
                elif not family.head and not instance.family_head:
                    # If family doesn't have a head, make this person the head
                    family.head = instance
                    if commit:
                        family.save()
            except Family.DoesNotExist:
                # Create new family if it doesn't exist
                if commit:
                    instance.save()  # Save instance first to get ID
                    family = Family.objects.create(
                        kk_number=instance.kk_number,
                        head=instance,
                        dusun=instance.dusun,
                        lorong=instance.lorong,
                        address=instance.address,
                        rt_number=instance.rt_number,
                        rw_number=instance.rw_number,
                        house_number=instance.house_number,
                        postal_code=instance.postal_code,
                    )
                    return instance
        
        if commit:
            instance.save()
        return instance

        labels = {
            'nik': 'NIK',
            'name': 'Nama Lengkap',
            'gender': 'Jenis Kelamin',
            'birth_place': 'Tempat Lahir',
            'birth_date': 'Tanggal Lahir',
            'religion': 'Agama',
            'education': 'Pendidikan',
            'occupation': 'Pekerjaan',
            'marital_status': 'Status Perkawinan',
            'kk_number': 'Nomor Kartu Keluarga',
            'family_head': 'Kepala Keluarga',
            'relationship_to_head': 'Hubungan dengan Kepala Keluarga',
            'blood_type': 'Golongan Darah',
            'height': 'Tinggi Badan (cm)',
            'weight': 'Berat Badan (kg)',
            'phone_number': 'Nomor Telepon',
            'mobile_number': 'Nomor HP',
            'email': 'Email',
            'dusun': 'Dusun',
            'lorong': 'Lorong',
            'rt_number': 'Nomor RT',
            'rw_number': 'Nomor RW',
            'house_number': 'Nomor Rumah',
            'address': 'Alamat Lengkap',
            'postal_code': 'Kode Pos',
            'citizenship': 'Kewarganegaraan',
            'passport_number': 'Nomor Paspor',
            'passport_expiry': 'Berlaku Hingga',
            'emergency_contact': 'Kontak Darurat',
            'emergency_phone': 'Telepon Darurat',
            'emergency_relationship': 'Hubungan dengan Kontak Darurat',
            'is_active': 'Aktif',
            'is_alive': 'Masih Hidup',
            'death_date': 'Tanggal Meninggal',
            'death_place': 'Tempat Meninggal',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make family_head choices more user-friendly
        if 'family_head' in self.fields:
            self.fields['family_head'].queryset = Penduduk.objects.filter(is_active=True).order_by('name')
            self.fields['family_head'].empty_label = "Pilih Kepala Keluarga (kosongkan jika kepala keluarga)"
        
        # Make dusun and lorong choices more user-friendly
        if 'dusun' in self.fields:
            self.fields['dusun'].queryset = Dusun.objects.filter(is_active=True).order_by('name')
        
        if 'lorong' in self.fields:
            self.fields['lorong'].queryset = Lorong.objects.filter(is_active=True).order_by('nama_lorong')
            self.fields['lorong'].empty_label = "Pilih Lorong (opsional)"


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'total_income': forms.NumberInput(attrs={'step': '1000', 'min': '0'}),
            'rt_number': forms.TextInput(attrs={'maxlength': '3'}),
            'rw_number': forms.TextInput(attrs={'maxlength': '3'}),
            'postal_code': forms.TextInput(attrs={'maxlength': '5'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '08123456789'}),
        }
        labels = {
            'kk_number': 'Nomor Kartu Keluarga',
            'head': 'Kepala Keluarga',
            'family_status': 'Status Keluarga',
            'total_members': 'Jumlah Anggota',
            'total_income': 'Total Pendapatan per Bulan (Rp)',
            'address': 'Alamat Keluarga',
            'dusun': 'Dusun',
            'lorong': 'Lorong',
            'rt_number': 'Nomor RT',
            'rw_number': 'Nomor RW',
            'house_number': 'Nomor Rumah',
            'postal_code': 'Kode Pos',
            'phone_number': 'Nomor Telepon',
            'is_active': 'Aktif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make head choices more user-friendly
        if 'head' in self.fields:
            self.fields['head'].queryset = Penduduk.objects.filter(is_active=True).order_by('name')
        
        # Make dusun and lorong choices more user-friendly
        if 'dusun' in self.fields:
            self.fields['dusun'].queryset = Dusun.objects.filter(is_active=True).order_by('name')
        
        if 'lorong' in self.fields:
            self.fields['lorong'].queryset = Lorong.objects.filter(is_active=True).order_by('name')
            self.fields['lorong'].empty_label = "Pilih Lorong (opsional)"
    
    def clean_kk_number(self):
        kk_number = self.cleaned_data.get('kk_number')
        if kk_number:
            # Check KK number format (16 digits)
            if not kk_number.isdigit() or len(kk_number) != 16:
                raise ValidationError('Nomor KK harus berupa 16 digit angka.')
            
            # Check if family with this KK already exists
            queryset = Family.objects.filter(kk_number=kk_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError('Nomor KK sudah terdaftar dalam sistem.')
        return kk_number
    
    def clean_total_income(self):
        income = self.cleaned_data.get('total_income')
        if income and income < 0:
            raise ValidationError('Pendapatan tidak boleh negatif.')
        return income
    
    def clean_total_members(self):
        members = self.cleaned_data.get('total_members')
        if members and members < 1:
            raise ValidationError('Jumlah anggota keluarga minimal 1 orang.')
        return members


class DisabilitasTypeForm(forms.ModelForm):
    class Meta:
        model = DisabilitasType
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Nama Jenis Disabilitas',
            'code': 'Kode',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }


class DisabilitasDataForm(forms.ModelForm):
    class Meta:
        model = DisabilitasData
        fields = '__all__'
        widgets = {
            'diagnosis_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'penduduk': 'Penduduk',
            'disability_type': 'Jenis Disabilitas',
            'severity': 'Tingkat Keparahan',
            'description': 'Deskripsi',
            'diagnosis_date': 'Tanggal Diagnosis',
            'needs_assistance': 'Memerlukan Bantuan',
            'is_active': 'Aktif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make choices more user-friendly
        if 'penduduk' in self.fields:
            self.fields['penduduk'].queryset = Penduduk.objects.filter(is_active=True).order_by('name')
        
        if 'disability_type' in self.fields:
            self.fields['disability_type'].queryset = DisabilitasType.objects.filter(is_active=True).order_by('name')


class ReligionReferenceForm(forms.ModelForm):
    class Meta:
        model = ReligionReference
        fields = '__all__'
        labels = {
            'name': 'Nama Agama',
            'code': 'Kode',
            'is_active': 'Aktif',
        }


class RWForm(forms.ModelForm):
    class Meta:
        model = RW
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'dusun': 'Dusun',
            'rw_number': 'Nomor RW',
            'ketua_rw': 'Ketua RW',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make choices more user-friendly
        if 'dusun' in self.fields:
            self.fields['dusun'].queryset = Dusun.objects.filter(is_active=True).order_by('name')
        
        if 'ketua_rw' in self.fields:
            self.fields['ketua_rw'].queryset = Penduduk.objects.filter(is_active=True).order_by('name')
            self.fields['ketua_rw'].empty_label = "Pilih Ketua RW (opsional)"


class RTForm(forms.ModelForm):
    class Meta:
        model = RT
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'rw': 'RW',
            'rt_number': 'Nomor RT',
            'ketua_rt': 'Ketua RT',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make choices more user-friendly
        if 'rw' in self.fields:
            self.fields['rw'].queryset = RW.objects.filter(is_active=True).order_by('dusun__name', 'rw_number')
        
        if 'ketua_rt' in self.fields:
            self.fields['ketua_rt'].queryset = Penduduk.objects.filter(is_active=True).order_by('name')
            self.fields['ketua_rt'].empty_label = "Pilih Ketua RT (opsional)"