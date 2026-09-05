from django import forms
from django.core.exceptions import ValidationError
from .models import LayananFeedback, LayananFAQ, LayananContact, LayananService

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = LayananFeedback
        fields = ['name', 'email', 'phone', 'category', 'status', 'subject', 'message', 'reply']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama lengkap',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan email',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nomor telepon (opsional)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan subjek feedback',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan pesan feedback',
                'rows': 4,
                'required': True
            }),
            'reply': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan balasan admin',
                'rows': 4
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise ValidationError('Email tidak valid')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValidationError('Nomor telepon hanya boleh berisi angka')
        return phone

class FAQForm(forms.ModelForm):
    class Meta:
        model = LayananFAQ
        fields = ['question', 'answer', 'category', 'is_active', 'order']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan pertanyaan',
                'required': True
            }),
            'answer': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan jawaban',
                'rows': 4,
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Urutan tampil (opsional)',
                'min': 0
            }),
        }
    
    def clean_question(self):
        question = self.cleaned_data.get('question')
        if question and len(question.strip()) < 10:
            raise ValidationError('Pertanyaan harus minimal 10 karakter')
        return question
    
    def clean_answer(self):
        answer = self.cleaned_data.get('answer')
        if answer and len(answer.strip()) < 20:
            raise ValidationError('Jawaban harus minimal 20 karakter')
        return answer

class ContactForm(forms.ModelForm):
    class Meta:
        model = LayananContact
        fields = ['name', 'position', 'phone', 'email', 'department', 'is_active', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama kontak',
                'required': True
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan jabatan',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nomor telepon',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan email',
                'required': True
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan departemen',
                'required': True
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Catatan tambahan (opsional)',
                'rows': 3
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValidationError('Nomor telepon hanya boleh berisi angka')
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise ValidationError('Email tidak valid')
        return email

class ServiceForm(forms.ModelForm):
    class Meta:
        model = LayananService
        fields = ['name', 'description', 'category', 'is_active', 'order', 'icon', 'url']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama layanan',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan deskripsi layanan',
                'rows': 4,
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Urutan tampil (opsional)',
                'min': 0
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama icon (Font Awesome)'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan URL layanan (opsional)'
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 3:
            raise ValidationError('Nama layanan harus minimal 3 karakter')
        return name
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise ValidationError('Deskripsi layanan harus minimal 10 karakter')
        return description

# Additional forms for modal operations
class QuickFeedbackForm(forms.ModelForm):
    """Simplified form for quick feedback creation"""
    class Meta:
        model = LayananFeedback
        fields = ['name', 'email', 'category', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama lengkap',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subjek',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Pesan',
                'rows': 3,
                'required': True
            }),
        }

class QuickFAQForm(forms.ModelForm):
    """Simplified form for quick FAQ creation"""
    class Meta:
        model = LayananFAQ
        fields = ['question', 'answer', 'category']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pertanyaan',
                'required': True
            }),
            'answer': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Jawaban',
                'rows': 3,
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

class QuickContactForm(forms.ModelForm):
    """Simplified form for quick contact creation"""
    class Meta:
        model = LayananContact
        fields = ['name', 'position', 'phone', 'email', 'department']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama',
                'required': True
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jabatan',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telepon',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'required': True
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Departemen',
                'required': True
            }),
        }

class QuickServiceForm(forms.ModelForm):
    """Simplified form for quick service creation"""
    class Meta:
        model = LayananService
        fields = ['name', 'description', 'category', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama layanan',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Deskripsi',
                'rows': 3,
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Icon (Font Awesome)'
            }),
        }

