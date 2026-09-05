from django.urls import path, re_path
from . import views

app_name = 'letters'

urlpatterns = [
    # Admin login for letters - removed
    
    # Halaman utama layanan dokumen
    path('', views.document_services, name='document_services'),
    
    # Halaman informasi dokumen
    path('info/<int:document_type_id>/', views.document_info, name='document_info'),
    # URL alternatif untuk info
    path('info/', views.document_services, name='document_info_list'),
    # URL dengan format /info/7/
re_path(r'info/(?P<document_type_id>\d+)/$', views.document_info, name='document_info'),
    
    # Halaman pengajuan dokumen
    path('request/', views.document_request, name='document_request'),
    path('request/<int:document_type_id>/', views.document_request, name='document_request_type'),
    # URL dengan format /request/7/
re_path(r'request/(?P<document_type_id>\d+)/$', views.document_request, name='document_request_type'),
    
    # Halaman status permohonan
    path('status/', views.request_status, name='request_status'),
    
    # Detail surat
    path('detail/<int:letter_id>/', views.letter_detail, name='letter_detail'),
    
    # Chat layanan
    path('chat/', views.chat_layanan, name='chat_layanan'),
    
    # API Endpoints
    path('api/document-types/', views.api_document_types, name='api_document_types'),
    path('api/search-residents/', views.api_search_residents, name='api_search_residents'),
    path('api/submit-request/', views.api_submit_request, name='api_submit_request'),
    path('api/request-status/', views.api_request_status, name='api_request_status'),
    path('api/chat/', views.api_chat_message, name='api_chat_message'),
]