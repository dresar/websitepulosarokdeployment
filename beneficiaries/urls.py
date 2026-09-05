from django.urls import path
from . import views

app_name = 'beneficiaries'

urlpatterns = [
    # Tampilan publik
    path('', views.beneficiaries_index, name='index'),
    path('list/', views.beneficiaries_list, name='beneficiaries_list'),
    path('categories/', views.beneficiary_categories, name='beneficiary_categories'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('programs/', views.aid_programs, name='aid_programs'),
    path('programs/<int:aid_id>/', views.aid_detail, name='aid_detail'),
    path('statistics/', views.aid_statistics, name='aid_statistics'),
    path('data-bantuan/', views.data_bantuan_list, name='data_bantuan_list'),
    path('documents/', views.documents_list, name='documents_list'),
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    
    # Admin dashboard
    path('admin/dashboard/', views.admin_beneficiaries_dashboard, name='admin_beneficiaries_dashboard'),
    
    # Admin CRUD operations
    path('admin/beneficiaries/', views.admin_beneficiaries_list, name='admin_beneficiaries_list'),
    path('admin/beneficiaries/create/', views.admin_beneficiary_create, name='beneficiary_create'),
    path('admin/beneficiaries/<int:pk>/', views.admin_beneficiary_detail, name='beneficiary_detail'),
    path('admin/beneficiaries/<int:pk>/edit/', views.admin_beneficiary_update, name='beneficiary_edit'),
    path('admin/beneficiaries/<int:pk>/delete/', views.admin_beneficiary_delete, name='beneficiary_delete'),
    # path('admin/beneficiaries/bulk-action/', views.admin_beneficiaries_bulk_action, name='beneficiaries_bulk_action'),
    
    # Categories CRUD
    path('admin/categories/', views.admin_categories_list, name='admin_categories_list'),
    path('admin/categories/create/', views.admin_category_create, name='category_create'),
    path('admin/categories/<int:pk>/edit/', views.admin_category_update, name='category_edit'),
    path('admin/categories/<int:pk>/delete/', views.admin_category_delete, name='category_delete'),
    
    # Aid Programs CRUD
    path('admin/aid-programs/', views.admin_aid_programs_list, name='admin_aid_programs_list'),
    path('admin/aid-programs/create/', views.admin_aid_program_create, name='aid_program_create'),
    path('admin/aid-programs/<int:pk>/edit/', views.admin_aid_program_update, name='aid_program_edit'),
    path('admin/aid-programs/<int:pk>/delete/', views.admin_aid_program_delete, name='aid_program_delete'),
    
    # Distributions CRUD
    path('admin/distributions/', views.admin_distributions_list, name='admin_distributions_list'),
    path('admin/distributions/create/', views.admin_distribution_create, name='distribution_create'),
    # path('admin/distributions/<int:distribution_id>/edit/', views.admin_distribution_edit, name='distribution_edit'),
    # path('admin/distributions/<int:distribution_id>/delete/', views.admin_distribution_delete, name='distribution_delete'),
    
    # Verifications CRUD
    path('admin/verifications/', views.admin_verifications_list, name='admin_verifications_list'),
    path('admin/verifications/<int:pk>/edit/', views.admin_verification_update, name='verification_edit'),
    # path('admin/verifications/<int:verification_id>/delete/', views.admin_verification_delete, name='verification_delete'),
    
    # Reports
    path('admin/reports/', views.admin_beneficiaries_reports, name='admin_beneficiaries_reports'),
    
    # API endpoints
    path('api/beneficiaries/', views.api_beneficiaries_list, name='api_beneficiaries_list'),
    path('api/beneficiaries/<int:beneficiary_id>/', views.api_beneficiary_detail, name='api_beneficiary_detail'),
    path('api/categories/', views.api_categories_list, name='api_categories_list'),
    path('api/beneficiaries-stats/', views.api_beneficiaries_stats, name='api_beneficiaries_stats'),
    path('api/aid-stats/', views.api_aid_stats, name='api_aid_stats'),
]