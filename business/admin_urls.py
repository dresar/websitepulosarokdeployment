from django.urls import path
from . import admin_views

app_name = 'admin_panel'

urlpatterns = [
    # Business Dashboard
    path('dashboard/', admin_views.business_dashboard, name='business_dashboard'),
    
    # UMKM URLs
    path('umkm/', admin_views.admin_ukm_list, name='umkm_list'),
    path('umkm/create/', admin_views.umkm_create, name='umkm_create'),
    path('umkm/<int:umkm_id>/', admin_views.umkm_detail, name='umkm_detail'),
    path('umkm/<int:umkm_id>/edit/', admin_views.umkm_edit, name='umkm_edit'),
    path('umkm/<int:umkm_id>/delete/', admin_views.umkm_delete, name='umkm_delete'),
    
    # Koperasi URLs
    path('koperasi/', admin_views.koperasi_list, name='koperasi_list'),
    path('koperasi/create/', admin_views.koperasi_create, name='koperasi_create'),
    path('koperasi/<int:koperasi_id>/', admin_views.koperasi_detail, name='koperasi_detail'),
    path('koperasi/<int:koperasi_id>/edit/', admin_views.koperasi_edit, name='koperasi_edit'),
    path('koperasi/<int:koperasi_id>/delete/', admin_views.koperasi_delete, name='koperasi_delete'),
    
    # BUMG URLs
    path('bumg/', admin_views.bumg_list, name='bumg_list'),
    path('bumg/create/', admin_views.bumg_create, name='bumg_create'),
    path('bumg/<int:bumg_id>/', admin_views.bumg_detail, name='bumg_detail'),
    path('bumg/<int:bumg_id>/edit/', admin_views.bumg_edit, name='bumg_edit'),
    path('bumg/<int:bumg_id>/delete/', admin_views.bumg_delete, name='bumg_delete'),
    
    # Layanan Jasa URLs
    path('layanan-jasa/', admin_views.admin_layanan_jasa_list, name='admin_layanan_jasa_list'),
    path('layanan-jasa/create/', admin_views.layanan_jasa_create, name='layanan_jasa_create'),
    path('layanan-jasa/<int:layanan_id>/', admin_views.layanan_jasa_detail, name='layanan_jasa_detail'),
    path('layanan-jasa/<int:layanan_id>/edit/', admin_views.layanan_jasa_edit, name='layanan_jasa_edit'),
    path('layanan-jasa/<int:layanan_id>/delete/', admin_views.layanan_jasa_delete, name='layanan_jasa_delete'),
    
    # Business Categories URLs
    path('categories/', admin_views.business_categories_list, name='business_categories_list'),
    path('categories/create/', admin_views.business_category_create, name='business_category_create'),
    path('categories/<int:category_id>/', admin_views.business_category_detail, name='business_category_detail'),
    path('categories/<int:category_id>/edit/', admin_views.business_category_edit, name='business_category_edit'),
    path('categories/<int:category_id>/delete/', admin_views.business_category_delete, name='business_category_delete'),
    
    # Business URLs
    path('business/', admin_views.business_list_admin, name='business_list'),
    path('business/create/', admin_views.business_create, name='business_create'),
    path('business/<int:business_id>/', admin_views.business_detail_admin, name='business_detail'),
    path('business/<int:business_id>/edit/', admin_views.business_edit, name='business_edit'),
    path('business/<int:business_id>/delete/', admin_views.business_delete, name='business_delete'),
]
