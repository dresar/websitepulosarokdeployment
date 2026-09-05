from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    # Admin URLs
    path('admin/dashboard/', views.admin_complaints_dashboard, name='admin_complaints_dashboard'),
    path('admin/complaints/', views.admin_complaints_list, name='admin_complaints_list'),
    path('admin/complaints/create/', views.admin_complaint_create, name='admin_complaint_create'),
    path('admin/complaints/<int:pk>/', views.admin_complaint_detail, name='admin_complaint_detail'),
    path('admin/complaints/<int:pk>/update/', views.admin_complaint_update, name='admin_complaint_update'),
    path('admin/complaints/<int:pk>/delete/', views.admin_complaint_delete, name='admin_complaint_delete'),
    path('admin/complaints/<int:pk>/add-update/', views.admin_complaint_add_update, name='admin_complaint_add_update'),
    path('admin/categories/', views.admin_categories_list, name='admin_categories_list'),
    path('admin/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/categories/<int:pk>/update/', views.admin_category_update, name='admin_category_update'),
    path('admin/categories/<int:pk>/delete/', views.admin_category_delete, name='admin_category_delete'),
    path('admin/verifications/', views.admin_verifications_list, name='admin_verifications_list'),
    path('admin/verifications/dashboard/', views.admin_verification_dashboard, name='admin_verification_dashboard'),
    path('admin/verifications/create/<int:complaint_id>/', views.admin_verification_create, name='admin_verification_create'),
    path('admin/verifications/<int:pk>/', views.admin_verification_detail, name='admin_verification_detail'),
    path('admin/verifications/<int:pk>/update/', views.admin_verification_update, name='admin_verification_update'),
    path('admin/verifications/<int:pk>/delete/', views.admin_verification_delete, name='admin_verification_delete'),
    
    # Complaint URLs
    path('', views.complaint_form_view, name='complaint_form'),
    path('buat-pengaduan/', views.complaint_form_view, name='create_complaint'),
    path('sukses/<uuid:complaint_id>/', views.complaint_success_view, name='complaint_success'),
    path('lacak/', views.complaint_tracking_view, name='complaint_tracking'),
    path('daftar/', views.complaint_list_view, name='complaint_list'),
    path('detail/<uuid:complaint_id>/', views.complaint_detail_view, name='complaint_detail'),
    
    # Chat URLs
    path('chat/modal/', views.chat_modal_view, name='chat_modal'),
    path('api/chat/start/', views.chat_start_session, name='chat_start_session'),
    path('api/chat/send/', views.chat_send_message, name='chat_send_message'),
    path('api/chat/messages/<uuid:session_id>/', views.chat_get_messages, name='chat_get_messages'),
    
    # API URLs
    path('api/stats/', views.api_complaint_stats, name='api_stats'),
    path('api/categories/', views.api_categories, name='api_categories'),
    
    # Export URLs
    path('admin/export/', views.export_complaints, name='export_complaints'),
    
    # Contact URLs
    path('kontak/', views.contact_view, name='contact'),
    path('kontak/sukses/<str:contact_id>/', views.contact_success_view, name='contact_success'),
]