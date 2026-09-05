from django.urls import path
from . import views

app_name = 'posyandu'

urlpatterns = [
    # Admin URLs
    path('admin/', views.posyandu_admin, name='posyandu_admin'),
    path('unified-form/', views.unified_form, name='unified_form'),
    path('locations/', views.locations, name='locations'),
    path('locations/create/', views.location_create, name='location_create'),
    path('locations/<int:location_id>/', views.location_detail, name='locations_detail'),
    path('locations/<int:location_id>/edit/', views.location_update, name='location_update'),
    path('locations/<int:location_id>/delete/', views.location_delete, name='location_delete'),
    path('schedules/', views.schedules, name='schedules'),
    path('schedules/create/', views.schedule_create, name='schedule_create'),
    path('schedules/<int:schedule_id>/', views.schedule_detail, name='schedule_detail'),
    path('schedules/<int:schedule_id>/edit/', views.schedule_update, name='schedule_update'),
    path('schedules/<int:schedule_id>/delete/', views.schedule_delete, name='schedule_delete'),
    path('health-records/', views.health_records, name='health_records'),
    path('health-records/create/', views.health_record_create, name='health_record_create'),
    path('health-records/<int:record_id>/', views.health_record_detail, name='health_record_detail'),
    path('health-records/<int:record_id>/edit/', views.health_record_update, name='health_record_update'),
    path('health-records/<int:record_id>/delete/', views.health_record_delete, name='health_record_delete'),
    path('immunizations/', views.immunizations, name='immunizations'),
    path('immunizations/create/', views.immunization_create, name='immunization_create'),
    path('immunizations/<int:immunization_id>/', views.immunization_detail, name='immunization_detail'),
    path('immunizations/<int:immunization_id>/edit/', views.immunization_update, name='immunization_update'),
    path('immunizations/<int:immunization_id>/delete/', views.immunization_delete, name='immunization_delete'),
    path('nutrition-data/', views.nutrition_data, name='nutrition_data'),
    path('nutrition-data/create/', views.nutrition_data_create, name='nutrition_data_create'),
    path('nutrition-data/<int:nutrition_id>/', views.nutrition_data_detail, name='nutrition_data_detail'),
    path('nutrition-data/<int:nutrition_id>/edit/', views.nutrition_data_update, name='nutrition_data_update'),
    path('nutrition-data/<int:nutrition_id>/delete/', views.nutrition_data_delete, name='nutrition_data_delete'),
    path('kaders/', views.kaders, name='kaders'),
    path('kaders/create/', views.kader_create, name='kader_create'),
    path('kaders/<int:kader_id>/', views.kader_detail, name='kader_detail'),
    path('kaders/<int:kader_id>/edit/', views.kader_update, name='kader_update'),
    path('kaders/<int:kader_id>/delete/', views.kader_delete, name='kader_delete'),
    path('ibu-hamil/', views.ibu_hamil, name='ibu_hamil'),
    path('ibu-hamil/create/', views.ibu_hamil_create, name='ibu_hamil_create'),
    path('ibu-hamil/<int:ibu_hamil_id>/', views.ibu_hamil_detail, name='ibu_hamil_detail'),
    path('ibu-hamil/<int:ibu_hamil_id>/edit/', views.ibu_hamil_update, name='ibu_hamil_update'),
    path('ibu-hamil/<int:ibu_hamil_id>/delete/', views.ibu_hamil_delete, name='ibu_hamil_delete'),
    path('stunting-data/', views.stunting_data, name='stunting_data'),
    path('stunting-data/create/', views.stunting_data_create, name='stunting_data_create'),
    path('stunting-data/<int:stunting_id>/', views.stunting_data_detail, name='stunting_data_detail'),
    path('stunting-data/<int:stunting_id>/edit/', views.stunting_data_update, name='stunting_data_update'),
    path('stunting-data/<int:stunting_id>/delete/', views.stunting_data_delete, name='stunting_data_delete'),
    path('patient-types/', views.patient_types, name='patient_types'),
    path('patient-types/create/', views.patient_type_create, name='patient_type_create'),
    path('patient-types/<int:patient_type_id>/', views.patient_type_detail, name='patient_type_detail'),
    path('patient-types/<int:patient_type_id>/edit/', views.patient_type_update, name='patient_type_update'),
    path('patient-types/<int:patient_type_id>/delete/', views.patient_type_delete, name='patient_type_delete'),
    path('reports/', views.reports, name='reports'),
    
    # Export URLs
    path('export/health-records/', views.export_health_records, name='export_health_records'),
    path('export/immunizations/', views.export_immunizations, name='export_immunizations'),
    path('export/nutrition-data/', views.export_nutrition_data, name='export_nutrition_data'),
    path('export/stunting-data/', views.export_stunting_data, name='export_stunting_data'),
    
    # Public URLs
    path('', views.public_posyandu_home, name='public_posyandu_home'),
    path('services/', views.public_posyandu_services, name='public_posyandu_services'),
    path('schedule/', views.public_posyandu_schedule, name='public_posyandu_schedule'),
    path('schedule/<int:location_id>/', views.public_posyandu_schedule, name='public_posyandu_schedule_location'),
    path('health-info/', views.public_health_info, name='public_health_info'),
    path('health-info/<str:nik>/', views.public_health_info, name='public_health_info_nik'),
    path('stunting-info/', views.public_stunting_info, name='public_stunting_info'),
    
    # Admin API URLs
    path('api/statistics/', views.api_statistics, name='api_statistics'),
    path('api/location-list/', views.api_location_list, name='api_location_list'),
    path('api/penduduk-search/', views.api_penduduk_search, name='api_penduduk_search'),
    path('api/location-create/', views.api_location_create, name='api_location_create'),
    path('api/location-update/<int:location_id>/', views.api_location_update, name='api_location_update'),
    path('api/location-delete/<int:location_id>/', views.api_location_delete, name='api_location_delete'),
    path('api/health-record-list/', views.api_health_record_list, name='api_health_record_list'),
    path('api/health-record-create/', views.api_health_record_create, name='api_health_record_create'),
    path('api/health-record-update/<int:record_id>/', views.api_health_record_update, name='api_health_record_update'),
    path('api/health-record-delete/<int:record_id>/', views.api_health_record_delete, name='api_health_record_delete'),
    path('api/health-record-cleanup/', views.api_health_record_cleanup, name='api_health_record_cleanup'),
    
    # Schedule API URLs
    path('api/schedule-list/', views.api_schedule_list, name='api_schedule_list'),
    path('api/schedule-create/', views.api_schedule_create, name='api_schedule_create'),
    path('api/schedule-detail/<int:schedule_id>/', views.api_schedule_detail, name='api_schedule_detail'),
    path('api/schedule-update/<int:schedule_id>/', views.api_schedule_update, name='api_schedule_update'),
    path('api/schedule-delete/<int:schedule_id>/', views.api_schedule_delete, name='api_schedule_delete'),
    
    # Ibu Hamil API URLs
    path('api/ibu-hamil-list/', views.api_ibu_hamil_list, name='api_ibu_hamil_list'),
    path('api/ibu-hamil-create/', views.api_ibu_hamil_create, name='api_ibu_hamil_create'),
    path('api/ibu-hamil-update/<int:ibu_hamil_id>/', views.api_ibu_hamil_update, name='api_ibu_hamil_update'),
    path('api/ibu-hamil-delete/<int:ibu_hamil_id>/', views.api_ibu_hamil_delete, name='api_ibu_hamil_delete'),
    
    # Immunization API URLs
    path('api/immunization-list/', views.api_immunization_list, name='api_immunization_list'),
    path('api/immunization-create/', views.api_immunization_create, name='api_immunization_create'),
    path('api/immunization-update/<int:immunization_id>/', views.api_immunization_update, name='api_immunization_update'),
    path('api/immunization-delete/<int:immunization_id>/', views.api_immunization_delete, name='api_immunization_delete'),
    
    # Kader API URLs
    path('api/kader-list/', views.api_kader_list, name='api_kader_list'),
    path('api/kader-create/', views.api_kader_create, name='api_kader_create'),
    path('api/kader-update/<int:kader_id>/', views.api_kader_update, name='api_kader_update'),
    path('api/kader-delete/<int:kader_id>/', views.api_kader_delete, name='api_kader_delete'),
    path('api/penduduk-search/', views.api_penduduk_search, name='api_penduduk_search'),
    path('api/posyandu-locations/', views.api_posyandu_locations, name='api_posyandu_locations'),
    
    # Stunting Data API URLs
    path('api/stunting-data-list/', views.api_stunting_data_list, name='api_stunting_data_list'),
    path('api/stunting-data-create/', views.api_stunting_data_create, name='api_stunting_data_create'),
    path('api/stunting-data-update/<int:stunting_data_id>/', views.api_stunting_data_update, name='api_stunting_data_update'),
    path('api/stunting-data-delete/<int:stunting_data_id>/', views.api_stunting_data_delete, name='api_stunting_data_delete'),
    
    # Nutrition Data API URLs
    path('api/nutrition-data-list/', views.api_nutrition_data_list, name='api_nutrition_data_list'),
    path('api/nutrition-data-create/', views.api_nutrition_data_create, name='api_nutrition_data_create'),
    path('api/nutrition-data-update/<int:nutrition_data_id>/', views.api_nutrition_data_update, name='api_nutrition_data_update'),
    path('api/nutrition-data-delete/<int:nutrition_data_id>/', views.api_nutrition_data_delete, name='api_nutrition_data_delete'),
    
    # Patient Type API URLs
    path('api/patient-types/', views.api_patient_types, name='api_patient_types'),
    path('api/patient-type-create/', views.api_patient_type_create, name='api_patient_type_create'),
    
    # Immunization Age Filter API URLs
    path('api/immunization-age-filter/', views.api_immunization_age_filter, name='api_immunization_age_filter'),
    path('api/immunization-by-age/', views.api_immunization_by_age, name='api_immunization_by_age'),
    
    # Public API URLs
    path('api/locations/', views.public_posyandu_locations_api, name='public_posyandu_locations_api'),
    path('api/schedules/', views.public_posyandu_schedules_api, name='public_posyandu_schedules_api'),
    path('api/health-stats/', views.public_health_stats_api, name='public_health_stats_api'),
    path('api/residents/', views.public_residents_api, name='public_residents_api'),
    
    # Test API page - disabled
    # path('test-api/', views.test_posyandu_api, name='test_posyandu_api'),
]