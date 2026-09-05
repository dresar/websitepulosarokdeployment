from django.urls import path
from . import views
from . import views_import_export

app_name = 'references'

urlpatterns = [
    # Main population page
    path('population/', views.population_page, name='population'),
    path('population/stats/', views.population_page, name='population_stats'),  # Alias for home menu compatibility
    
    # Public statistics APIs for homepage and public pages (no duplicates with admin_panel)
    path('api/public/statistics/', views.api_public_statistics, name='api_public_statistics'),
    path('api/public/dashboard/', views.api_dashboard_statistics, name='api_dashboard_statistics'),
    path('api/public/news/', views.api_public_news, name='api_public_news'),
    path('api/public/business/', views.api_public_business, name='api_public_business'),
    path('api/public/tourism/', views.api_public_tourism, name='api_public_tourism'),
    
    # Public Population APIs - no authentication required
    path('api/public/population/overview/', views.api_public_population_overview, name='api_public_population_overview'),
    path('api/public/population/demographics/', views.api_public_population_demographics, name='api_public_population_demographics'),
    
    # API Documentation
    path('api/documentation/', views.api_documentation, name='api_documentation'),
    
    # API for penduduk by dusun - removed (function not found)
    # path('api/penduduk-by-dusun/<int:dusun_id>/', views.api_penduduk_by_dusun, name='api_penduduk_by_dusun'),
    # path('api/penduduk/', views.api_penduduk_list, name='api_penduduk_list'),
    
    # RW URLs - removed (functions not found)
    # path('rw/', views.rw_list, name='rw_list'),
    # path('rw/create/', views.rw_create, name='rw_create'),
    # path('rw/<int:rw_id>/edit/', views.rw_edit, name='rw_edit'),
    # path('rw/<int:rw_id>/delete/', views.rw_delete, name='rw_delete'),
    # API URLs - removed (functions not found)
    # path('api/rw-by-dusun/<int:dusun_id>/', views.api_rw_by_dusun, name='api_rw_by_dusun'),
    # path('api/penduduk-by-rw/<int:rw_id>/', views.api_penduduk_by_rw, name='api_penduduk_by_rw'),
    
    # RT URLs - removed (functions not found)
    # path('rt/', views.rt_list, name='rt_list'),
    # path('rt/create/', views.rt_create, name='rt_create'),
    # path('rt/<int:rt_id>/edit/', views.rt_edit, name='rt_edit'),
    # path('rt/<int:rt_id>/delete/', views.rt_delete, name='rt_delete'),
    # path('api/rt-by-rw/<int:rw_id>/', views.api_rt_by_rw, name='api_rt_by_rw'),
    
    # Individual export URLs removed - use comprehensive system below
    
    # Individual import/export URLs removed - use comprehensive system below
    
    # Import/Export Dashboard
    path('import-export/', views_import_export.import_export_dashboard, name='import_export_dashboard'),
    path('export/<str:model_name>/', views_import_export.export_data, name='export_data'),
    path('import/<str:model_name>/', views_import_export.import_data, name='import_data'),
    path('download-template/<str:model_name>/<str:format_type>/', views_import_export.download_template, name='download_template'),
    path('bulk-export/', views_import_export.bulk_export, name='bulk_export'),
    path('export-statistics/', views_import_export.export_statistics, name='export_statistics'),
    
    # Enhanced Import/Export APIs
    path('api/quick-export/<str:model_name>/', views_import_export.quick_export, name='quick_export'),
    path('api/quick-import/<str:model_name>/', views_import_export.quick_import, name='quick_import'),
    path('api/template/<str:model_name>/', views_import_export.get_import_template, name='get_import_template'),
    path('api/import-preview/<str:model_name>/', views_import_export.api_import_preview, name='api_import_preview'),
    path('api/bulk-export-selected/', views_import_export.bulk_export_selected, name='bulk_export_selected'),
    path('api/validate-import/', views_import_export.validate_import_file, name='validate_import_file'),
    path('api/bulk-action/', views_import_export.bulk_action, name='bulk_action'),
    
]