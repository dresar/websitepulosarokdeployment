from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.core.serializers.json import DjangoJSONEncoder
from .models import Announcement, NotificationSettings
import json

@require_GET
def get_announcements(request):
    """
    API endpoint untuk mendapatkan daftar pengumuman aktif
    """
    try:
        # Ambil pengumuman yang aktif
        announcements = Announcement.objects.filter(
            status='published',
            start_date__lte=timezone.now()
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
        ).order_by('-is_pinned', '-priority', '-start_date')
        
        # Batasi jumlah pengumuman berdasarkan pengaturan
        settings = NotificationSettings.get_active_settings()
        max_notifications = settings.max_notifications
        announcements = announcements[:max_notifications]
        
        # Format data untuk respons JSON
        announcements_data = []
        for announcement in announcements:
            announcements_data.append({
                'id': announcement.id,
                'title': announcement.title,
                'excerpt': announcement.excerpt,
                'content': announcement.content,
                'type': announcement.announcement_type,  # Changed from 'announcement_type' to 'type'
                'priority': announcement.priority,
                'isPinned': announcement.is_pinned,  # Changed from 'is_pinned' to 'isPinned'
                'startDate': announcement.start_date.strftime('%Y-%m-%d %H:%M:%S'),  # Changed from 'start_date' to 'startDate'
                'endDate': announcement.end_date.strftime('%Y-%m-%d %H:%M:%S') if announcement.end_date else None,  # Changed from 'end_date' to 'endDate'
                'slug': announcement.slug,
                'url': announcement.get_absolute_url(),
            })
        
        return JsonResponse({
            'success': True,
            'count': len(announcements_data),
            'data': announcements_data,  # Changed from 'announcements' to 'data'
            'settings': {
                'autoShowDelay': settings.auto_show_delay,  # Changed from 'auto_show_delay' to 'autoShowDelay'
                'autoHideDelay': settings.auto_hide_delay,  # Changed from 'auto_hide_delay' to 'autoHideDelay'
                'slideAnimation': settings.slide_animation,  # Changed from 'slide_animation' to 'slideAnimation'
                'soundEnabled': settings.sound_enabled,  # Changed from 'sound_enabled' to 'soundEnabled'
                'vibrationEnabled': settings.vibration_enabled,  # Changed from 'vibration_enabled' to 'vibrationEnabled'
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_GET
def get_announcement_detail(request, announcement_id):
    """
    API endpoint untuk mendapatkan detail pengumuman
    """
    try:
        announcement = get_object_or_404(
            Announcement,
            id=announcement_id,
            status='published',
            start_date__lte=timezone.now()
        )
        
        # Periksa apakah pengumuman masih aktif
        is_active = True
        if announcement.end_date and announcement.end_date < timezone.now():
            is_active = False
        
        # Format data untuk respons JSON
        announcement_data = {
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'type': announcement.announcement_type,
            'priority': announcement.priority,
            'isPinned': announcement.is_pinned,
            'isActive': is_active,
            'startDate': announcement.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'endDate': announcement.end_date.strftime('%Y-%m-%d %H:%M:%S') if announcement.end_date else None,
            'targetAudience': announcement.target_audience,
            'contactPerson': announcement.contact_person,
            'contactPhone': announcement.contact_phone,
            'location': announcement.location,
            'slug': announcement.slug,
            'url': announcement.get_absolute_url(),
        }
        
        return JsonResponse({
            'success': True,
            'announcement': announcement_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_GET
def get_notification_settings(request):
    """
    API endpoint untuk mendapatkan pengaturan notifikasi
    """
    try:
        settings = NotificationSettings.get_active_settings()
        
        settings_data = {
            'isEnabled': settings.is_enabled,
            'showInNavbar': settings.show_in_navbar,
            'autoShowDelay': settings.auto_show_delay,
            'autoHideDelay': settings.auto_hide_delay,
            'showCountBadge': settings.show_count_badge,
            'maxNotifications': settings.max_notifications,
            'slideAnimation': settings.slide_animation,
            'soundEnabled': settings.sound_enabled,
            'vibrationEnabled': settings.vibration_enabled,
        }
        
        return JsonResponse({
            'success': True,
            'data': settings_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)