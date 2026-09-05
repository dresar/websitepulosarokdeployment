from django import forms
from django.contrib.auth import get_user_model
from .models import Document, DocumentCategory, DocumentComment

User = get_user_model()

# Import Penduduk model - try references first, then letters as fallback
try:
    from references.models import Penduduk
    print("Documents forms: Using references.models.Penduduk")
except ImportError:
    try:
        from letters.models import Penduduk
        print("Documents forms: Using letters.models.Penduduk")
    except ImportError:
        Penduduk = None
        print("Documents forms: No Penduduk model found")


class DocumentForm(forms.ModelForm):
    """Form for creating and editing documents"""
    
    class Meta:
        model = Document
        fields = [
            'title', 'document_number', 'category', 'document_category',
            'summary', 'status', 'priority', 'applicant',
            'recipient', 'sender', 'document_date', 'file_attachment',
            'notes', 'tags'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan judul dokumen'
            }),
            'document_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor dokumen (opsional)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'document_category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ringkasan dokumen (opsional)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'applicant': forms.Select(attrs={
                'class': 'form-control'
            }),
            'recipient': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama penerima (opsional)'
            }),
            'sender': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama pengirim (opsional)'
            }),
            'document_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'file_attachment': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Catatan tambahan (opsional)'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tags dipisahkan dengan koma (opsional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make applicant field optional and use text input for search
        if Penduduk:
            self.fields['applicant'].widget = forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cari penduduk (opsional)',
                'id': 'applicant_search'
            })
            self.fields['applicant'].required = False
            # Hide the original field and add a hidden field for the ID
            self.fields['applicant'].widget = forms.HiddenInput()
            self.fields['applicant_id'] = forms.IntegerField(
                required=False,
                widget=forms.HiddenInput(attrs={'id': 'applicant_id'})
            )
        else:
            self.fields['applicant'].widget = forms.HiddenInput()
            self.fields['applicant'].required = False
        
        # Make document_category optional
        self.fields['document_category'].required = False
        
        # Set default values
        if not self.instance.pk:
            self.fields['status'].initial = 'draft'
            self.fields['priority'].initial = 'normal'


class DocumentCategoryForm(forms.ModelForm):
    """Form for creating and editing document categories"""
    
    class Meta:
        model = DocumentCategory
        fields = ['name', 'description', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama kategori'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deskripsi kategori (opsional)'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'placeholder': '#007bff'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class DocumentCommentForm(forms.ModelForm):
    """Form for adding comments to documents"""
    
    class Meta:
        model = DocumentComment
        fields = ['comment', 'is_internal']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tulis komentar...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_internal'].label = 'Komentar Internal (tidak terlihat oleh pemohon)'


class DocumentSearchForm(forms.Form):
    """Form for searching documents"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari dokumen...'
        })
    )
    category = forms.ChoiceField(
        choices=[('', 'Semua Kategori')] + list(Document.CATEGORY_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'Semua Status')] + list(Document.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )