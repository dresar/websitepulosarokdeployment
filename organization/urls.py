from django.urls import path
from . import views

app_name = 'organization'

urlpatterns = [
    # Main organization page
    path('', views.organization_list, name='organization_list'),
    path('hierarchy/', views.organization_hierarchy, name='organization_hierarchy'),
    
    # Perangkat Desa URLs (Public)
    path('perangkat-desa/', views.perangkat_desa_list, name='perangkat_desa_list'),
    path('perangkat-desa/<int:pk>/', views.perangkat_desa_detail, name='perangkat_desa_detail'),
    
    # Lembaga Adat URLs (Public)
    path('lembaga-adat/', views.lembaga_adat_list, name='lembaga_adat_list'),
    path('lembaga-adat/<int:pk>/', views.lembaga_adat_detail, name='lembaga_adat_detail'),
    
    # PKK URLs (Public)
    path('pkk/', views.pkk_list, name='pkk_list'),
    path('pkk/<int:pk>/', views.pkk_detail, name='pkk_detail'),
    
    # Kepemudaan URLs (Public)
    path('kepemudaan/', views.kepemudaan_list, name='kepemudaan_list'),
    path('kepemudaan/<int:pk>/', views.kepemudaan_detail, name='kepemudaan_detail'),
    
    # Karang Taruna URLs (Public)
    path('karang-taruna/', views.karang_taruna_list, name='karang_taruna_list'),
    path('karang-taruna/<int:pk>/', views.karang_taruna_detail, name='karang_taruna_detail'),
    
    # API URLs
    path('api/organizations/', views.api_organizations, name='api_organizations'),
    path('api/statistics/', views.api_statistics, name='api_statistics'),
    path('api/stats/', views.api_organization_stats, name='api_organization_stats'),
    path('api/village-officials/', views.api_village_officials, name='api_village_officials'),
    path('api/lembaga-adat/', views.api_lembaga_adat, name='api_lembaga_adat'),
    path('api/penggerak-pkk/', views.api_penggerak_pkk, name='api_penggerak_pkk'),
    path('api/kepemudaan/', views.api_kepemudaan, name='api_kepemudaan'),
    path('api/karang-taruna/', views.api_karang_taruna, name='api_karang_taruna'),
    path('api/structure/', views.api_organization_structure, name='api_organization_structure'),
    path('api/search-penduduk/', views.api_search_penduduk, name='api_search_penduduk'),
    
    # API Detail URLs
    path('api/perangkat-desa/<int:pk>/', views.api_perangkat_desa_detail, name='api_perangkat_desa_detail'),
    path('api/lembaga-adat/<int:pk>/', views.api_lembaga_adat_detail, name='api_lembaga_adat_detail'),
    path('api/pkk/<int:pk>/', views.api_pkk_detail, name='api_pkk_detail'),
    path('api/kepemudaan/<int:pk>/', views.api_kepemudaan_detail, name='api_kepemudaan_detail'),
    path('api/karang-taruna/<int:pk>/', views.api_karang_taruna_detail, name='api_karang_taruna_detail'),
    
    # AJAX endpoints for filtering
    path('ajax/perangkat-desa/filter/', views.ajax_perangkat_desa_filter, name='ajax_perangkat_desa_filter'),
    path('ajax/lembaga-adat/filter/', views.ajax_lembaga_adat_filter, name='ajax_lembaga_adat_filter'),
    path('ajax/pkk/filter/', views.ajax_pkk_filter, name='ajax_pkk_filter'),
    path('ajax/kepemudaan/filter/', views.ajax_kepemudaan_filter, name='ajax_kepemudaan_filter'),
    path('ajax/karang-taruna/filter/', views.ajax_karang_taruna_filter, name='ajax_karang_taruna_filter'),
]