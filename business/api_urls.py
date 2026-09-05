from django.urls import path
from . import api_views

app_name = 'business_api'

urlpatterns = [
    # Statistics API
    path('statistics/', api_views.api_business_statistics, name='business_statistics'),
    
    # Penduduk Search API
    path('penduduk-search/', api_views.api_penduduk_search, name='penduduk_search'),
    path('penduduk-search-public/', api_views.api_penduduk_search_public, name='penduduk_search_public'),
    
    # UMKM API
    path('umkm/', api_views.api_umkm_list, name='umkm_list'),
    path('umkm/create/', api_views.api_umkm_create, name='umkm_create'),
    path('umkm/<int:umkm_id>/update/', api_views.api_umkm_update, name='umkm_update'),
    path('umkm/<int:umkm_id>/delete/', api_views.api_umkm_delete, name='umkm_delete'),
    
    # Koperasi API
    path('koperasi/', api_views.api_koperasi_list, name='koperasi_list'),
    
    # BUMG API
    path('bumg/', api_views.api_bumg_list, name='bumg_list'),
    
    # Layanan Jasa API
    path('layanan-jasa/', api_views.api_layanan_jasa_list, name='layanan_jasa_list'),
    
    # Business Categories API
    path('categories/', api_views.api_business_categories_list, name='business_categories_list'),
    
    # Recent Activities API
    path('recent-activities/', api_views.api_recent_activities, name='recent_activities'),
]
