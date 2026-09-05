from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Role, MenuPermission, UserRole, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    position = forms.CharField(max_length=100, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    is_village_staff = forms.BooleanField(required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 
                 'position', 'address', 'is_village_staff', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.position = self.cleaned_data['position']
        user.address = self.cleaned_data['address']
        user.is_village_staff = self.cleaned_data['is_village_staff']
        
        if commit:
            user.save()
        return user


class RoleForm(forms.ModelForm):
    """Form for creating and editing roles"""
    
    class Meta:
        model = Role
        fields = ['name', 'display_name', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = 'Nama unik untuk role (huruf kecil, underscore)'
        self.fields['display_name'].help_text = 'Nama yang ditampilkan untuk role'
        self.fields['description'].help_text = 'Deskripsi singkat tentang role ini'


class RolePermissionForm(forms.ModelForm):
    """Form for managing role permissions"""
    menu_permissions = forms.ModelMultipleChoiceField(
        queryset=MenuPermission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Pilih permission yang akan diberikan kepada role ini'
    )
    
    class Meta:
        model = Role
        fields = ['menu_permissions']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['menu_permissions'].initial = self.instance.menu_permissions.all()
    
    def save(self, commit=True):
        role = super().save(commit=False)
        if commit:
            role.save()
            role.menu_permissions.set(self.cleaned_data['menu_permissions'])
        return role


class UserRoleForm(forms.ModelForm):
    """Form for managing user roles"""
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Pilih role yang akan diberikan kepada user ini'
    )
    
    class Meta:
        model = CustomUser
        fields = ['roles']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['roles'].initial = self.instance.roles.all()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.roles.set(self.cleaned_data['roles'])
        return user


class UserProfileForm(forms.ModelForm):
    """Form for user profile"""
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'address', 'birth_date']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class UserEditForm(forms.ModelForm):
    """Form for editing user basic information"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 
                 'position', 'address', 'is_village_staff', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Nama pengguna untuk login'
        self.fields['email'].help_text = 'Email address user'
        self.fields['is_village_staff'].help_text = 'Centang jika user adalah staff desa'
        self.fields['is_active'].help_text = 'Centang jika user dapat login'


class PermissionFilterForm(forms.Form):
    """Form for filtering permissions"""
    module = forms.ChoiceField(
        choices=[('', 'Semua Module')] + MenuPermission.MODULE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    action = forms.ChoiceField(
        choices=[('', 'Semua Action')] + MenuPermission.ACTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.ChoiceField(
        choices=[('', 'Semua Status'), (True, 'Aktif'), (False, 'Non-Aktif')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class RoleFilterForm(forms.Form):
    """Form for filtering roles"""
    name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cari role...'})
    )
    is_active = forms.ChoiceField(
        choices=[('', 'Semua Status'), (True, 'Aktif'), (False, 'Non-Aktif')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class UserFilterForm(forms.Form):
    """Form for filtering users"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cari user...'})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.filter(is_active=True),
        required=False,
        empty_label="Semua Role",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.ChoiceField(
        choices=[('', 'Semua Status'), (True, 'Aktif'), (False, 'Non-Aktif')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )