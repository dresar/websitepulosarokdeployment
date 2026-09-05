from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

class PosyanduPermissions:
    """Class untuk mengelola permission posyandu"""
    
    @staticmethod
    def create_permissions():
        """Membuat permission untuk semua model posyandu"""
        permissions = []
        
        # Model yang memerlukan permission
        models_permissions = [
            ('posyandu', 'posyandulocation', 'Lokasi Posyandu'),
            ('posyandu', 'posyanduschedule', 'Jadwal Posyandu'),
            ('posyandu', 'healthrecord', 'Rekam Kesehatan'),
            ('posyandu', 'ibuhamil', 'Data Ibu Hamil'),
            ('posyandu', 'immunization', 'Data Imunisasi'),
            ('posyandu', 'posyandukader', 'Kader Posyandu'),
            ('posyandu', 'nutritiondata', 'Data Gizi'),
            ('posyandu', 'stuntingdata', 'Data Stunting'),
        ]
        
        for app_label, model_name, verbose_name in models_permissions:
            try:
                content_type = ContentType.objects.get(
                    app_label=app_label,
                    model=model_name
                )
                
                # Permission untuk setiap operasi CRUD
                permissions.extend([
                    Permission.objects.get_or_create(
                        codename=f'view_{model_name}',
                        name=f'Can view {verbose_name}',
                        content_type=content_type
                    )[0],
                    Permission.objects.get_or_create(
                        codename=f'add_{model_name}',
                        name=f'Can add {verbose_name}',
                        content_type=content_type
                    )[0],
                    Permission.objects.get_or_create(
                        codename=f'change_{model_name}',
                        name=f'Can change {verbose_name}',
                        content_type=content_type
                    )[0],
                    Permission.objects.get_or_create(
                        codename=f'delete_{model_name}',
                        name=f'Can delete {verbose_name}',
                        content_type=content_type
                    )[0],
                ])
            except ContentType.DoesNotExist:
                print(f"ContentType tidak ditemukan untuk {app_label}.{model_name}")
                continue
        
        return permissions

    @staticmethod
    def get_posyandu_permissions():
        """Mendapatkan semua permission posyandu"""
        return Permission.objects.filter(
            content_type__app_label='posyandu'
        ).order_by('content_type__model', 'codename')

    @staticmethod
    def assign_posyandu_admin_permissions(user):
        """Memberikan semua permission posyandu kepada user"""
        permissions = PosyanduPermissions.get_posyandu_permissions()
        user.user_permissions.set(permissions)
        return permissions.count()

    @staticmethod
    def assign_posyandu_kader_permissions(user):
        """Memberikan permission terbatas untuk kader posyandu"""
        # Kader hanya bisa view dan add, tidak bisa delete
        permissions = Permission.objects.filter(
            content_type__app_label='posyandu',
            codename__in=[
                'view_healthrecord', 'add_healthrecord', 'change_healthrecord',
                'view_ibuhamil', 'add_ibuhamil', 'change_ibuhamil',
                'view_immunization', 'add_immunization', 'change_immunization',
                'view_nutritiondata', 'add_nutritiondata', 'change_nutritiondata',
                'view_stuntingdata', 'add_stuntingdata', 'change_stuntingdata',
                'view_posyanduschedule', 'view_posyandulocation'
            ]
        )
        user.user_permissions.set(permissions)
        return permissions.count()

    @staticmethod
    def assign_posyandu_viewer_permissions(user):
        """Memberikan permission view saja untuk viewer"""
        permissions = Permission.objects.filter(
            content_type__app_label='posyandu',
            codename__startswith='view_'
        )
        user.user_permissions.set(permissions)
        return permissions.count()


# Decorator untuk permission check
from functools import wraps
from django.core.exceptions import PermissionDenied

def require_posyandu_permission(permission_codename):
    """Decorator untuk mengecek permission posyandu"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(f'posyandu.{permission_codename}'):
                raise PermissionDenied("Anda tidak memiliki permission untuk mengakses halaman ini")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Permission mixins untuk class-based views
from django.contrib.auth.mixins import PermissionRequiredMixin

class PosyanduPermissionMixin(PermissionRequiredMixin):
    """Mixin untuk permission posyandu"""
    permission_required = None
    raise_exception = True
    
    def get_permission_required(self):
        """Mendapatkan permission yang diperlukan"""
        if self.permission_required:
            return [f'posyandu.{perm}' for perm in self.permission_required]
        return []

# Template tags untuk permission check
from django import template

register = template.Library()

@register.filter
def has_posyandu_permission(user, permission):
    """Template filter untuk mengecek permission posyandu"""
    return user.has_perm(f'posyandu.{permission}')

@register.filter
def can_view_posyandu(user):
    """Template filter untuk mengecek apakah user bisa view posyandu"""
    return user.has_perm('posyandu.view_posyandulocation')

@register.filter
def can_manage_posyandu(user):
    """Template filter untuk mengecek apakah user bisa manage posyandu"""
    return user.has_perm('posyandu.add_posyandulocation')

@register.filter
def can_delete_posyandu(user):
    """Template filter untuk mengecek apakah user bisa delete posyandu"""
    return user.has_perm('posyandu.delete_posyandulocation')

