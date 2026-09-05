from django.urls import path
from . import views

app_name = 'layanan'

urlpatterns = [
    # Main pages
    path('', views.LayananIndexView.as_view(), name='index'),
    path('chat/', views.ChatLayananView.as_view(), name='chat_layanan'),
    
    # Document services
    path('dokumen/', views.DocumentServicesView.as_view(), name='document_services'),
    path('dokumen/info/', views.DocumentInfoView.as_view(), name='document_info'),
    path('dokumen/ajukan/', views.DocumentRequestView.as_view(), name='document_request'),
    path('dokumen/status/', views.RequestStatusView.as_view(), name='request_status'),
    
    # Other services
    path('posyandu/', views.PosyanduServicesView.as_view(), name='posyandu_services'),
    path('bisnis/', views.BusinessServicesView.as_view(), name='business_services'),
    path('wisata/', views.TourismServicesView.as_view(), name='tourism_services'),
    
    # API endpoints
    path('api/chat/', views.api_chat_message, name='api_chat_message'),
    path('api/document-types/', views.api_document_types, name='api_document_types'),
    path('api/request-status/', views.api_request_status, name='api_request_status'),
]




