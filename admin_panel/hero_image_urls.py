"""
URL patterns for Hero Image Management - Simplified
"""

from django.urls import path
from . import hero_image_views

app_name = 'hero_images'

urlpatterns = [
    # Dashboard
    path('dashboard/', hero_image_views.hero_images_dashboard, name='hero_images_dashboard'),
    
    # Hero Images CRUD
    path('', hero_image_views.hero_images_list, name='hero_images_list'),
    path('create/', hero_image_views.hero_image_create, name='hero_image_create'),
    path('<int:pk>/edit/', hero_image_views.hero_image_edit, name='hero_image_edit'),
    path('<int:pk>/delete/', hero_image_views.hero_image_delete, name='hero_image_delete'),
    
    # API endpoints
    path('api/check-page/', hero_image_views.check_page_exists, name='check_page_exists'),
]