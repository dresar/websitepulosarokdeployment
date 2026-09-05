from django.urls import path
from . import views, api_views

# API URLs for village profile
urlpatterns = [
    # Public API endpoints (no authentication required)
    path('public/profile/', api_views.api_village_profile, name='public_profile'),
    path('public/history/', api_views.api_village_history, name='public_history'),
    path('public/geography/', api_views.api_village_geography, name='public_geography'),
    path('public/demography/', api_views.api_village_demography, name='public_demography'),
    path('public/officials/', api_views.api_village_officials, name='public_officials'),
    path('public/facilities/', api_views.api_village_facilities, name='public_facilities'),
    path('public/gallery/', api_views.api_village_gallery, name='public_gallery'),
    path('public/complete/', api_views.api_village_complete, name='public_complete'),
    
    # Legacy API endpoints (kept for compatibility)
    path('profile/', views.ajax_profile_data, name='api_profile_data'),
    path('geography/', views.ajax_geography_data, name='api_geography_data'),
    path('demography/', views.ajax_demography_data, name='api_demography_data'),
    path('facilities/', views.ajax_facilities_data, name='api_facilities_data'),
    path('officials/', views.ajax_officials_data, name='api_officials_data'),
    path('history/', views.ajax_history_data, name='api_history_data'),
    path('gallery/', views.ajax_gallery_data, name='api_gallery_data'),
]