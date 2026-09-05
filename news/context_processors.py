from django.utils import timezone
from django.db.models import Q
from .models import NotificationSettings, Announcement, News

def notification_settings(request):
    """Context processor untuk pengaturan notifikasi"""
    try:
        settings = NotificationSettings.get_active_settings()
        announcements = Announcement.objects.filter(
            status='published',
            start_date__lte=timezone.now()
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
        ).order_by('-is_pinned', '-priority', '-start_date')[:settings.max_notifications]
        
        return {
            'notification_settings': settings,
            'announcements': announcements if settings.is_enabled else [],
        }
    except Exception:
        return {
            'notification_settings': None,
            'announcements': [],
        }

def latest_news(request):
    """Context processor untuk berita terbaru"""
    try:
        latest_news = News.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).order_by('-published_date')[:5]
        
        return {
            'latest_news': latest_news,
        }
    except Exception:
        return {
            'latest_news': [],
        }
