"""
URL configuration for pulosarok_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponseForbidden

# View untuk blokir admin bawaan
def block_admin(request):
    """Blokir akses ke Django admin bawaan"""
    return HttpResponseForbidden("Akses ditolak.")

urlpatterns = [
    # Admin URLs - Django admin bawaan diblokir, admin panel kustom tetap aktif
    # path('admin/', admin.site.urls),  # DIHAPUS - Django admin bawaan
    path('admin/', block_admin, name='block_admin'),  # Blokir akses admin bawaan
    
    # Core URLs
    path('', include('core.urls')),
    
    # Admin Panel URLs
    path('admin-panel/', include('admin_panel.urls')),
    
    # App URLs
    path('beneficiaries/', include('beneficiaries.urls')),
    path('business/', include('business.urls')),
    path('complaints/', include('complaints.urls')),
    path('documents/', include('documents.urls')),
    path('layanan/', include('layanan.urls')),
    path('letters/', include('letters.urls')),
    path('news/', include('news.urls')),
    path('organization/', include('organization.urls')),
    path('posyandu/', include('posyandu.urls')),
    path('references/', include('references.urls')),
    path('tourism/', include('tourism.urls')),
    path('village-profile/', include('village_profile.urls')),
    
    # API URLs (with different namespaces)
    path('api/', include('core.urls', namespace='api_core')),
    path('api/beneficiaries/', include('beneficiaries.urls', namespace='api_beneficiaries')),
    path('api/business/', include('business.urls', namespace='api_business')),
    path('api/complaints/', include('complaints.urls', namespace='api_complaints')),
    path('api/documents/', include('documents.urls', namespace='api_documents')),
    path('api/layanan/', include('layanan.urls', namespace='api_layanan')),
    path('api/letters/', include('letters.urls', namespace='api_letters')),
    path('api/news/', include('news.urls', namespace='api_news')),
    path('api/organization/', include('organization.urls', namespace='api_organization')),
    path('api/posyandu/', include('posyandu.urls', namespace='api_posyandu')),
    path('api/references/', include('references.urls', namespace='api_references')),
    path('api/tourism/', include('tourism.urls', namespace='api_tourism')),
    path('api/village-profile/', include('village_profile.urls', namespace='api_village_profile')),
    
    
    # Home page - handled by core.urls
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Django default error handlers will be used for development
