from django.urls import path, include
from . import views, api_views

app_name = 'tourism'

urlpatterns = [
    # CSRF API endpoint
    path('api/csrf/', views.get_csrf_token, name='csrf_token'),
    
    # Public views
    path('', views.tourism_dashboard, name='dashboard'),
    path('locations/', views.tourism_list, name='location_list'),
    path('location/<slug:slug>/', views.tourism_detail, name='location_detail'),
    path('<int:location_id>/', views.tourism_detail_by_id, name='location_detail_by_id'),  # Redirect from ID to slug
    path('debug/', views.debug_tourism, name='debug_tourism'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('category/<slug:slug>/', views.category_detail_by_slug, name='category_detail_by_slug'),
    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<slug:slug>/', views.event_detail_by_slug, name='event_detail_by_slug'),
    path('packages/', views.package_list, name='package_list'),
    path('package/<int:package_id>/', views.package_detail, name='package_detail'),
    path('package/<slug:slug>/', views.package_detail_by_slug, name='package_detail_by_slug'),
    path('search/', views.search_tourism, name='search'),
    
    # User actions (require login)
    path('review/<int:location_id>/', views.submit_review, name='submit_review'),
    path('add-review/<slug:slug>/', views.add_review, name='add_review'),
    path('rating/<int:location_id>/', views.submit_rating, name='submit_rating'),
    
    # Admin views (require login)
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/locations/', views.admin_location_list, name='admin_location_list'),
    path('admin/location/create/', views.admin_location_create, name='admin_location_create'),
    path('admin/location/<int:location_id>/', views.admin_location_detail, name='admin_location_detail'),
    path('admin/location/<int:location_id>/edit/', views.admin_location_edit, name='admin_location_edit'),
    path('admin/location/<int:location_id>/delete/', views.admin_location_delete, name='admin_location_delete'),
    
    # Admin Category views
    path('admin/categories/', views.admin_category_list, name='admin_category_list'),
    path('admin/category/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/category/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/category/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # Admin Package views
    path('admin/packages/', views.admin_package_list, name='admin_package_list'),
    path('admin/package/create/', views.admin_package_create, name='admin_package_create'),
    path('admin/package/<int:package_id>/', views.admin_package_detail, name='admin_package_detail'),
    path('admin/package/<int:package_id>/edit/', views.admin_package_edit, name='admin_package_edit'),
    path('admin/package/<int:package_id>/delete/', views.admin_package_delete, name='admin_package_delete'),
    
    # Admin Event views now handled by AJAX modals
    
    # API endpoints for penduduk
    path('api/penduduk/search/', api_views.api_penduduk_search, name='api_penduduk_search'),
    path('api/penduduk/<int:penduduk_id>/', api_views.api_penduduk_detail, name='api_penduduk_detail'),
    path('api/penduduk/self/', api_views.api_penduduk_self, name='api_penduduk_self'),
    path('api/penduduk/list/', api_views.api_penduduk_list, name='api_penduduk_list'),
]
