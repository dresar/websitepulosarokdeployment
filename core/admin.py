from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, WebsiteSettings, Role, MenuPermission, UserRole)

# Minimal admin configuration - focus on custom admin panel
# Django admin is kept for emergency access only

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Minimal user admin - emergency access only"""
    list_display = ('username', 'email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')

@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    """Minimal settings admin - emergency access only"""
    list_display = ['site_name', 'maintenance_mode', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Minimal role admin - emergency access only"""
    list_display = ('display_name', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'display_name')

@admin.register(MenuPermission)
class MenuPermissionAdmin(admin.ModelAdmin):
    """Minimal permission admin - emergency access only"""
    list_display = ('name', 'module', 'action', 'is_active')
    list_filter = ('module', 'is_active')
    search_fields = ('name', 'codename')

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Minimal user role admin - emergency access only"""
    list_display = ('user', 'role', 'is_active')
    list_filter = ('is_active', 'role')
    search_fields = ('user__username', 'role__display_name')

# Note: All other models are managed through custom admin panel
# Django admin is kept minimal for emergency access only