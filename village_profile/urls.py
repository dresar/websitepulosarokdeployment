from django.urls import path, include
from django.views.generic import TemplateView
from . import views, admin_views, gallery_views

app_name = 'village_profile'

urlpatterns = [
    # Dashboard utama
    path('', views.dashboard_view, name='profile'),
    
    # View terpisah untuk setiap komponen
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('history/', views.history_view, name='history'),
    path('history/<int:history_id>/', views.history_detail_view, name='history_detail'),
    path('vision-mission/', views.vision_mission_view, name='vision_mission'),
    path('geography/', views.geography_view, name='geography'),
    path('officials/', views.officials_view, name='officials'),
    path('facilities/', views.facilities_view, name='facilities'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('demography/', views.demography_view, name='demography'),
    
    # Admin CRUD operations
    path('admin/dashboard/', admin_views.village_profile_dashboard, name='admin_dashboard'),
    path('admin/general-info/', admin_views.village_profile_general_info, name='admin_general_info'),
    path('admin/geography/', admin_views.village_profile_general_info, name='admin_geography'),
    path('admin/demography/', admin_views.village_profile_general_info, name='admin_demography'),
    path('admin/officials/', admin_views.village_profile_officials, name='admin_officials'),
    path('admin/officials/add/', admin_views.village_official_form, name='admin_official_add'),
    path('admin/officials/edit/<int:official_id>/', admin_views.village_official_form, name='admin_official_edit'),
    path('admin/facilities/', admin_views.village_profile_facilities, name='admin_facilities'),
    path('admin/history/', admin_views.village_profile_history, name='admin_history'),
    path('admin/history/<int:history_id>/', admin_views.history_detail_view, name='admin_history_detail'),
    path('admin/gallery/', admin_views.village_profile_gallery, name='admin_gallery'),
    
    # Admin save operations
    path('admin/save-profile/', admin_views.save_village_profile, name='admin_save_profile'),
    path('admin/save-geography/', admin_views.save_village_geography, name='admin_save_geography'),
    path('admin/save-demography/', admin_views.save_village_demography, name='admin_save_demography'),
    path('admin/save-official/', admin_views.save_village_official, name='admin_save_official'),
    path('admin/save-facility/', admin_views.save_village_facility, name='admin_save_facility'),
    path('admin/save-history/', admin_views.save_village_history, name='admin_save_history'),
    path('admin/save-photo/', admin_views.save_village_photo, name='admin_save_photo'),
    
    # Admin delete operations
    path('admin/delete-official/', admin_views.delete_village_official, name='admin_delete_official'),
    path('admin/delete-facility/', admin_views.delete_village_facility, name='admin_delete_facility'),
    path('admin/delete-history/', admin_views.delete_village_history, name='admin_delete_history'),
    path('admin/delete-photo/', admin_views.delete_village_photo, name='admin_delete_photo'),
    
    # Admin toggle status operations
    path('admin/toggle-official/', admin_views.toggle_official_status, name='admin_toggle_official'),
    path('admin/toggle-facility/', admin_views.toggle_facility_status, name='admin_toggle_facility'),
    path('admin/toggle-history/', admin_views.toggle_history_status, name='admin_toggle_history'),
    path('admin/toggle-photo/', admin_views.toggle_photo_status, name='admin_toggle_photo'),
    
    # Admin display order operations
    path('admin/update-officials-order/', admin_views.update_officials_order, name='admin_update_officials_order'),
    path('admin/update-photos-order/', admin_views.update_photos_order, name='admin_update_photos_order'),
    
    # Admin bulk operations
    path('admin/bulk-delete-officials/', admin_views.bulk_delete_officials, name='admin_bulk_delete_officials'),
    path('admin/bulk-delete-facilities/', admin_views.bulk_delete_facilities, name='admin_bulk_delete_facilities'),
    path('admin/bulk-toggle-officials/', admin_views.bulk_toggle_officials_status, name='admin_bulk_toggle_officials'),
    
    # Admin API endpoints
    path('admin/api/profile/', admin_views.api_village_profile_data, name='admin_api_profile'),
    path('admin/api/officials/', admin_views.api_village_officials, name='admin_api_officials'),
    path('admin/api/officials/get/', admin_views.api_get_official, name='admin_api_get_official'),
    path('admin/api/facilities/get/', admin_views.api_get_facility, name='admin_api_get_facility'),
    path('admin/api/history/get/', admin_views.api_get_history, name='admin_api_get_history'),
    path('admin/api/photos/get/', admin_views.api_get_photo, name='admin_api_get_photo'),
    path('admin/api/statistics/', admin_views.api_village_statistics, name='admin_api_statistics'),
    path('admin/api/search-penduduk/', admin_views.api_search_penduduk, name='admin_api_search_penduduk'),
    path('admin/api/penduduk/<int:penduduk_id>/', admin_views.api_get_penduduk_detail, name='api_get_penduduk_detail'),
    
    # Gallery API endpoints
    path('admin/api/gallery/', gallery_views.gallery_api, name='gallery_api'),
    
    # Export operations
    path('admin/export/', admin_views.export_village_data, name='admin_export_data'),
    path('admin/export/officials/', admin_views.export_officials, name='admin_export_officials'),
    path('admin/export/facilities/', admin_views.export_facilities, name='admin_export_facilities'),
    path('admin/export/history/', admin_views.export_history, name='admin_export_history'),
    
    # API endpoints
    path('api/', include('village_profile.api_urls')),
    
    # AJAX endpoints
    path('ajax/profile/', views.ajax_profile_data, name='ajax_profile_data'),
    path('ajax/geography/', views.ajax_geography_data, name='ajax_geography_data'),
    path('ajax/demography/', views.ajax_demography_data, name='ajax_demography_data'),
    path('ajax/facilities/', views.ajax_facilities_data, name='ajax_facilities_data'),
    path('ajax/officials/', views.ajax_officials_data, name='ajax_officials_data'),
    path('ajax/history/', views.ajax_history_data, name='ajax_history_data'),
    path('ajax/gallery/', views.ajax_gallery_data, name='ajax_gallery_data'),
    
    # Additional AJAX endpoints for admin
    path('ajax/officials-data/', admin_views.api_village_officials, name='ajax_officials_data_admin'),
    path('ajax/facilities-data/', admin_views.api_village_facilities, name='ajax_facilities_data_admin'),
    path('ajax/history-data/', admin_views.api_village_history, name='ajax_history_data_admin'),
    path('ajax/gallery-data/', admin_views.api_village_gallery, name='ajax_gallery_data_admin'),
]