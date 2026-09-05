from django import forms
from django.core.validators import EmailValidator
from django.utils import timezone
from .models import Complaint, ComplaintCategory, ChatMessage, ChatSession, Contact, ComplaintVerification


class ComplaintForm(forms.ModelForm):
    """Formulir untuk membuat pengaduan baru"""
    
    class Meta:
        model = Complaint
        fields = [
            'reporter_name', 'reporter_email', 'reporter_phone', 'reporter_address',
            'category', 'title', 'description', 'location', 'incident_date',
            'attachment', 'priority'
        ]
        
        widgets = {
            'reporter_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama lengkap Anda',
                'required': True
            }),
            'reporter_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contoh@email.com',
                'required': True
            }),
            'reporter_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '08xxxxxxxxxx',
                'pattern': '[0-9]{10,15}'
            }),
            'reporter_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Alamat lengkap Anda'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Judul singkat pengaduan Anda',
                'required': True,
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Jelaskan detail pengaduan Anda dengan lengkap',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lokasi kejadian (opsional)'
            }),
            'incident_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png,.pdf,.doc,.docx'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        
        labels = {
            'reporter_name': 'Nama Lengkap *',
            'reporter_email': 'Email *',
            'reporter_phone': 'Nomor Telepon',
            'reporter_address': 'Alamat',
            'category': 'Kategori Pengaduan *',
            'title': 'Judul Pengaduan *',
            'description': 'Deskripsi Pengaduan *',
            'location': 'Lokasi Kejadian',
            'incident_date': 'Tanggal Kejadian',
            'attachment': 'File Lampiran',
            'priority': 'Tingkat Prioritas'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter kategori yang aktif saja
        self.fields['category'].queryset = ComplaintCategory.objects.filter(is_active=True)
        
        # Set default priority ke medium
        if not self.instance.pk:
            self.fields['priority'].initial = 'medium'
    
    def clean_reporter_email(self):
        email = self.cleaned_data.get('reporter_email')
        if email:
            validator = EmailValidator()
            validator(email)
        return email
    
    def clean_reporter_phone(self):
        phone = self.cleaned_data.get('reporter_phone')
        if phone:
            # Hapus spasi dan karakter non-digit
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10 or len(phone) > 15:
                raise forms.ValidationError('Nomor telepon harus antara 10-15 digit')
        return phone
    
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Validasi ukuran file (maksimal 5MB)
            if attachment.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Ukuran file tidak boleh lebih dari 5MB')
            
            # Validasi tipe file
            allowed_types = ['image/jpeg', 'image/png', 'application/pdf', 
                           'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if attachment.content_type not in allowed_types:
                raise forms.ValidationError('Tipe file tidak didukung. Gunakan JPG, PNG, PDF, DOC, atau DOCX')
        
        return attachment


class ComplaintTrackingForm(forms.Form):
    """Formulir untuk tracking pengaduan berdasarkan ID"""
    
    complaint_id = forms.CharField(
        max_length=36,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan ID Pengaduan Anda',
            'required': True
        }),
        label='ID Pengaduan'
    )
    
    reporter_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email yang digunakan saat membuat pengaduan',
            'required': True
        }),
        label='Email Pelapor'
    )


class ChatMessageForm(forms.ModelForm):
    """Formulir untuk mengirim pesan chat"""
    
    class Meta:
        model = ChatMessage
        fields = ['content']
        
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ketik pesan Anda...',
                'required': True,
                'autocomplete': 'off'
            })
        }
        
        labels = {
            'content': ''
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            content = content.strip()
            if len(content) < 1:
                raise forms.ValidationError('Pesan tidak boleh kosong')
            if len(content) > 500:
                raise forms.ValidationError('Pesan terlalu panjang (maksimal 500 karakter)')
        return content


class ContactForm(forms.ModelForm):
    """Formulir untuk mengirim pesan kontak"""
    
    class Meta:
        model = Contact
        fields = [
            'sender_name', 'sender_email', 'sender_phone', 'is_anonymous',
            'subject_type', 'subject', 'message'
        ]
        
        widgets = {
            'sender_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white',
                'placeholder': 'Nama lengkap Anda',
                'required': True
            }),
            'sender_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white',
                'placeholder': 'alamat@email.com',
                'required': True
            }),
            'sender_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white',
                'placeholder': 'Nomor telepon (opsional)',
                'pattern': '[0-9]{10,15}'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2',
                'id': 'anonymous-checkbox'
            }),
            'subject_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white',
                'placeholder': 'Subjek atau topik pesan',
                'required': True,
                'maxlength': 200
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 resize-none bg-white',
                'rows': 6,
                'placeholder': 'Tulis pesan atau pertanyaan Anda dengan jelas...',
                'required': True
            })
        }
        
        labels = {
            'sender_name': 'Nama Lengkap *',
            'sender_email': 'Email *',
            'sender_phone': 'Nomor Telepon (opsional)',
            'is_anonymous': 'Kirim sebagai anonim',
            'subject_type': 'Jenis Pesan *',
            'subject': 'Subjek *',
            'message': 'Pesan *'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set kategori choices
        self.fields['subject_type'].choices = Contact.SUBJECT_CHOICES
    
    def clean_sender_email(self):
        email = self.cleaned_data.get('sender_email')
        if email:
            validator = EmailValidator()
            validator(email)
        return email
    
    def clean_sender_phone(self):
        phone = self.cleaned_data.get('sender_phone')
        if phone:
            # Remove spaces and validate format
            phone = phone.replace(' ', '').replace('-', '')
            if not phone.isdigit() or len(phone) < 10 or len(phone) > 15:
                raise forms.ValidationError('Nomor telepon tidak valid. Gunakan format: 08xxxxxxxxxx')
        return phone
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message or len(message.strip()) < 10:
            raise forms.ValidationError('Pesan terlalu pendek. Minimal 10 karakter.')
        if len(message) > 2000:
            raise forms.ValidationError('Pesan terlalu panjang. Maksimal 2000 karakter.')
        return message


class ComplaintVerificationForm(forms.ModelForm):
    """Formulir untuk verifikasi pengaduan"""
    
    class Meta:
        model = ComplaintVerification
        fields = [
            'verification_type', 'status', 'verification_notes', 
            'verification_result', 'supporting_evidence', 'recommended_action',
            'priority_level', 'requires_follow_up', 'follow_up_date', 'follow_up_notes'
        ]
        
        widgets = {
            'verification_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'verification_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Masukkan catatan verifikasi...',
                'required': True
            }),
            'verification_result': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Hasil verifikasi...'
            }),
            'supporting_evidence': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Bukti pendukung...'
            }),
            'recommended_action': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Rekomendasi tindakan...'
            }),
            'priority_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'requires_follow_up': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'follow_up_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'follow_up_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Catatan tindak lanjut...'
            })
        }
        
        labels = {
            'verification_type': 'Jenis Verifikasi',
            'status': 'Status Verifikasi',
            'verification_notes': 'Catatan Verifikasi',
            'verification_result': 'Hasil Verifikasi',
            'supporting_evidence': 'Bukti Pendukung',
            'recommended_action': 'Rekomendasi Tindakan',
            'priority_level': 'Tingkat Prioritas',
            'requires_follow_up': 'Memerlukan Tindak Lanjut',
            'follow_up_date': 'Tanggal Tindak Lanjut',
            'follow_up_notes': 'Catatan Tindak Lanjut'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        if not self.instance.pk:
            self.fields['status'].initial = 'pending'
            self.fields['verification_type'].initial = 'initial'
            self.fields['priority_level'].initial = 'medium'
    
    def clean_follow_up_date(self):
        follow_up_date = self.cleaned_data.get('follow_up_date')
        requires_follow_up = self.cleaned_data.get('requires_follow_up')
        
        if requires_follow_up and not follow_up_date:
            raise forms.ValidationError('Tanggal tindak lanjut harus diisi jika memerlukan tindak lanjut.')
        
        if follow_up_date and follow_up_date <= timezone.now():
            raise forms.ValidationError('Tanggal tindak lanjut harus di masa depan.')
        
        return follow_up_date


class VerificationSearchForm(forms.Form):
    """Formulir pencarian verifikasi"""
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari berdasarkan ID pengaduan, catatan, atau hasil verifikasi...'
        }),
        label='Pencarian'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Semua Status')] + ComplaintVerification.VERIFICATION_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Status Verifikasi'
    )
    
    verification_type = forms.ChoiceField(
        choices=[('', 'Semua Jenis')] + ComplaintVerification.VERIFICATION_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Jenis Verifikasi'
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'Semua Prioritas')] + Complaint.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Prioritas'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Dari Tanggal'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Sampai Tanggal'
    )