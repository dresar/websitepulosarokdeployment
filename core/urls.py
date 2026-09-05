from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
    path('custom-login-redirect/', views.custom_login_redirect, name='custom_login_redirect'),
    # Public URLs
    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),  # Redirect to village_profile
    
    # Public API URLs
    path('api/settings/', views.public_website_settings, name='public_website_settings'),
    path('population/', views.population_view, name='population'),
    path('events/', views.events_view, name='events'),
    # News routes moved to news app - handled by news.urls
    path('umkm/', views.umkm_view, name='umkm'),
    path('correspondence/', views.correspondence_view, name='correspondence'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('complaints/', views.complaints_view, name='complaints'),
    path('bantuna/', views.bantuna_view, name='bantuna'),
    path('offline/', views.offline_view, name='offline'),
    
    # Admin Panel URLs - Moved to admin_panel app
    
    # Settings URLs - Simplified
    path('admin-panel/settings/', views.website_settings, name='settings'),
    path('admin-panel/settings/media/', views.media_settings, name='media_settings'),
    path('admin-panel/settings/security/', views.security_settings, name='security_settings'),
    path('admin-panel/settings/email/', views.email_settings, name='email_settings'),
    path('admin-panel/settings/seo/', views.seo_settings, name='seo_settings'),
    path('admin-panel/settings/backup/', views.backup_settings, name='backup_settings'),
    path('admin-panel/settings/cache/', views.cache_settings, name='cache_settings'),
    path('admin-panel/settings/system/', views.system_info, name='system_info'),
    path('admin-panel/settings/users/', views.user_management_view, name='user_management'),
    
    # Website Settings URLs (alias for settings)
    path('admin-panel/website-settings/', views.website_settings, name='website_settings'),
    path('admin-panel/system-info/', views.system_info, name='system_info'),
    path('admin-panel/maintenance-mode/', views.maintenance_mode, name='maintenance_mode'),
    
    # Public API URLs
    path('api/settings/', views.public_settings_api, name='public_settings_api'),
    
    # API URLs - Website Settings
    path('admin-panel/api/website-settings/', views.api_website_settings, name='api_website_settings'),
    path('admin-panel/api/website-settings/update/', views.api_update_website_settings, name='api_update_website_settings'),
    
    path('admin-panel/api/users/add/', views.api_add_user, name='api_add_user'),
    path('admin-panel/api/users/update/', views.api_update_user, name='api_update_user'),
    path('admin-panel/api/users/delete/', views.api_delete_user, name='api_delete_user'),
    path('admin-panel/api/users/list/', views.api_list_users, name='api_list_users'),
    path('admin-panel/api/users/toggle-status/', views.api_toggle_user_status, name='api_toggle_user_status'),
    
    path('admin-panel/api/profile/update/', views.api_update_profile, name='api_update_profile'),
    path('admin-panel/api/profile/change-password/', views.api_change_password, name='api_change_password'),
    
    # Profile URLs for public access - moved to views.py
    path('profile/update/', views.api_update_profile, name='profile_update'),
    path('profile/change-password/', views.api_change_password, name='change_password'),
    
    
    # Export URLs
    path('admin-panel/export/users/csv/', views.export_users_csv, name='export_users_csv'),
    path('admin-panel/export/population/csv/', views.export_population_csv, name='export_population_csv'),
    
    # Admin dashboard
    path('admin-panel/admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    
    # Media Management URLs
    path('admin-panel/media/optimize/', views.optimize_images, name='optimize_images'),
    path('admin-panel/media/thumbnails/', views.generate_thumbnails, name='generate_thumbnails'),
    path('admin-panel/media/dashboard/', views.media_dashboard, name='media_dashboard'),
    
    # SEO Management URLs
    path('admin-panel/seo/sitemap/', views.generate_sitemap, name='generate_sitemap'),
    path('admin-panel/seo/audit/', views.seo_audit, name='seo_audit'),
    path('admin-panel/seo/analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('admin-panel/seo/reports/', views.seo_reports, name='seo_reports'),
    
    # Backup Management URLs
    path('admin-panel/backup/history/', views.backup_history, name='backup_history'),
    path('admin-panel/backup/dashboard/', views.backup_dashboard, name='backup_dashboard'),
    path('admin-panel/backup/download/<int:backup_id>/', views.download_backup, name='download_backup'),
    
    # Security Management URLs
    path('admin-panel/security/audit/', views.security_audit, name='security_audit'),
    path('admin-panel/security/blocked-ips/', views.blocked_ips, name='blocked_ips'),
    path('admin-panel/security/login-logs/', views.login_logs, name='login_logs'),
    path('admin-panel/security/dashboard/', views.security_dashboard, name='security_dashboard'),
    
    # Email Management URLs
    path('admin-panel/email/logs/', views.email_logs, name='email_logs'),
    path('admin-panel/email/templates/', views.email_templates, name='email_templates'),
    path('admin-panel/email/bulk/', views.send_bulk_email, name='send_bulk_email'),
    path('admin-panel/email/dashboard/', views.email_dashboard, name='email_dashboard'),
    
]