from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.urls import reverse
from django.conf import settings
import json
import re
from user_agents import parse
from .models import (
    News, NewsCategory, NewsTag, NewsComment, 
    NewsView, NewsLike, NewsShare, Announcement, NotificationSettings
)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request):
    """Extract device information from user agent"""
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)
    
    return {
        'device_type': 'mobile' if user_agent.is_mobile else 'tablet' if user_agent.is_tablet else 'desktop',
        'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
        'operating_system': f"{user_agent.os.family} {user_agent.os.version_string}",
        'user_agent': user_agent_string
    }


def track_news_view(request, news):
    """Track news view with analytics"""
    ip_address = get_client_ip(request)
    
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key or ''
    
    device_info = get_device_info(request)
    
    # Use get_or_create to avoid duplicate entries
    view_record, created = NewsView.objects.get_or_create(
        news=news,
        ip_address=ip_address,
        session_key=session_key,
        defaults={
            'user': request.user if request.user.is_authenticated else None,
            'user_agent': device_info['user_agent'],
            'referrer': request.META.get('HTTP_REFERER', ''),
            'device_type': device_info['device_type'],
            'browser': device_info['browser'],
            'operating_system': device_info['operating_system'],
        }
    )
    
    # Always update the view date to track the latest visit
    view_record.view_date = timezone.now()
    view_record.save()
    
    # Increment total_views counter for every page load
    news.total_views += 1
    news.save(update_fields=['total_views'])
    
    return view_record


class NewsListView(ListView):
    """List view for news with search and filtering"""
    model = News
    template_name = 'public/news/news.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = News.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).select_related('category', 'author').prefetch_related('tags')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        # Category filtering
        category_id = self.request.GET.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Annotate with like and share counts
        queryset = queryset.annotate(
            total_likes=Count('likes', distinct=True),
            total_shares=Count('shares', distinct=True)
        )
        
        return queryset.order_by('-is_featured', '-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get categories for filter
        context['categories'] = NewsCategory.objects.filter(
            is_active=True,
            news__status='published'
        ).distinct().order_by('name')
        
        # Get featured news
        featured_news = News.objects.filter(
            status='published',
            is_featured=True,
            published_date__lte=timezone.now()
        ).select_related('category', 'author').annotate(
            total_likes=Count('likes', distinct=True),
            total_shares=Count('shares', distinct=True)
        ).order_by('-published_date')[:3]
        
        context['featured_news'] = featured_news
        
        # Get breaking news
        breaking_news = News.objects.filter(
            status='published',
            is_breaking=True,
            published_date__lte=timezone.now()
        ).select_related('category', 'author').annotate(
            total_likes=Count('likes', distinct=True),
            total_shares=Count('shares', distinct=True)
        ).order_by('-published_date')[:5]
        
        context['breaking_news'] = breaking_news
        
        # Get popular tags
        popular_tags = NewsTag.objects.annotate(
            news_count=Count('news')
        ).filter(news__status='published').order_by('-news_count')[:10]
        
        context['popular_tags'] = popular_tags
        
        # Search and filter context
        context['search_query'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category_id', '')
        context['page_title'] = 'Berita Desa Pulosarok'
        
        # Filter parameters
        context['featured_filter'] = self.request.GET.get('featured', '')
        context['breaking_filter'] = self.request.GET.get('breaking', '')
        
        return context


class NewsDetailView(DetailView):
    """Detail view for individual news with analytics tracking"""
    model = News
    template_name = 'public/news/news_detail.html'
    context_object_name = 'news'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return News.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).select_related('category', 'author').prefetch_related('tags', 'images')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Track the view
        track_news_view(self.request, obj)
        
        # Update news counts
        obj.update_counts()
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news = context['news']
        
        # Get related news with proper counts
        related_news = News.objects.filter(
            status='published',
            published_date__lte=timezone.now(),
            category=news.category
        ).exclude(id=news.id).annotate(
            total_likes=Count('likes', distinct=True),
            total_shares=Count('shares', distinct=True)
        ).order_by('-published_date')[:5]
        
        # Get news with same tags
        tag_related_news = News.objects.filter(
            status='published',
            published_date__lte=timezone.now(),
            tags__in=news.tags.all()
        ).exclude(id=news.id).annotate(
            total_likes=Count('likes', distinct=True),
            total_shares=Count('shares', distinct=True)
        ).order_by('-published_date')[:3]
        
        # Get comments for this news
        comments = news.comments.filter(status='approved').order_by('-created_at')
        
        # Get view statistics
        view_stats = {
            'total_views': news.total_views,
            'unique_views': news.view_records.values('ip_address').distinct().count(),
        }
        
        context['related_news'] = related_news
        context['tag_related_news'] = tag_related_news
        context['comments'] = comments
        context['view_stats'] = view_stats
        context['page_title'] = news.title
        context['meta_description'] = news.meta_description or news.excerpt
        
        return context


@require_POST
@csrf_exempt
def like_news(request, news_id):
    """AJAX endpoint to like/unlike news"""
    try:
        news = get_object_or_404(News, id=news_id, status='published')
        ip_address = get_client_ip(request)
        
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key or ''
        
        device_info = get_device_info(request)
        
        # Check if already liked
        like_record, created = NewsLike.objects.get_or_create(
            news=news,
            ip_address=ip_address,
            session_key=session_key,
            defaults={
                'user': request.user if request.user.is_authenticated else None,
                'user_agent': device_info['user_agent'],
            }
        )
        
        if not created:
            # Unlike - remove the like
            like_record.delete()
            liked = False
        else:
            liked = True
        
        # Get updated counts
        total_likes = news.likes.count()
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': total_likes
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def share_news(request, news_id):
    """AJAX endpoint to track news sharing"""
    try:
        # Try to get platform from JSON body, fallback to 'other'
        platform = 'other'
        try:
            data = json.loads(request.body)
            platform = data.get('platform', 'other')
        except:
            # If no JSON body, try to get from POST data
            platform = request.POST.get('platform', 'other')
        
        news = get_object_or_404(News, id=news_id, status='published')
        ip_address = get_client_ip(request)
        
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key or ''
        
        device_info = get_device_info(request)
        
        # Track the share
        NewsShare.objects.create(
            news=news,
            platform=platform,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip_address,
            session_key=session_key,
            user_agent=device_info['user_agent'],
            referrer=request.META.get('HTTP_REFERER', '')
        )
        
        # Get updated counts
        total_shares = news.shares.count()
        
        return JsonResponse({
            'success': True,
            'total_shares': total_shares
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def add_comment(request, slug):
    """Add comment to news article"""
    news = get_object_or_404(News, slug=slug, status='published')
    
    if request.method == 'POST':
        author_name = request.POST.get('author_name', '').strip()
        author_email = request.POST.get('author_email', '').strip()
        author_website = request.POST.get('author_website', '').strip()
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        # Basic validation
        if not all([author_name, author_email, content]):
            messages.error(request, 'Nama, email, dan komentar harus diisi.')
            return redirect('news:detail', slug=slug)
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, author_email):
            messages.error(request, 'Format email tidak valid.')
            return redirect('news:detail', slug=slug)
        
        # Get parent comment if replying
        parent = None
        if parent_id:
            try:
                parent = NewsComment.objects.get(id=parent_id, news=news)
            except NewsComment.DoesNotExist:
                pass
        
        # Create comment
        ip_address = get_client_ip(request)
        device_info = get_device_info(request)
        
        comment = NewsComment.objects.create(
            news=news,
            author_name=author_name,
            author_email=author_email,
            author_website=author_website,
            content=content,
            parent=parent,
            ip_address=ip_address,
            user_agent=device_info['user_agent'],
            status='pending'  # Require moderation
        )
        
        # Update news counts
        news.update_counts()
        
        messages.success(request, 'Komentar Anda telah dikirim dan menunggu moderasi.')
        return redirect('news:detail', slug=slug)
    
    return redirect('news:detail', slug=slug)


def news_by_category(request, category_slug):
    """View news by category"""
    category = get_object_or_404(NewsCategory, slug=category_slug, is_active=True)
    
    news_list = News.objects.filter(
        status='published',
        published_date__lte=timezone.now(),
        category=category
    ).select_related('category', 'author').prefetch_related('tags').annotate(
        total_likes=Count('likes', distinct=True),
        total_shares=Count('shares', distinct=True)
    ).order_by('-published_date')
    
    # Get featured news in this category
    featured_news = news_list.filter(is_featured=True).annotate(
        total_likes=Count('likes', distinct=True),
        total_shares=Count('shares', distinct=True)
    ).order_by('-published_date')[:3]
    
    # Get total views for this category
    total_views = news_list.aggregate(total=Count('view_records'))['total'] or 0
    
    # Get related categories
    related_categories = NewsCategory.objects.filter(
        is_active=True
    ).exclude(id=category.id).annotate(
        news_count=Count('news', filter=Q(news__status='published'))
    ).filter(news_count__gt=0).order_by('-news_count')[:5]
    
    paginator = Paginator(news_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'news_list': page_obj,
        'category': category,
        'featured_news': featured_news,
        'total_views': total_views,
        'related_categories': related_categories,
        'page_title': f'Berita {category.name}',
        'categories': NewsCategory.objects.filter(is_active=True).order_by('name'),
        'pagination': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'public/news/category.html', context)


def news_by_tag(request, tag_slug):
    """View news by tag"""
    tag = get_object_or_404(NewsTag, slug=tag_slug)
    
    news_list = News.objects.filter(
        status='published',
        published_date__lte=timezone.now(),
        tags=tag
    ).select_related('category', 'author').prefetch_related('tags').annotate(
        total_likes=Count('likes', distinct=True),
        total_shares=Count('shares', distinct=True)
    ).order_by('-published_date')
    
    # Get popular tags
    popular_tags = NewsTag.objects.annotate(
        news_count=Count('news')
    ).filter(news__status='published').order_by('-news_count')[:15]
    
    # Get related tags (tags used with this tag)
    related_tags = NewsTag.objects.filter(
        news__tags=tag,
        news__status='published'
    ).exclude(id=tag.id).annotate(
        news_count=Count('news', filter=Q(news__status='published'))
    ).distinct().order_by('-news_count')[:10]
    
    paginator = Paginator(news_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'news_list': page_obj,
        'tag': tag,
        'popular_tags': popular_tags,
        'related_tags': related_tags,
        'page_title': f'Berita dengan Tag {tag.name}',
        'categories': NewsCategory.objects.filter(is_active=True).order_by('name'),
        'pagination': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'public/news/tag.html', context)


def announcements_list(request):
    """List active announcements with pagination"""
    from django.core.paginator import Paginator
    
    announcements = Announcement.objects.filter(
        status='published',
        start_date__lte=timezone.now()
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
    ).order_by('-is_pinned', '-priority', '-start_date')
    
    # Get pinned announcements
    pinned_announcements = announcements.filter(is_pinned=True)
    
    # Get statistics
    active_count = announcements.count()
    urgent_count = announcements.filter(priority='urgent').count()
    
    # Pagination
    paginator = Paginator(announcements, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'announcements': page_obj,
        'pinned_announcements': pinned_announcements,
        'active_count': active_count,
        'urgent_count': urgent_count,
        'page_obj': page_obj,
        'page_title': 'Pengumuman Desa Pulosarok',
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'public/news/announcements.html', context)


def announcement_detail(request, slug):
    """Detail view for announcement"""
    announcement = get_object_or_404(
        Announcement,
        slug=slug,
        status='published',
        start_date__lte=timezone.now()
    )
    
    # Check if announcement is still active
    if announcement.end_date and announcement.end_date < timezone.now():
        messages.warning(request, 'Pengumuman ini sudah tidak aktif.')
    
    # Get related announcements (same type or priority)
    related_announcements = Announcement.objects.filter(
        status='published',
        start_date__lte=timezone.now()
    ).filter(
        Q(announcement_type=announcement.announcement_type) |
        Q(priority=announcement.priority)
    ).exclude(id=announcement.id).order_by('-start_date')[:5]
    
    context = {
        'announcement': announcement,
        'related_announcements': related_announcements,
        'page_title': announcement.title
    }
    
    return render(request, 'public/news/announcement_detail.html', context)


def get_csrf_token(request):
    """Get CSRF token for AJAX requests"""
    return JsonResponse({'csrf_token': get_token(request)})

# ==================== ADMIN PANEL INTEGRATION ====================

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Avg, Sum, Max, Min
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from core.models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import csv

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser

# ==================== ADMIN DASHBOARD ====================

@login_required
@user_passes_test(is_admin)
def admin_news_dashboard(request):
    """Admin dashboard for news management"""
    # Basic statistics
    total_news = News.objects.count()
    published_news = News.objects.filter(status='published').count()
    draft_news = News.objects.filter(status='draft').count()
    total_categories = NewsCategory.objects.count()
    total_tags = NewsTag.objects.count()
    total_comments = NewsComment.objects.count()
    pending_comments = NewsComment.objects.filter(status='pending').count()
    
    # View statistics
    total_views = NewsView.objects.count()
    total_likes = NewsLike.objects.count()
    total_shares = NewsShare.objects.count()
    
    # Recent news
    recent_news = News.objects.select_related('category', 'author').order_by('-created_at')[:10]
    
    # Recent comments
    recent_comments = NewsComment.objects.select_related('news').order_by('-created_at')[:10]
    
    # Popular news (by views)
    popular_news = News.objects.annotate(
        view_count=Count('view_records')
    ).order_by('-view_count')[:5]
    
    # Category statistics
    category_stats = NewsCategory.objects.annotate(
        news_count=Count('news')
    ).order_by('-news_count')[:5]
    
    
    # Daily views (last 30 days) - keeping for potential future use
    daily_views = NewsView.objects.filter(
        view_date__gte=timezone.now() - timedelta(days=30)
    ).annotate(
        date=TruncDate('view_date')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Today's views
    today_views = NewsView.objects.filter(
        view_date__date=timezone.now().date()
    ).count()
    
    # This week's views (last 7 days)
    week_views = NewsView.objects.filter(
        view_date__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # This month's views
    month_views = NewsView.objects.filter(
        view_date__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Active authors (users who have published news in last 30 days)
    active_authors = CustomUser.objects.filter(
        news_articles__created_at__gte=timezone.now() - timedelta(days=30),
        news_articles__status='published'
    ).distinct().count()
    
    # Top authors
    top_authors = CustomUser.objects.annotate(
        news_count=Count('news_articles')
    ).order_by('-news_count')[:5]
    
    context = {
        'title': 'Dashboard Berita',
        'total_news': total_news,
        'published_news': published_news,
        'draft_news': draft_news,
        'total_categories': total_categories,
        'total_tags': total_tags,
        'total_comments': total_comments,
        'pending_comments': pending_comments,
        'total_views': total_views,
        'total_likes': total_likes,
        'total_shares': total_shares,
        'recent_news': recent_news,
        'recent_comments': recent_comments,
        'popular_news': popular_news,
        'category_stats': category_stats,
        'daily_views': list(daily_views),
        'today_views': today_views,
        'week_views': week_views,
        'month_views': month_views,
        'active_authors': active_authors,
        'top_authors': top_authors,
    }
    return render(request, 'admin_panel/news/dashboard.html', context)

# ==================== NEWS MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_news_list(request):
    """Admin list view for news"""
    news = News.objects.select_related('category', 'author').annotate(
        view_count=Count('view_records'),
        like_count=Count('likes'),
        comment_count=Count('comments')
    ).order_by('-created_at')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        news = news.filter(category_id=category_id)
    
    # Filter by author
    author_id = request.GET.get('author')
    if author_id:
        news = news.filter(author_id=author_id)
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'published':
        news = news.filter(status='published')
    elif status == 'draft':
        news = news.filter(status='draft')
    elif status == 'featured':
        news = news.filter(is_featured=True)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        news = news.filter(created_at__gte=parse_date(start_date))
    if end_date:
        news = news.filter(created_at__lte=parse_date(end_date))
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        news = news.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(excerpt__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()
    
    # Pagination
    paginator = Paginator(news, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = NewsCategory.objects.all()
    authors = CustomUser.objects.filter(news_articles__isnull=False).distinct()
    
    context = {
        'title': 'Manajemen Berita',
        'news': page_obj,
        'categories': categories,
        'authors': authors,
        'current_filters': {
            'category': category_id,
            'author': author_id,
            'status': status,
            'start_date': start_date,
            'end_date': end_date,
            'search': search,
        }
    }
    return render(request, 'admin_panel/news/list.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_news_create(request):
    """Create new news"""
    if request.method == 'POST':
        try:
            # Create news
            news = News.objects.create(
                title=request.POST.get('title'),
                slug=request.POST.get('slug'),
                excerpt=request.POST.get('excerpt', ''),
                content=request.POST.get('content'),
                category_id=request.POST.get('category'),
                author=request.user,
                status=request.POST.get('status', 'draft'),
                priority=request.POST.get('priority', 'normal'),
                is_featured=request.POST.get('is_featured') == 'on',
                is_breaking=request.POST.get('is_breaking') == 'on',
                allow_comments=request.POST.get('allow_comments') == 'true',
                meta_title=request.POST.get('meta_title', ''),
                meta_description=request.POST.get('meta_description', ''),
                featured_image_alt=request.POST.get('featured_image_alt', ''),
                youtube_url=request.POST.get('youtube_url', ''),
            )
            
            # Handle dates
            published_date = request.POST.get('published_date')
            if published_date:
                from django.utils.dateparse import parse_datetime
                news.published_date = parse_datetime(published_date)
            
            scheduled_date = request.POST.get('scheduled_date')
            if scheduled_date:
                from django.utils.dateparse import parse_datetime
                news.scheduled_date = parse_datetime(scheduled_date)
            
            # Handle featured image upload
            if 'featured_image' in request.FILES:
                news.featured_image = request.FILES['featured_image']
            
            # Handle video file upload
            if 'video_file' in request.FILES:
                news.video_file = request.FILES['video_file']
            
            news.save()
            
            # Add tags
            tag_ids = request.POST.getlist('tags')
            for tag_id in tag_ids:
                if tag_id.startswith('new_'):
                    # Create new tag
                    tag_name = request.POST.get(f'tag_name_{tag_id}', '')
                    if tag_name:
                        tag, created = NewsTag.objects.get_or_create(name=tag_name.strip())
                        news.tags.add(tag)
                else:
                    # Use existing tag
                    try:
                        tag = NewsTag.objects.get(id=tag_id)
                        news.tags.add(tag)
                    except NewsTag.DoesNotExist:
                        pass
            
            return redirect('admin_panel:news_detail', pk=news.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating news: {str(e)}')
    
    # GET request - show create form
    categories = NewsCategory.objects.all()
    all_tags = NewsTag.objects.all()
    
    context = {
        'title': 'Tambah Berita Baru',
        'news': None,
        'categories': categories,
        'all_tags': all_tags,
        'current_tags': [],
    }
    return render(request, 'admin_panel/news/form.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_news_update(request, pk):
    """Update news"""
    news = get_object_or_404(News, pk=pk)
    
    if request.method == 'POST':
        try:
            # Handle form data (not JSON)
            news.title = request.POST.get('title', news.title)
            news.slug = request.POST.get('slug', news.slug)
            news.excerpt = request.POST.get('excerpt', news.excerpt)
            news.content = request.POST.get('content', news.content)
            news.category_id = request.POST.get('category', news.category_id)
            news.status = request.POST.get('status', news.status)
            news.priority = request.POST.get('priority', news.priority)
            news.is_featured = request.POST.get('is_featured') == 'on'
            news.is_breaking = request.POST.get('is_breaking') == 'on'
            news.allow_comments = request.POST.get('allow_comments') == 'true'
            news.meta_title = request.POST.get('meta_title', news.meta_title)
            news.meta_description = request.POST.get('meta_description', news.meta_description)
            news.featured_image_alt = request.POST.get('featured_image_alt', news.featured_image_alt)
            news.youtube_url = request.POST.get('youtube_url', news.youtube_url)
            
            # Handle dates
            published_date = request.POST.get('published_date')
            if published_date:
                from django.utils.dateparse import parse_datetime
                news.published_date = parse_datetime(published_date)
            
            scheduled_date = request.POST.get('scheduled_date')
            if scheduled_date:
                from django.utils.dateparse import parse_datetime
                news.scheduled_date = parse_datetime(scheduled_date)
            
            # Handle featured image upload
            if 'featured_image' in request.FILES:
                news.featured_image = request.FILES['featured_image']
            
            # Handle video file upload
            if 'video_file' in request.FILES:
                news.video_file = request.FILES['video_file']
            
            news.save()
            
            # Update tags
            news.tags.clear()
            tag_ids = request.POST.getlist('tags')
            for tag_id in tag_ids:
                if tag_id.startswith('new_'):
                    # Create new tag
                    tag_name = request.POST.get(f'tag_name_{tag_id}', '')
                    if tag_name:
                        tag, created = NewsTag.objects.get_or_create(name=tag_name.strip())
                        news.tags.add(tag)
                else:
                    # Use existing tag
                    try:
                        tag = NewsTag.objects.get(id=tag_id)
                        news.tags.add(tag)
                    except NewsTag.DoesNotExist:
                        pass
            
            return redirect('admin_panel:news_detail', pk=news.pk)
            
        except Exception as e:
            messages.error(request, f'Error updating news: {str(e)}')
    
    # GET request - show edit form
    categories = NewsCategory.objects.all()
    all_tags = NewsTag.objects.all()
    current_tags = news.tags.all()
    
    context = {
        'title': f'Edit Berita - {news.title}',
        'news': news,
        'categories': categories,
        'all_tags': all_tags,
        'current_tags': current_tags,
    }
    return render(request, 'admin_panel/news/form.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_news_upload_image(request):
    """Upload image for Summernote editor"""
    if request.method == 'POST':
        try:
            image = request.FILES.get('image')
            if not image:
                return JsonResponse({
                    'success': False,
                    'message': 'No image provided'
                })
            
            # Validate image
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                return JsonResponse({
                    'success': False,
                    'message': 'Image size too large. Maximum 5MB allowed.'
                })
            
            # Generate unique filename
            import uuid
            import os
            from django.conf import settings
            
            ext = os.path.splitext(image.name)[1]
            filename = f"summernote_{uuid.uuid4().hex}{ext}"
            
            # Save image
            from django.core.files.storage import default_storage
            path = default_storage.save(f"summernote/{filename}", image)
            
            # Get URL
            url = default_storage.url(path)
            
            return JsonResponse({
                'success': True,
                'url': url,
                'message': 'Image uploaded successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error uploading image: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def admin_news_delete(request, pk):
    """Delete news"""
    try:
        news = get_object_or_404(News, pk=pk)
        title = news.title
        news.delete()
        return JsonResponse({
            'success': True,
            'message': f'Berita "{title}" berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
def admin_news_detail(request, pk):
    """View news details"""
    news = get_object_or_404(News, pk=pk)
    
    # Get analytics data
    views = NewsView.objects.filter(news=news)
    likes = NewsLike.objects.filter(news=news)
    shares = NewsShare.objects.filter(news=news)
    comments = NewsComment.objects.filter(news=news).order_by('-created_at')
    
    # View trends (last 30 days)
    view_trends = views.filter(
        view_date__gte=timezone.now() - timedelta(days=30)
    ).annotate(
        date=TruncDate('view_date')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    context = {
        'title': f'Detail Berita - {news.title}',
        'news': news,
        'total_views': views.count(),
        'total_likes': likes.count(),
        'total_shares': shares.count(),
        'total_comments': comments.count(),
        'comments': comments[:10],
        'view_trends': list(view_trends),
    }
    return render(request, 'admin_panel/news/detail.html', context)

# ==================== CATEGORY MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_news_categories_list(request):
    """Admin list view for news categories"""
    categories = NewsCategory.objects.annotate(
        news_count=Count('news')
    ).order_by('name')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        categories = categories.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(categories, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Manajemen Kategori Berita',
        'categories': page_obj,
        'current_filters': {
            'search': search,
        }
    }
    return render(request, 'admin_panel/news/categories.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_news_category_create(request):
    """Create new news category"""
    if request.method == 'POST':
        try:
            # Handle form data (not JSON)
            category = NewsCategory.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                color=request.POST.get('color', '#007bff'),
                icon=request.POST.get('icon', ''),
                is_active=request.POST.get('is_active') == 'on',
                order=int(request.POST.get('order', 0))
            )
            return JsonResponse({
                'success': True,
                'message': 'Kategori berhasil ditambahkan',
                'data': {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'message': 'Method not allowed'}, status=405)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_news_category_update(request, pk):
    """Update news category"""
    category = get_object_or_404(NewsCategory, pk=pk)
    
    if request.method == 'POST':
        try:
            # Handle form data (not JSON)
            category.name = request.POST.get('name', category.name)
            category.description = request.POST.get('description', category.description)
            category.color = request.POST.get('color', category.color)
            category.icon = request.POST.get('icon', category.icon)
            category.is_active = request.POST.get('is_active') == 'on'
            category.order = int(request.POST.get('order', category.order))
            category.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Kategori berhasil diperbarui',
                'data': {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # GET request - return current data
    return JsonResponse({
        'category': {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'description': category.description,
            'color': category.color,
            'icon': category.icon,
            'is_active': category.is_active,
            'order': category.order,
        }
    })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def admin_news_category_delete(request, pk):
    """Delete news category"""
    try:
        category = get_object_or_404(NewsCategory, pk=pk)
        
        # Check if category has news
        if category.news.exists():
            return JsonResponse({
                'success': False,
                'message': 'Kategori tidak dapat dihapus karena masih memiliki berita'
            })
        
        name = category.name
        category.delete()
        return JsonResponse({
            'success': True,
            'message': f'Kategori "{name}" berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# ==================== TAG MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_news_tags_list(request):
    """Admin list view for news tags"""
    tags = NewsTag.objects.annotate(
        news_count=Count('news')
    ).order_by('-news_count')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        tags = tags.filter(name__icontains=search)
    
    # Pagination
    paginator = Paginator(tags, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Manajemen Tag Berita',
        'tags': page_obj,
        'current_filters': {
            'search': search,
        }
    }
    return render(request, 'admin_panel/news/tags.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_news_tag_create(request):
    """Create new news tag"""
    if request.method == 'POST':
        try:
            # Handle form data (not JSON)
            tag = NewsTag.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                color=request.POST.get('color', '#6c757d')
            )
            return JsonResponse({
                'success': True,
                'message': 'Tag berhasil ditambahkan',
                'data': {
                    'id': tag.id,
                    'name': tag.name,
                    'slug': tag.slug
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'message': 'Method not allowed'}, status=405)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_news_tag_update(request, pk):
    """Update news tag"""
    tag = get_object_or_404(NewsTag, pk=pk)
    
    if request.method == 'POST':
        try:
            # Handle form data (not JSON)
            tag.name = request.POST.get('name', tag.name)
            tag.description = request.POST.get('description', tag.description)
            tag.color = request.POST.get('color', tag.color)
            tag.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Tag berhasil diperbarui',
                'data': {
                    'id': tag.id,
                    'name': tag.name,
                    'slug': tag.slug
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    # GET request - return current data
    return JsonResponse({
        'tag': {
            'id': tag.id,
            'name': tag.name,
            'slug': tag.slug,
            'description': tag.description,
            'color': tag.color,
        }
    })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def admin_news_tag_delete(request, pk):
    """Delete news tag"""
    try:
        tag = get_object_or_404(NewsTag, pk=pk)
        name = tag.name
        tag.delete()
        return JsonResponse({
            'success': True,
            'message': f'Tag "{name}" berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# ==================== COMMENT MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_news_comments_list(request):
    """Admin list view for news comments"""
    comments = NewsComment.objects.select_related('news').order_by('-created_at')
    
    # Filter by approval status
    status = request.GET.get('status')
    if status == 'approved':
        comments = comments.filter(status='approved')
    elif status == 'pending':
        comments = comments.filter(status='pending')
    elif status == 'rejected':
        comments = comments.filter(status='rejected')
    elif status == 'spam':
        comments = comments.filter(status='spam')
    
    # Filter by news
    news_id = request.GET.get('news')
    if news_id:
        comments = comments.filter(news_id=news_id)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        comments = comments.filter(
            Q(author_name__icontains=search) |
            Q(author_email__icontains=search) |
            Q(content__icontains=search) |
            Q(news__title__icontains=search)
        )
    
    # Filter by date
    date_from = request.GET.get('date_from')
    if date_from:
        from django.utils.dateparse import parse_date
        try:
            date_obj = parse_date(date_from)
            comments = comments.filter(created_at__date__gte=date_obj)
        except:
            pass
    
    # Pagination
    paginator = Paginator(comments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    news_list = News.objects.filter(comments__isnull=False).distinct()
    
    # Statistics
    total_comments = NewsComment.objects.count()
    approved_comments = NewsComment.objects.filter(status='approved').count()
    pending_comments = NewsComment.objects.filter(status='pending').count()
    rejected_comments = NewsComment.objects.filter(status='rejected').count()
    spam_comments = NewsComment.objects.filter(status='spam').count()
    
    context = {
        'title': 'Manajemen Komentar',
        'comments': page_obj,
        'news_list': news_list,
        'total_comments': total_comments,
        'approved_comments': approved_comments,
        'pending_comments': pending_comments,
        'rejected_comments': rejected_comments,
        'spam_comments': spam_comments,
        'current_filters': {
            'status': status,
            'news': news_id,
            'search': search,
            'date_from': date_from,
        }
    }
    return render(request, 'admin_panel/news/comments.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_news_comment_approve(request, pk):
    """Approve news comment"""
    try:
        comment = get_object_or_404(NewsComment, pk=pk)
        comment.status = 'approved'
        comment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Komentar berhasil disetujui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_news_comment_reject(request, pk):
    """Reject news comment"""
    try:
        comment = get_object_or_404(NewsComment, pk=pk)
        comment.status = 'rejected'
        comment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Komentar berhasil ditolak'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def admin_news_comment_delete(request, pk):
    """Delete news comment"""
    try:
        comment = get_object_or_404(NewsComment, pk=pk)
        comment.delete()
        return JsonResponse({
            'success': True,
            'message': 'Komentar berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_news_comment_spam(request, pk):
    """Mark comment as spam"""
    try:
        comment = get_object_or_404(NewsComment, pk=pk)
        comment.status = 'spam'
        comment.save()
        return JsonResponse({
            'success': True,
            'message': 'Komentar berhasil ditandai sebagai spam'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# ==================== ANNOUNCEMENT MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def admin_announcements_list(request):
    """Admin list view for announcements"""
    announcements = Announcement.objects.order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'published':
        announcements = announcements.filter(status='published')
    elif status == 'draft':
        announcements = announcements.filter(status='draft')
    elif status == 'urgent':
        announcements = announcements.filter(priority='urgent')
    
    # Filter by pinned
    pinned = request.GET.get('pinned')
    if pinned == 'true':
        announcements = announcements.filter(is_pinned=True)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        announcements = announcements.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(announcements, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_announcements = Announcement.objects.count()
    published_announcements = Announcement.objects.filter(status='published').count()
    draft_announcements = Announcement.objects.filter(status='draft').count()
    pinned_announcements = Announcement.objects.filter(is_pinned=True).count()
    
    context = {
        'title': 'Manajemen Pengumuman',
        'announcements': page_obj,
        'total_announcements': total_announcements,
        'published_announcements': published_announcements,
        'draft_announcements': draft_announcements,
        'pinned_announcements': pinned_announcements,
        'current_filters': {
            'status': status,
            'search': search,
            'pinned': pinned,
        }
    }
    return render(request, 'admin_panel/news/announcements.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_announcement_create(request):
    """Create new announcement"""
    if request.method == 'POST':
        try:
            # Handle form data (not JSON)
            # Determine status based on is_active checkbox
            is_active = request.POST.get('is_active') == 'on'
            status = 'published' if is_active else 'draft'
            
            # Handle dates
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone
            
            start_date = request.POST.get('start_date')
            if start_date:
                start_date = parse_datetime(start_date)
            else:
                start_date = timezone.now()
            
            end_date = request.POST.get('end_date')
            if end_date:
                end_date = parse_datetime(end_date)
            else:
                end_date = None
            
            announcement = Announcement.objects.create(
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                announcement_type=request.POST.get('announcement_type', 'info'),
                priority=request.POST.get('priority', 'normal'),
                target_audience=request.POST.get('target_audience', ''),
                location=request.POST.get('location', ''),
                contact_person=request.POST.get('contact_person', ''),
                contact_phone=request.POST.get('contact_phone', ''),
                author=request.user,
                status=status,
                is_pinned=request.POST.get('is_pinned') == 'on',
                is_popup=request.POST.get('is_popup') == 'on',
                start_date=start_date,
                end_date=end_date,
            )
            
            announcement.save()
            
            return redirect('admin_panel:announcement_detail', pk=announcement.pk)
            
        except Exception as e:
            messages.error(request, f'Error creating announcement: {str(e)}')
    
    # GET request - show create form
    from django.utils import timezone
    
    context = {
        'title': 'Tambah Pengumuman Baru',
        'announcement': None,
        'now': timezone.now(),
    }
    return render(request, 'admin_panel/news/announcement_form.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def admin_announcement_detail(request, pk):
    """Detail announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    context = {
        'title': f'Detail Pengumuman - {announcement.title}',
        'announcement': announcement,
    }
    return render(request, 'admin_panel/news/announcement_detail.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_announcement_update(request, pk):
    """Update announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        try:
            # Handle form data (not JSON)
            announcement.title = request.POST.get('title', announcement.title)
            announcement.content = request.POST.get('content', announcement.content)
            announcement.announcement_type = request.POST.get('announcement_type', announcement.announcement_type)
            announcement.priority = request.POST.get('priority', announcement.priority)
            announcement.target_audience = request.POST.get('target_audience', announcement.target_audience)
            announcement.location = request.POST.get('location', announcement.location)
            announcement.contact_person = request.POST.get('contact_person', announcement.contact_person)
            announcement.contact_phone = request.POST.get('contact_phone', announcement.contact_phone)
            
            # Determine status based on is_active checkbox
            is_active = request.POST.get('is_active') == 'on'
            announcement.status = 'published' if is_active else 'draft'
            
            announcement.is_pinned = request.POST.get('is_pinned') == 'on'
            announcement.is_popup = request.POST.get('is_popup') == 'on'
            
            # Handle dates
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone
            
            start_date = request.POST.get('start_date')
            if start_date:
                announcement.start_date = parse_datetime(start_date)
            elif not announcement.start_date:
                announcement.start_date = timezone.now()
            
            end_date = request.POST.get('end_date')
            if end_date:
                announcement.end_date = parse_datetime(end_date)
            elif end_date == '':
                announcement.end_date = None
            
            announcement.save()
            
            return redirect('admin_panel:announcement_detail', pk=announcement.pk)
            
        except Exception as e:
            messages.error(request, f'Error updating announcement: {str(e)}')
    
    # GET request - show edit form
    from django.utils import timezone
    
    context = {
        'title': f'Edit Pengumuman - {announcement.title}',
        'announcement': announcement,
        'now': timezone.now(),
    }
    return render(request, 'admin_panel/news/announcement_form.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def admin_announcement_delete(request, pk):
    """Delete announcement"""
    try:
        announcement = get_object_or_404(Announcement, pk=pk)
        title = announcement.title
        announcement.delete()
        return JsonResponse({
            'success': True,
            'message': f'Pengumuman "{title}" berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_announcement_toggle_status(request, pk):
    """Toggle announcement status"""
    try:
        announcement = get_object_or_404(Announcement, pk=pk)
        
        # Toggle between published and draft
        if announcement.status == 'published':
            announcement.status = 'draft'
        else:
            announcement.status = 'published'
        
        announcement.save()
        
        status = "dipublikasi" if announcement.status == 'published' else "draft"
        return JsonResponse({
            'success': True,
            'message': f'Status pengumuman berhasil diubah menjadi {status}',
            'status': announcement.status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_announcement_toggle_pin(request, pk):
    """Toggle announcement pin status"""
    try:
        announcement = get_object_or_404(Announcement, pk=pk)
        announcement.is_pinned = not announcement.is_pinned
        announcement.save()
        
        status = "dipasang" if announcement.is_pinned else "tidak dipasang"
        return JsonResponse({
            'success': True,
            'message': f'Status pin pengumuman berhasil diubah menjadi {status}',
            'is_pinned': announcement.is_pinned
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# ==================== REPORTS AND ANALYTICS ====================

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def admin_news_reports(request):
    """Generate news reports and analytics"""
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    news_qs = News.objects.all()
    if start_date:
        news_qs = news_qs.filter(created_at__gte=parse_date(start_date))
    if end_date:
        news_qs = news_qs.filter(created_at__lte=parse_date(end_date))
    
    # Basic statistics
    total_news = news_qs.count()
    published_news = news_qs.filter(status='published').count()
    draft_news = news_qs.filter(status='draft').count()
    featured_news = news_qs.filter(is_featured=True).count()
    
    # Category breakdown
    category_breakdown = news_qs.values(
        'category__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Author breakdown
    author_breakdown = news_qs.values(
        'author__username'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    
    # View statistics
    view_stats = NewsView.objects.filter(
        news__in=news_qs
    ).aggregate(
        total_views=Count('id'),
        unique_visitors=Count('ip_address', distinct=True)
    )
    
    # Engagement statistics
    engagement_stats = {
        'total_likes': NewsLike.objects.filter(news__in=news_qs).count(),
        'total_shares': NewsShare.objects.filter(news__in=news_qs).count(),
        'total_comments': NewsComment.objects.filter(news__in=news_qs).count(),
        'approved_comments': NewsComment.objects.filter(
            news__in=news_qs, status='approved'
        ).count(),
    }
    
    # Top performing news
    top_news = news_qs.annotate(
        view_count=Count('view_records'),
        like_count=Count('likes'),
        comment_count=Count('comments')
    ).order_by('-view_count')[:10]
    
    context = {
        'title': 'Laporan Berita',
        'total_news': total_news,
        'published_news': published_news,
        'draft_news': draft_news,
        'featured_news': featured_news,
        'category_breakdown': list(category_breakdown),
        'author_breakdown': list(author_breakdown),
        'view_stats': view_stats,
        'engagement_stats': engagement_stats,
        'top_news': top_news,
        'date_filters': {
            'start_date': start_date,
            'end_date': end_date,
        }
    }
    return render(request, 'admin_panel/news/reports.html', context)

@login_required
@user_passes_test(is_admin)
def admin_news_export(request):
    """Export news data to CSV"""
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    
    news = News.objects.select_related('category', 'author').annotate(
        view_count=Count('view_records'),
        like_count=Count('likes'),
        comment_count=Count('comments')
    )
    
    if start_date:
        news = news.filter(created_at__gte=parse_date(start_date))
    if end_date:
        news = news.filter(created_at__lte=parse_date(end_date))
    if category_id:
        news = news.filter(category_id=category_id)
    if status == 'published':
        news = news.filter(status='published')
    elif status == 'draft':
        news = news.filter(status='draft')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="news_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Judul', 'Kategori', 'Penulis', 'Status',
        'Featured', 'Tanggal Dibuat', 'Views', 'Likes', 'Komentar'
    ])
    
    for item in news:
        writer.writerow([
            item.id,
            item.title,
            item.category.name if item.category else '',
            item.author.username,
            'Published' if item.status == 'published' else 'Draft',
            'Yes' if item.is_featured else 'No',
            item.created_at.strftime('%Y-%m-%d %H:%M'),
            item.view_count,
            item.like_count,
            item.comment_count
        ])
    
    return response

# ==================== BULK OPERATIONS ====================

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_news_bulk_update(request):
    """Bulk update news"""
    try:
        data = json.loads(request.body)
        news_ids = data.get('news_ids', [])
        action = data.get('action')
        
        if not news_ids or not action:
            return JsonResponse({
                'success': False,
                'message': 'ID berita dan aksi harus diisi'
            })
        
        news_items = News.objects.filter(id__in=news_ids)
        updated_count = 0
        
        if action == 'publish':
            updated_count = news_items.update(status='published')
        elif action == 'unpublish':
            updated_count = news_items.update(status='draft')
        elif action == 'feature':
            updated_count = news_items.update(is_featured=True)
        elif action == 'unfeature':
            updated_count = news_items.update(is_featured=False)
        elif action == 'delete':
            updated_count = news_items.count()
            news_items.delete()
        
        action_messages = {
            'publish': 'dipublikasikan',
            'unpublish': 'dibatalkan publikasinya',
            'feature': 'dijadikan featured',
            'unfeature': 'dibatalkan featured-nya',
            'delete': 'dihapus'
        }
        
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} berita berhasil {action_messages.get(action, "diperbarui")}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_tags_bulk_action(request):
    """Bulk action for tags"""
    try:
        data = json.loads(request.body)
        tag_ids = data.get('tag_ids', [])
        action = data.get('action')
        
        if not tag_ids or not action:
            return JsonResponse({
                'success': False,
                'message': 'ID tag dan aksi harus diisi'
            })
        
        tags = NewsTag.objects.filter(id__in=tag_ids)
        updated_count = 0
        
        if action == 'delete':
            updated_count = tags.count()
            tags.delete()
        
        action_messages = {
            'delete': 'dihapus',
        }
        
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} tag berhasil {action_messages.get(action, "diperbarui")}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_announcements_bulk_action(request):
    """Bulk action for announcements"""
    try:
        data = json.loads(request.body)
        announcement_ids = data.get('announcement_ids', [])
        action = data.get('action')
        
        if not announcement_ids or not action:
            return JsonResponse({
                'success': False,
                'message': 'ID pengumuman dan aksi harus diisi'
            })
        
        announcements = Announcement.objects.filter(id__in=announcement_ids)
        updated_count = 0
        
        if action == 'activate':
            updated_count = announcements.update(is_active=True)
        elif action == 'deactivate':
            updated_count = announcements.update(is_active=False)
        elif action == 'pin':
            updated_count = announcements.update(is_pinned=True)
        elif action == 'unpin':
            updated_count = announcements.update(is_pinned=False)
        elif action == 'delete':
            updated_count = announcements.count()
            announcements.delete()
        
        action_messages = {
            'activate': 'diaktifkan',
            'deactivate': 'dinonaktifkan',
            'pin': 'dipasang',
            'unpin': 'dilepas',
            'delete': 'dihapus',
        }
        
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} pengumuman berhasil {action_messages.get(action, "diperbarui")}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_comments_bulk_update(request):
    """Bulk update comments"""
    try:
        data = json.loads(request.body)
        comment_ids = data.get('comment_ids', [])
        action = data.get('action')
        
        if not comment_ids or not action:
            return JsonResponse({
                'success': False,
                'message': 'ID komentar dan aksi harus diisi'
            })
        
        comments = NewsComment.objects.filter(id__in=comment_ids)
        updated_count = 0
        
        if action == 'approve':
            updated_count = comments.update(status='approved')
        elif action == 'reject':
            updated_count = comments.update(status='rejected')
        elif action == 'delete':
            updated_count = comments.count()
            comments.delete()
        
        action_messages = {
            'approve': 'disetujui',
            'reject': 'ditolak',
            'delete': 'dihapus'
        }
        
        return JsonResponse({
            'success': True,
            'message': f'{updated_count} komentar berhasil {action_messages.get(action, "diperbarui")}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

# ==================== API ENDPOINTS ====================

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def admin_api_news_stats(request):
    """API endpoint for news statistics"""
    # Basic counts
    stats = {
        'total_news': News.objects.count(),
        'published_news': News.objects.filter(status='published').count(),
        'draft_news': News.objects.filter(status='draft').count(),
        'featured_news': News.objects.filter(is_featured=True).count(),
        'total_categories': NewsCategory.objects.count(),
        'total_tags': NewsTag.objects.count(),
        'total_comments': NewsComment.objects.count(),
        'pending_comments': NewsComment.objects.filter(status='pending').count(),
    }
    
    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_stats = {
        'new_news': News.objects.filter(created_at__gte=week_ago).count(),
        'new_comments': NewsComment.objects.filter(created_at__gte=week_ago).count(),
        'new_views': NewsView.objects.filter(view_date__gte=week_ago).count(),
    }
    
    # Popular categories
    popular_categories = NewsCategory.objects.annotate(
        news_count=Count('news')
    ).order_by('-news_count')[:5]
    
    popular_categories_data = [{
        'name': cat.name,
        'count': cat.news_count
    } for cat in popular_categories]
    
    return JsonResponse({
        'stats': stats,
        'recent': recent_stats,
        'popular_categories': popular_categories_data,
    })

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def admin_api_news_search(request):
    """API endpoint for news search"""
    query = request.GET.get('q', '')
    limit = int(request.GET.get('limit', 10))
    search_type = request.GET.get('type', 'all')  # all, news, comments
    
    if not query:
        return JsonResponse({'results': []})
    
    results = []
    
    if search_type in ['all', 'news']:
        news = News.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('category', 'author')[:limit//2 if search_type == 'all' else limit]
        
        for item in news:
            results.append({
                'type': 'news',
                'id': item.id,
                'title': item.title,
                'category': item.category.name if item.category else '',
                'author': item.author.username,
                'status': item.status,
                'created_at': item.created_at.isoformat(),
            })
    
    if search_type in ['all', 'comments']:
        comments = NewsComment.objects.filter(
            Q(name__icontains=query) |
            Q(comment__icontains=query) |
            Q(news__title__icontains=query)
        ).select_related('news')[:limit//2 if search_type == 'all' else limit]
        
        for comment in comments:
            results.append({
                'type': 'comment',
                'id': comment.id,
                'name': comment.name,
                'comment': comment.comment[:100] + '...' if len(comment.comment) > 100 else comment.comment,
                'news_title': comment.news.title,
                'status': comment.status,
                'created_at': comment.created_at.isoformat(),
            })
    
    return JsonResponse({'results': results})

# ==================== HELPER VIEWS ====================

@login_required
@user_passes_test(is_admin)
def admin_news_duplicate(request, pk):
    """Duplicate existing news"""
    try:
        original_news = get_object_or_404(News, pk=pk)
        
        # Generate unique slug
        base_slug = f"{original_news.slug}-copy-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        counter = 1
        slug = base_slug
        while News.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create a copy of the news with all fields
        duplicated_news = News.objects.create(
            title=f"{original_news.title} (Copy)",
            slug=slug,
            content=original_news.content,
            excerpt=original_news.excerpt,
            category=original_news.category,
            author=request.user,
            status='draft',  # Always set as draft
            priority=original_news.priority,
            is_featured=False,  # Always set as not featured
            is_breaking=False,  # Always set as not breaking
            meta_title=original_news.meta_title,
            meta_description=original_news.meta_description,
            allow_comments=original_news.allow_comments,
            youtube_url=original_news.youtube_url,
            # Don't copy featured_image to avoid file conflicts
            # Don't copy video_file to avoid file conflicts
        )
        
        # Copy tags
        duplicated_news.tags.set(original_news.tags.all())
        
        # Copy images if any (create new image records)
        for image in original_news.images.all():
            duplicated_news.images.create(
                image=image.image,
                caption=image.caption,
                alt_text=image.alt_text,
                is_featured=image.is_featured,
                order=image.order
            )
        
        messages.success(request, f'Berita "{original_news.title}" berhasil diduplikasi.')
        return redirect('admin_panel:news_edit', pk=duplicated_news.pk)
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan saat menduplikasi berita: {str(e)}')
        return redirect('admin_panel:news_list')

@login_required
@user_passes_test(is_admin)
def admin_news_generate_slug(request):
    """Generate slug from title"""
    title = request.GET.get('title', '')
    if not title:
        return JsonResponse({'slug': ''})
    
    # Simple slug generation
    import re
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')
    
    # Check if slug exists and make it unique
    original_slug = slug
    counter = 1
    while News.objects.filter(slug=slug).exists():
        slug = f"{original_slug}-{counter}"
        counter += 1
    
    return JsonResponse({'slug': slug})

@login_required
@user_passes_test(is_admin)
def admin_news_preview(request, pk):
    """Preview news before publishing"""
    news = get_object_or_404(News, pk=pk)
    
    context = {
        'news': news,
        'preview_mode': True,
    }
    return render(request, 'public/news/news_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_news_analytics_detail(request, pk):
    """Detailed analytics for specific news"""
    news = get_object_or_404(News, pk=pk)
    
    # View analytics
    views = NewsView.objects.filter(news=news)
    total_views = views.count()
    unique_views = views.values('ip_address').distinct().count()
    
    # Device breakdown
    device_breakdown = views.values('device_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Daily views (last 30 days)
    daily_views = views.filter(
        view_date__gte=timezone.now() - timedelta(days=30)
    ).annotate(
        date=TruncDate('view_date')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Engagement metrics
    likes = NewsLike.objects.filter(news=news).count()
    shares = NewsShare.objects.filter(news=news).count()
    comments = NewsComment.objects.filter(news=news).count()
    approved_comments = NewsComment.objects.filter(news=news, status='approved').count()
    
    # Share platform breakdown
    share_breakdown = NewsShare.objects.filter(news=news).values('platform').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'title': f'Analytics - {news.title}',
        'news': news,
        'total_views': total_views,
        'unique_views': unique_views,
        'device_breakdown': list(device_breakdown),
        'daily_views': list(daily_views),
        'likes': likes,
        'shares': shares,
        'comments': comments,
        'approved_comments': approved_comments,
        'share_breakdown': list(share_breakdown),
    }
    return render(request, 'admin_panel/news/analytics_detail.html', context)