from django import template
from django.contrib.auth.models import AnonymousUser

register = template.Library()


@register.filter
def has_menu_permission(user, permission_string):
    """
    Check if user has specific menu permission
    Usage: {% if user|has_menu_permission:"beneficiaries.view" %}
    """
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False
        
    if user.is_superuser:
        return True
        
    try:
        module, action = permission_string.split('.')
        return user.has_menu_permission(module, action)
    except (ValueError, AttributeError):
        return False


@register.filter
def has_role(user, role_name):
    """
    Check if user has specific role
    Usage: {% if user|has_role:"admin" %}
    """
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False
        
    if user.is_superuser:
        return True
        
    return user.has_role(role_name)


@register.filter
def has_any_role(user, role_names):
    """
    Check if user has any of the specified roles
    Usage: {% if user|has_any_role:"admin,moderator" %}
    """
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False
        
    if user.is_superuser:
        return True
        
    roles = [role.strip() for role in role_names.split(',')]
    return any(user.has_role(role) for role in roles)


@register.filter
def can_view(user, module):
    """
    Check if user can view specific module
    Usage: {% if user|can_view:"beneficiaries" %}
    """
    return has_menu_permission(user, f"{module}.view")


@register.filter
def can_add(user, module):
    """
    Check if user can add to specific module
    Usage: {% if user|can_add:"beneficiaries" %}
    """
    return has_menu_permission(user, f"{module}.add")


@register.filter
def can_change(user, module):
    """
    Check if user can change specific module
    Usage: {% if user|can_change:"beneficiaries" %}
    """
    return has_menu_permission(user, f"{module}.change")


@register.filter
def can_delete(user, module):
    """
    Check if user can delete from specific module
    Usage: {% if user|can_delete:"beneficiaries" %}
    """
    return has_menu_permission(user, f"{module}.delete")


@register.filter
def can_export(user, module):
    """
    Check if user can export from specific module
    Usage: {% if user|can_export:"beneficiaries" %}
    """
    return has_menu_permission(user, f"{module}.export")


@register.filter
def can_import(user, module):
    """
    Check if user can import to specific module
    Usage: {% if user|can_import:"beneficiaries" %}
    """
    return has_menu_permission(user, f"{module}.import")


@register.simple_tag
def get_user_roles(user):
    """
    Get all active roles for user
    Usage: {% get_user_roles user as roles %}
    """
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return []
        
    return user.get_active_roles()


@register.simple_tag
def get_user_permissions(user):
    """
    Get all menu permissions for user
    Usage: {% get_user_permissions user as permissions %}
    """
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return []
        
    return user.get_menu_permissions()

