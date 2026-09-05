from django.urls import path
from . import views, api_views

app_name = 'news'

urlpatterns = [
    # Admin dashboard
    path('admin/dashboard/', views.admin_news_dashboard, name='admin_news_dashboard'),
    
    # News list and detail views
    path('', views.NewsListView.as_view(), name='list'),
    path('detail/<slug:slug>/', views.NewsDetailView.as_view(), name='detail'),
    
    # Category and tag views
    path('category/<slug:category_slug>/', views.news_by_category, name='by_category'),
    path('tag/<slug:tag_slug>/', views.news_by_tag, name='by_tag'),
    
    # AJAX endpoints for analytics
    path('like/<int:news_id>/', views.like_news, name='like'),
    path('share/<int:news_id>/', views.share_news, name='share'),
    path('csrf-token/', views.get_csrf_token, name='csrf_token'),
    
    # Comment functionality
    path('comment/<slug:slug>/', views.add_comment, name='add_comment'),
    
    # Announcements
    path('announcements/', views.announcements_list, name='announcements'),
    path('announcement/<slug:slug>/', views.announcement_detail, name='announcement_detail'),
    
    # API endpoints
    path('api/announcements/', api_views.get_announcements, name='api_announcements'),
    path('api/announcement/<int:announcement_id>/', api_views.get_announcement_detail, name='api_announcement_detail'),
    path('api/notification-settings/', api_views.get_notification_settings, name='api_notification_settings'),
]