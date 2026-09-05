from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Dashboard
    path('', views.documents_dashboard, name='documents_dashboard'),
    
    # Documents CRUD
    path('list/', views.documents_list, name='documents_list'),
    path('create/', views.document_create, name='document_create'),
    path('<int:pk>/', views.document_detail, name='document_detail'),
    path('<int:pk>/edit/', views.document_edit, name='document_edit'),
    path('<int:pk>/delete/', views.document_delete, name='document_delete'),
    
    # Document comments
    path('<int:pk>/comment/', views.document_comment_add, name='document_comment_add'),
    
    # Categories
    path('categories/', views.document_categories_list, name='document_categories_list'),
    path('categories/create/', views.document_category_create, name='document_category_create'),
    path('categories/<int:pk>/edit/', views.document_category_edit, name='document_category_edit'),
    path('categories/<int:pk>/delete/', views.document_category_delete, name='document_category_delete'),
    
    # Document preview
    path('<int:pk>/preview/', views.document_preview, name='document_preview'),
    
    # API endpoints
    path('api/penduduk-search/', views.api_penduduk_search, name='api_penduduk_search'),
    path('api/stats/', views.api_documents_stats, name='api_documents_stats'),
]