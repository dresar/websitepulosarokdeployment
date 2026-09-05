from django.urls import path, include
from . import views

app_name = 'business'

urlpatterns = [
    # Public URLs - Halaman Utama
    path('', views.business_list, name='business_list'),
    path('detail/<int:business_id>/', views.business_detail, name='business_detail'),
    path('daftar/', views.business_register, name='business_register'),
    
    # Public URLs - Jenis Bisnis Spesifik
    path('umkm/', views.umkm_list_public, name='umkm_list'),
    path('umkm/detail/<int:umkm_id>/', views.umkm_detail_public, name='umkm_detail'),
    path('koperasi/', views.koperasi_list_public, name='koperasi_list'),
    path('koperasi/detail/<int:koperasi_id>/', views.koperasi_detail_public, name='koperasi_detail'),
    path('bumg/', views.bumg_list_public, name='bumg_list'),
    path('bumg/detail/<int:bumg_id>/', views.bumg_detail_public, name='bumg_detail'),
    path('toko-warung/', views.toko_warung_list, name='toko_warung_list'),
    path('layanan-jasa/', views.layanan_jasa_list, name='layanan_jasa_list'),
    path('layanan-jasa/detail/<int:layanan_id>/', views.layanan_jasa_detail_public, name='layanan_jasa_detail'),
    
    # API URLs for AJAX
    path('api/csrf/', views.get_csrf_token, name='csrf_token'),
    path('api/register/', views.api_business_register, name='api_business_register'),
    path('api/list/', views.api_business_list, name='api_business_list'),
    path('api/detail/<int:business_id>/', views.api_business_detail, name='api_business_detail'),
    path('api/categories/', views.api_business_categories, name='api_business_categories'),
    path('api/statistics/', views.api_business_statistics, name='api_business_statistics'),
    path('api/stats/', views.api_business_statistics, name='api_business_stats'),
    path('api/types/', views.api_business_categories, name='api_business_types'),
    
    # API URLs for search functionality
    path('api/penduduk-search/', views.api_penduduk_search, name='api_penduduk_search'),
    path('api/business-search/', views.api_business_search, name='api_business_search'),
    
    # Admin Panel URLs
    path('admin/', include('business.admin_urls')),
    
    # API URLs for Admin
    path('api/', include('business.api_urls')),
]
