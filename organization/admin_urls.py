from django.urls import path
from . import admin_views as views
from . import admin_api as api

app_name = 'organization'

urlpatterns = [
    # Main admin organization pages
    path('', views.admin_organization_list, name='organization_list'),
    path('hierarchy/', views.admin_organization_hierarchy, name='organization_hierarchy'),
    
    # Perangkat Desa URLs (Admin Panel)
    path('perangkat-desa/', views.admin_perangkat_desa_list, name='admin_perangkat_desa_list'),
    path('perangkat-desa/create/', views.perangkat_desa_create, name='admin_perangkat_desa_create'),
    path('perangkat-desa/<int:pk>/detail/', views.perangkat_desa_detail, name='admin_perangkat_desa_detail'),
    path('perangkat-desa/<int:pk>/edit/', views.perangkat_desa_edit, name='admin_perangkat_desa_edit'),
    path('perangkat-desa/<int:pk>/delete/', views.perangkat_desa_delete, name='admin_perangkat_desa_delete'),
    
    # Lembaga Adat URLs (Admin Panel)
    path('lembaga-adat/', views.admin_lembaga_adat_list, name='admin_lembaga_adat_list'),
    path('lembaga-adat/create/', views.lembaga_adat_create, name='admin_lembaga_adat_create'),
    path('lembaga-adat/<int:pk>/detail/', views.lembaga_adat_detail, name='admin_lembaga_adat_detail'),
    path('lembaga-adat/<int:pk>/edit/', views.lembaga_adat_edit, name='admin_lembaga_adat_edit'),
    path('lembaga-adat/<int:pk>/delete/', views.lembaga_adat_delete, name='admin_lembaga_adat_delete'),
    
    # PKK URLs (Admin Panel)
    path('pkk/', views.admin_pkk_list, name='admin_pkk_list'),
    path('pkk/create/', views.pkk_create, name='admin_pkk_create'),
    path('pkk/<int:pk>/detail/', views.pkk_detail, name='admin_pkk_detail'),
    path('pkk/<int:pk>/edit/', views.pkk_edit, name='admin_pkk_edit'),
    path('pkk/<int:pk>/delete/', views.pkk_delete, name='admin_pkk_delete'),
    
    # Kepemudaan URLs (Admin Panel)
    path('kepemudaan/', views.admin_kepemudaan_list, name='admin_kepemudaan_list'),
    path('kepemudaan/create/', views.kepemudaan_create, name='admin_kepemudaan_create'),
    path('kepemudaan/<int:pk>/detail/', views.kepemudaan_detail, name='admin_kepemudaan_detail'),
    path('kepemudaan/<int:pk>/edit/', views.kepemudaan_edit, name='admin_kepemudaan_edit'),
    path('kepemudaan/<int:pk>/delete/', views.kepemudaan_delete, name='admin_kepemudaan_delete'),
    
    # Karang Taruna URLs (Admin Panel)
    path('karang-taruna/', views.admin_karang_taruna_list, name='admin_karang_taruna_list'),
    path('karang-taruna/create/', views.karang_taruna_create, name='admin_karang_taruna_create'),
    path('karang-taruna/<int:pk>/detail/', views.karang_taruna_detail, name='admin_karang_taruna_detail'),
    path('karang-taruna/<int:pk>/edit/', views.karang_taruna_edit, name='admin_karang_taruna_edit'),
    path('karang-taruna/<int:pk>/delete/', views.karang_taruna_delete, name='admin_karang_taruna_delete'),
    
    # Admin API URLs
    path('api/stats/', api.admin_api_organization_stats, name='api_organization_stats'),
    path('api/village-officials/', api.admin_api_village_officials, name='api_village_officials'),
    path('api/lembaga-adat/', api.admin_api_lembaga_adat, name='api_lembaga_adat'),
    path('api/penggerak-pkk/', api.admin_api_penggerak_pkk, name='api_penggerak_pkk'),
    path('api/kepemudaan/', api.admin_api_kepemudaan, name='api_kepemudaan'),
    path('api/karang-taruna/', api.admin_api_karang_taruna, name='api_karang_taruna'),
    path('api/structure/', api.admin_api_organization_structure, name='api_organization_structure'),
    path('api/search-penduduk/', api.admin_api_search_penduduk, name='api_search_penduduk'),
    
    # Test Form URL
    path('test-search/', views.test_penduduk_search, name='test_penduduk_search'),
    
    # Admin API Detail URLs
    path('api/perangkat-desa/<int:pk>/', views.api_perangkat_desa_detail, name='api_perangkat_desa_detail'),
    path('api/lembaga-adat/<int:pk>/', views.api_lembaga_adat_detail, name='api_lembaga_adat_detail'),
    path('api/pkk/<int:pk>/', views.api_pkk_detail, name='api_pkk_detail'),
    path('api/kepemudaan/<int:pk>/', views.api_kepemudaan_detail, name='api_kepemudaan_detail'),
    path('api/karang-taruna/<int:pk>/', views.api_karang_taruna_detail, name='api_karang_taruna_detail'),
]
