from django.urls import path
from . import admin_views

app_name = 'layanan'

urlpatterns = [
    # Dashboard
    path('', admin_views.layanan_dashboard, name='dashboard'),
    
    # Feedback Management
    path('feedback/', admin_views.feedback_list, name='feedback_list'),
    path('feedback/<int:pk>/', admin_views.feedback_detail, name='feedback_detail'),
    path('feedback/form/', admin_views.feedback_form, name='feedback_form'),
    path('feedback/<int:pk>/mark-read/', admin_views.feedback_mark_read, name='feedback_mark_read'),
    path('feedback/<int:pk>/reply/', admin_views.feedback_reply, name='feedback_reply'),
    
    # FAQ Management
    path('faq/', admin_views.faq_list, name='faq_list'),
    path('faq/form/', admin_views.faq_form, name='faq_form'),
    
    # Contact Management
    path('contact/', admin_views.contact_list, name='contact_list'),
    path('contact/form/', admin_views.contact_form, name='contact_form'),
    
    # Service Management
    path('service/', admin_views.service_list, name='service_list'),
    path('service/form/', admin_views.service_form, name='service_form'),
    
    # AJAX Endpoints
    path('ajax/create-feedback/', admin_views.ajax_create_feedback, name='ajax_create_feedback'),
    path('ajax/create-faq/', admin_views.ajax_create_faq, name='ajax_create_faq'),
    path('ajax/create-contact/', admin_views.ajax_create_contact, name='ajax_create_contact'),
    path('ajax/create-service/', admin_views.ajax_create_service, name='ajax_create_service'),
    path('ajax/delete-item/', admin_views.ajax_delete_item, name='ajax_delete_item'),
    path('ajax/toggle-status/', admin_views.ajax_toggle_status, name='ajax_toggle_status'),
]