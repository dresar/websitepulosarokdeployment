from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from .models import (
    TourismLocation, TourismCategory, TourismGallery, TourismReview,
    TourismRating, TourismEvent, TourismPackage, TourismFAQ,
    TourismPackageGallery, TourismDashboard, TourismSettings
)
from .forms import (
    TourismLocationForm, TourismCategoryForm, TourismReviewForm,
    TourismRatingForm, TourismEventForm, TourismPackageForm, AnonymousReviewForm
)

# Helper function to check if user is staff
def is_staff(user):
    return user.is_authenticated and user.is_staff

# PUBLIC VIEWS
def tourism_dashboard(request):
    """Dashboard utama wisata dengan statistik dan featured content"""
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Get dashboard configuration
    dashboard_config = TourismDashboard.objects.filter(is_active=True).first()
    
    # If no dashboard config exists, create a default one
    if not dashboard_config:
        dashboard_config = TourismDashboard.objects.create(
            title="Wisata Desa Pulosarok",
            description="Jelajahi keindahan alam, kekayaan budaya, dan kelezatan kuliner yang menanti Anda di setiap sudut desa kami."
        )
    
    # Get hero media from dashboard config
    hero_video = dashboard_config.hero_video
    hero_youtube = dashboard_config.hero_youtube
    hero_image = dashboard_config.hero_background
    
    # Use dynamic limits from settings
    featured_locations_limit = settings.featured_locations_limit
    categories_limit = settings.categories_limit
    upcoming_events_limit = settings.upcoming_events_limit
    featured_packages_limit = settings.featured_packages_limit
    
    context = {
        'dashboard_config': dashboard_config,
        'featured_locations': TourismLocation.objects.filter(
            status='published', featured=True, is_active=True
        )[:featured_locations_limit],
        'categories': TourismCategory.objects.filter(is_active=True)[:categories_limit],
        'upcoming_events': TourismEvent.objects.filter(
            start_date__gte=timezone.now(), is_active=True
        )[:upcoming_events_limit],
        'featured_packages': TourismPackage.objects.filter(
            is_featured=True, is_active=True
        )[:featured_packages_limit],
        'total_locations': TourismLocation.objects.filter(
            status='published', is_active=True
        ).count(),
        'total_categories': TourismCategory.objects.filter(is_active=True).count(),
        'total_events': TourismEvent.objects.filter(is_active=True).count(),
        'hero_video': hero_video,
        'hero_youtube': hero_youtube,
        'hero_image': hero_image,
    }
    return render(request, 'public/tourism/dashboard.html', context)

def tourism_list(request):
    """Daftar semua lokasi wisata dengan filter dan pencarian"""
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    locations = TourismLocation.objects.filter(status='published', is_active=True)
    
    # Filter berdasarkan kategori
    category_id = request.GET.get('category')
    if category_id:
        locations = locations.filter(category_id=category_id)
    
    # Filter berdasarkan jenis wisata
    location_type = request.GET.get('type')
    if location_type:
        locations = locations.filter(location_type=location_type)
    
    # Pencarian
    search = request.GET.get('q')  # Template uses 'q' parameter
    if search:
        locations = locations.filter(
            Q(title__icontains=search) |
            Q(short_description__icontains=search) |
            Q(address__icontains=search)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'rating':
        locations = locations.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')
    elif sort_by == 'name':
        locations = locations.order_by('title')
    else:
        locations = locations.order_by(sort_by)
    
    # Pagination with dynamic settings
    paginator = Paginator(locations, settings.locations_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'locations': page_obj.object_list,
        'total_locations': locations.count(),
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'categories': TourismCategory.objects.filter(is_active=True),
        'location_types': TourismLocation.LOCATION_TYPE_CHOICES,
        'current_category': category_id,
        'current_type': location_type,
        'current_search': search,
        'current_sort': sort_by,
    }
    return render(request, 'public/tourism/location_list.html', context)

def tourism_detail(request, slug):
    """Detail lokasi wisata"""
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    try:
        location = TourismLocation.objects.get(slug=slug, is_active=True)
        if location.status != 'published':
            from django.http import Http404
            raise Http404("Location not published")
    except TourismLocation.DoesNotExist:
        from django.http import Http404
        raise Http404("Location not found")
    
    
    # Gallery
    gallery = location.gallery.filter(is_active=True).order_by('order')
    
    # Reviews with dynamic limit
    reviews = location.reviews.filter(is_approved=True).order_by('-created_at')[:settings.reviews_per_page]
    
    # Events with dynamic limit
    upcoming_events = location.events.filter(
        start_date__gte=timezone.now(),
        is_active=True
    )[:settings.upcoming_events_limit]
    
    # Packages with dynamic limit
    packages = location.packages.filter(is_active=True)[:settings.related_packages_limit]
    
    # FAQs
    faqs = location.faqs.filter(is_active=True).order_by('order')
    
    # Related locations with dynamic limit
    related_locations = TourismLocation.objects.filter(
        category=location.category,
        status='published',
        is_active=True
    ).exclude(id=location.id)[:settings.related_locations_limit]
    
    # Calculate rating breakdown dynamically
    rating_breakdown = []
    for i in range(5, 0, -1):
        count = location.reviews.filter(rating=i, is_approved=True).count()
        total_reviews = location.reviews.filter(is_approved=True).count()
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_breakdown.append({
            'stars': i,
            'count': count,
            'percentage': percentage
        })
    
    context = {
        'location': location,
        'galleries': gallery,  # Template expects 'galleries'
        'reviews': reviews,
        'upcoming_events': upcoming_events,
        'related_packages': packages,  # Template expects 'related_packages'
        'faqs': faqs,
        'related_locations': related_locations,
        'rating_breakdown': rating_breakdown,
        'review_form': AnonymousReviewForm(),  # Use anonymous form for now
        'rating_form': TourismRatingForm(),
    }
    return render(request, 'public/tourism/location_detail.html', context)

def category_list(request):
    """Daftar kategori wisata"""
    categories = TourismCategory.objects.filter(is_active=True).annotate(
        total_locations=Count('tourismlocation')
    )
    
    context = {
        'categories': categories,
    }
    return render(request, 'public/tourism/category_list.html', context)

def category_detail(request, category_id):
    """Detail kategori dengan lokasi wisata terkait"""
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    category = get_object_or_404(TourismCategory, id=category_id, is_active=True)
    
    locations = TourismLocation.objects.filter(
        category=category,
        status='published',
        is_active=True
    )
    
    # Pagination with dynamic settings
    paginator = Paginator(locations, settings.locations_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'public/tourism/category_detail.html', context)

def category_detail_by_slug(request, slug):
    """Detail kategori dengan lokasi wisata terkait berdasarkan slug"""
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    category = get_object_or_404(TourismCategory, slug=slug, is_active=True)
    
    locations = TourismLocation.objects.filter(
        category=category,
        status='published',
        is_active=True
    )
    
    # Pagination with dynamic settings
    paginator = Paginator(locations, settings.locations_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'public/tourism/category_detail.html', context)

def event_list(request):
    """Daftar event wisata"""
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    events = TourismEvent.objects.filter(is_active=True)
    
    # Filter berdasarkan jenis event
    event_type = request.GET.get('type')
    if event_type:
        events = events.filter(event_type=event_type)
    
    # Filter berdasarkan waktu menggunakan dynamic settings
    time_filter = request.GET.get('time', 'upcoming')
    if time_filter and settings.time_filters:
        for time_config in settings.time_filters:
            if time_config.get('value') == time_filter:
                if time_filter == 'upcoming':
                    events = events.filter(start_date__gte=timezone.now())
                elif time_filter == 'ongoing':
                    events = events.filter(
                        start_date__lte=timezone.now(),
                        end_date__gte=timezone.now()
                    )
                elif time_filter == 'past':
                    events = events.filter(end_date__lt=timezone.now())
                break
    else:
        # Fallback to default behavior
        if time_filter == 'upcoming':
            events = events.filter(start_date__gte=timezone.now())
        elif time_filter == 'past':
            events = events.filter(end_date__lt=timezone.now())
    
    events = events.order_by('start_date')
    
    # Pagination with dynamic settings
    paginator = Paginator(events, settings.events_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'event_types': TourismEvent.EVENT_TYPE_CHOICES,
        'current_type': event_type,
        'current_time': time_filter,
    }
    return render(request, 'public/tourism/event_list.html', context)

def event_detail(request, event_id):
    """Detail event wisata"""
    event = get_object_or_404(TourismEvent, id=event_id, is_active=True)
    
    context = {
        'event': event,
    }
    return render(request, 'public/tourism/event_detail.html', context)

def event_detail_by_slug(request, slug):
    """Detail event wisata berdasarkan slug"""
    event = get_object_or_404(TourismEvent, slug=slug, is_active=True)
    
    context = {
        'event': event,
    }
    return render(request, 'public/tourism/event_detail.html', context)

def package_list(request):
    """Daftar paket wisata"""
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    packages = TourismPackage.objects.filter(is_active=True)
    
    # Filter berdasarkan jenis paket
    package_type = request.GET.get('type')
    if package_type:
        packages = packages.filter(package_type=package_type)
    
    # Filter berdasarkan harga menggunakan dynamic settings
    price_range = request.GET.get('price_range')
    if price_range and settings.price_ranges:
        for price_config in settings.price_ranges:
            if price_config.get('label') == price_range:
                min_price = price_config.get('min', 0)
                max_price = price_config.get('max')
                if max_price is None:
                    packages = packages.filter(price__gte=min_price)
                else:
                    packages = packages.filter(price__gte=min_price, price__lt=max_price)
                break
    
    # Filter berdasarkan durasi menggunakan dynamic settings
    duration = request.GET.get('duration')
    if duration and settings.duration_filters:
        for duration_config in settings.duration_filters:
            if duration_config.get('value') == duration:
                duration_value = duration_config.get('value')
                packages = packages.filter(duration__icontains=duration_value)
                break
    
    # Pencarian
    search = request.GET.get('q')
    if search:
        packages = packages.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'price')
    if sort_by == 'name':
        packages = packages.order_by('title')
    elif sort_by == '-name':
        packages = packages.order_by('-title')
    elif sort_by == 'price':
        packages = packages.order_by('price')
    elif sort_by == '-price':
        packages = packages.order_by('-price')
    else:
        packages = packages.order_by(sort_by)
    
    # Pagination with dynamic settings
    paginator = Paginator(packages, settings.packages_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics with real data
    total_packages = packages.count()
    popular_packages = packages.filter(is_featured=True).count()
    
    # Calculate real average rating from reviews
    if settings.enable_real_statistics:
        from django.db.models import Avg
        average_rating = TourismReview.objects.filter(
            is_approved=True
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    else:
        average_rating = 4.5  # Fallback placeholder
    
    # Calculate real total bookings (if booking system exists)
    if settings.enable_real_statistics:
        # This would need a booking model to be implemented
        total_bookings = 0  # Placeholder until booking system is implemented
    else:
        total_bookings = 150  # Fallback placeholder
    
    context = {
        'packages': page_obj.object_list,
        'total_packages': total_packages,
        'popular_packages': popular_packages,
        'average_rating': average_rating,
        'total_bookings': total_bookings,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'package_types': TourismPackage.PACKAGE_TYPE_CHOICES,
        'current_type': package_type,
        'current_price_range': price_range,
        'current_duration': duration,
        'current_search': search,
        'current_sort': sort_by,
    }
    return render(request, 'public/tourism/package_list.html', context)

def package_detail(request, package_id):
    """Detail paket wisata"""
    package = get_object_or_404(TourismPackage, id=package_id, is_active=True)
    
    # Gallery
    gallery = package.gallery.filter(is_active=True).order_by('order')
    
    # Related packages
    related_packages = TourismPackage.objects.filter(
        tourism_location=package.tourism_location,
        is_active=True
    ).exclude(id=package.id)[:4]
    
    context = {
        'package': package,
        'gallery': gallery,
        'related_packages': related_packages,
    }
    return render(request, 'public/tourism/package_detail.html', context)

def package_detail_by_slug(request, slug):
    """Detail paket wisata berdasarkan slug"""
    package = get_object_or_404(TourismPackage, slug=slug, is_active=True)
    
    # Gallery
    gallery = package.gallery.filter(is_active=True).order_by('order')
    
    # Related packages
    related_packages = TourismPackage.objects.filter(
        tourism_location=package.tourism_location,
        is_active=True
    ).exclude(id=package.id)[:4]
    
    # Parse itinerary from JSON string
    import json
    try:
        itinerary_list = json.loads(package.itinerary) if package.itinerary else []
    except:
        itinerary_list = []
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Calculate real rating breakdown
    if settings.enable_real_statistics:
        rating_breakdown = []
        total_reviews = TourismReview.objects.filter(
            tourism_location=package.tourism_location,
            is_approved=True
        ).count()
        
        for i in range(5, 0, -1):
            count = TourismReview.objects.filter(
                tourism_location=package.tourism_location,
                rating=i,
                is_approved=True
            ).count()
            percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
            rating_breakdown.append({
                'stars': i,
                'count': count,
                'percentage': percentage
            })
    else:
        # Fallback placeholder data
        rating_breakdown = [
            {'stars': 5, 'count': 12, 'percentage': 60},
            {'stars': 4, 'count': 6, 'percentage': 30},
            {'stars': 3, 'count': 2, 'percentage': 10},
            {'stars': 2, 'count': 0, 'percentage': 0},
            {'stars': 1, 'count': 0, 'percentage': 0},
        ]
    
    # Add computed fields to package object
    package.main_image = package.image  # Map image to main_image
    
    # Calculate real average rating and total reviews
    if settings.enable_real_statistics:
        from django.db.models import Avg
        package.average_rating = TourismReview.objects.filter(
            tourism_location=package.tourism_location,
            is_approved=True
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        package.total_reviews = TourismReview.objects.filter(
            tourism_location=package.tourism_location,
            is_approved=True
        ).count()
    else:
        package.average_rating = 4.5  # Fallback placeholder
        package.total_reviews = 20  # Fallback placeholder
    package.rating_breakdown = rating_breakdown
    package.itinerary_list = itinerary_list
    package.includes_accommodation = 'penginapan' in package.includes.lower() if package.includes else False
    package.includes_meals = 'makan' in package.includes.lower() if package.includes else False
    package.includes_transport = 'transport' in package.includes.lower() if package.includes else False
    package.includes_guide = 'pemandu' in package.includes.lower() if package.includes else False
    package.difficulty_level = 'easy'  # Placeholder
    package.terms_conditions = package.excludes if package.excludes else 'Syarat dan ketentuan berlaku.'
    # Generate WhatsApp booking URL using dynamic settings
    if package.whatsapp:
        whatsapp_number = settings.whatsapp_number or package.whatsapp
        message_template = settings.whatsapp_message_template.format(item_name=package.title)
        package.booking_url = f"https://wa.me/{whatsapp_number}?text={message_template}"
    else:
        package.booking_url = None
    
    context = {
        'package': package,
        'galleries': gallery,  # Template expects 'galleries'
        'related_packages': related_packages,
    }
    return render(request, 'public/tourism/package_detail.html', context)

def search_tourism(request):
    """Pencarian global untuk wisata"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Search locations
        locations = TourismLocation.objects.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(address__icontains=query),
            status='published',
            is_active=True
        )[:10]
        
        # Search events
        events = TourismEvent.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )[:5]
        
        # Search packages
        packages = TourismPackage.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )[:5]
        
        results = {
            'locations': locations,
            'events': events,
            'packages': packages,
            'query': query,
        }
    
    context = {
        'results': results,
        'query': query,
    }
    return render(request, 'public/tourism/search.html', context)

# USER INTERACTION VIEWS
@login_required
@require_POST
def submit_review(request, location_id):
    """Submit review untuk lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    
    # Check if user already reviewed this location
    existing_review = TourismReview.objects.filter(
        tourism_location=location,
        user=request.user
    ).first()
    
    if existing_review:
        messages.error(request, 'Anda sudah memberikan review untuk lokasi ini.')
        return redirect('tourism:location_detail', slug=location.slug)
    
    form = TourismReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.tourism_location = location
        review.user = request.user
        review.save()
        messages.success(request, 'Review Anda berhasil dikirim dan menunggu persetujuan.')
    else:
        messages.error(request, 'Terjadi kesalahan saat mengirim review.')
    
    return redirect('tourism:location_detail', slug=location.slug)

def add_review(request, slug):
    """Add review untuk lokasi wisata berdasarkan slug"""
    location = get_object_or_404(TourismLocation, slug=slug, is_active=True)
    
    if request.method == 'POST':
        form = AnonymousReviewForm(request.POST)
        if form.is_valid():
            # Create review manually since we're using anonymous form
            # For now, create with user=None until visitor_name field is added to DB
            review = TourismReview.objects.create(
                tourism_location=location,
                user=None,  # Anonymous review
                rating=int(form.cleaned_data['rating']),
                title=f"Review dari {form.cleaned_data['visitor_name']}",
                comment=form.cleaned_data['comment'],
                is_approved=False  # Require approval for anonymous reviews
            )
            messages.success(request, 'Review Anda berhasil dikirim dan menunggu persetujuan.')
            return redirect('tourism:location_detail', slug=location.slug)
        else:
            messages.error(request, 'Terjadi kesalahan saat mengirim review.')
    else:
        form = AnonymousReviewForm()
    
    context = {
        'location': location,
        'form': form,
    }
    return render(request, 'public/tourism/add_review.html', context)

@login_required
@require_POST
def submit_rating(request, location_id):
    """Submit rating untuk lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    
    # Check if user already rated this location
    rating, created = TourismRating.objects.get_or_create(
        tourism_location=location,
        user=request.user,
        defaults={
            'rating': request.POST.get('rating', 5),
            'cleanliness': request.POST.get('cleanliness'),
            'accessibility': request.POST.get('accessibility'),
            'facilities': request.POST.get('facilities'),
            'service': request.POST.get('service'),
            'value': request.POST.get('value'),
        }
    )
    
    if not created:
        # Update existing rating
        rating.rating = request.POST.get('rating', rating.rating)
        rating.cleanliness = request.POST.get('cleanliness', rating.cleanliness)
        rating.accessibility = request.POST.get('accessibility', rating.accessibility)
        rating.facilities = request.POST.get('facilities', rating.facilities)
        rating.service = request.POST.get('service', rating.service)
        rating.value = request.POST.get('value', rating.value)
        rating.save()
        messages.success(request, 'Rating Anda berhasil diperbarui.')
    else:
        messages.success(request, 'Rating Anda berhasil dikirim.')
    
    return redirect('tourism:location_detail', slug=location.slug)

# ADMIN VIEWS
@user_passes_test(is_staff)
def admin_dashboard(request):
    """Dashboard admin wisata"""
    context = {
        'total_locations': TourismLocation.objects.count(),
        'published_locations': TourismLocation.objects.filter(status='published').count(),
        'draft_locations': TourismLocation.objects.filter(status='draft').count(),
        'total_categories': TourismCategory.objects.count(),
        'total_events': TourismEvent.objects.count(),
        'total_packages': TourismPackage.objects.count(),
        'total_reviews': TourismReview.objects.count(),
        'pending_reviews': TourismReview.objects.filter(is_approved=False).count(),
        'recent_locations': TourismLocation.objects.order_by('-created_at')[:5],
        'recent_reviews': TourismReview.objects.order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/tourism/dashboard.html', context)

@user_passes_test(is_staff)
def admin_location_list(request):
    """Daftar lokasi wisata untuk admin"""
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    locations = TourismLocation.objects.all()
    
    # Filter berdasarkan status
    status = request.GET.get('status')
    if status:
        locations = locations.filter(status=status)
    
    # Pencarian
    search = request.GET.get('search')
    if search:
        locations = locations.filter(
            Q(title__icontains=search) |
            Q(short_description__icontains=search)
        )
    
    locations = locations.order_by('-created_at')
    
    # Pagination with dynamic settings
    paginator = Paginator(locations, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': TourismLocation.STATUS_CHOICES,
        'current_status': status,
        'current_search': search,
    }
    return render(request, 'admin_panel/tourism/location_list.html', context)

@user_passes_test(is_staff)
def admin_location_create(request):
    """Buat lokasi wisata baru"""
    if request.method == 'POST':
        form = TourismLocationForm(request.POST, request.FILES)
        if form.is_valid():
            location = form.save(commit=False)
            location.created_by = request.user
            location.updated_by = request.user
            if location.status == 'published':
                location.published_at = timezone.now()
            location.save()
            messages.success(request, 'Lokasi wisata berhasil dibuat.')
            return redirect('tourism:admin_location_detail', location_id=location.id)
    else:
        form = TourismLocationForm()
    
    context = {
        'form': form,
        'title': 'Tambah Lokasi Wisata',
    }
    return render(request, 'admin_panel/tourism/location_form.html', context)

@user_passes_test(is_staff)
def admin_location_detail(request, location_id):
    """Detail lokasi wisata untuk admin"""
    location = get_object_or_404(TourismLocation, id=location_id)
    
    context = {
        'location': location,
        'gallery': location.gallery.all(),
        'reviews': location.reviews.order_by('-created_at')[:10],
        'events': location.events.order_by('-start_date')[:5],
        'packages': location.packages.all(),
        'faqs': location.faqs.order_by('order'),
    }
    return render(request, 'admin_panel/tourism/location_detail.html', context)

@user_passes_test(is_staff)
def admin_location_edit(request, location_id):
    """Edit lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    
    if request.method == 'POST':
        form = TourismLocationForm(request.POST, request.FILES, instance=location)
        if form.is_valid():
            location = form.save(commit=False)
            location.updated_by = request.user
            if location.status == 'published' and not location.published_at:
                location.published_at = timezone.now()
            location.save()
            messages.success(request, 'Lokasi wisata berhasil diperbarui.')
            return redirect('tourism:admin_location_detail', location_id=location.id)
    else:
        form = TourismLocationForm(instance=location)
    
    context = {
        'form': form,
        'location': location,
        'title': f'Edit {location.title}',
    }
    return render(request, 'admin_panel/tourism/location_form.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_location_delete(request, location_id):
    """Hapus lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    location.delete()
    messages.success(request, f'Lokasi wisata "{location.title}" berhasil dihapus.')
    return redirect('tourism:admin_location_list')

# ADMIN CATEGORY VIEWS
@user_passes_test(is_staff)
def admin_category_list(request):
    """Daftar kategori wisata untuk admin"""
    categories = TourismCategory.objects.all().annotate(
        total_locations=Count('tourismlocation')
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'public/tourism/admin/category_list.html', context)

@user_passes_test(is_staff)
def admin_category_create(request):
    """Buat kategori wisata baru"""
    if request.method == 'POST':
        form = TourismCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori wisata berhasil dibuat.')
            return redirect('tourism:admin_category_list')
    else:
        form = TourismCategoryForm()
    
    context = {
        'form': form,
        'title': 'Tambah Kategori Wisata',
    }
    return render(request, 'public/tourism/admin/category_form.html', context)

@user_passes_test(is_staff)
def admin_category_edit(request, category_id):
    """Edit kategori wisata"""
    category = get_object_or_404(TourismCategory, id=category_id)
    
    if request.method == 'POST':
        form = TourismCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori wisata berhasil diperbarui.')
            return redirect('tourism:admin_category_list')
    else:
        form = TourismCategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': f'Edit {category.name}',
    }
    return render(request, 'public/tourism/admin/category_form.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_category_delete(request, category_id):
    """Hapus kategori wisata"""
    category = get_object_or_404(TourismCategory, id=category_id)
    category.delete()
    messages.success(request, f'Kategori wisata "{category.name}" berhasil dihapus.')
    return redirect('tourism:admin_category_list')

# ADMIN PACKAGE VIEWS
@user_passes_test(is_staff)
def admin_package_list(request):
    """Daftar paket wisata untuk admin"""
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    packages = TourismPackage.objects.all().order_by('-created_at')
    
    # Pagination with dynamic settings
    paginator = Paginator(packages, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin_panel/tourism/package_list.html', context)

@user_passes_test(is_staff)
def admin_package_create(request):
    """Buat paket wisata baru"""
    if request.method == 'POST':
        form = TourismPackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paket wisata berhasil dibuat.')
            return redirect('tourism:admin_package_list')
    else:
        form = TourismPackageForm()
    
    context = {
        'form': form,
        'title': 'Tambah Paket Wisata',
    }
    return render(request, 'admin_panel/tourism/package_form.html', context)

@user_passes_test(is_staff)
def admin_package_detail(request, package_id):
    """Detail paket wisata untuk admin"""
    package = get_object_or_404(TourismPackage, id=package_id)
    
    context = {
        'package': package,
        'gallery': package.gallery.all(),
    }
    return render(request, 'admin_panel/tourism/package_detail.html', context)

@user_passes_test(is_staff)
def admin_package_edit(request, package_id):
    """Edit paket wisata"""
    package = get_object_or_404(TourismPackage, id=package_id)
    
    if request.method == 'POST':
        form = TourismPackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paket wisata berhasil diperbarui.')
            return redirect('tourism:admin_package_detail', package_id=package.id)
    else:
        form = TourismPackageForm(instance=package)
    
    context = {
        'form': form,
        'package': package,
        'title': f'Edit {package.title}',
    }
    return render(request, 'admin_panel/tourism/package_form.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_package_delete(request, package_id):
    """Hapus paket wisata"""
    package = get_object_or_404(TourismPackage, id=package_id)
    package.delete()
    messages.success(request, f'Paket wisata "{package.title}" berhasil dihapus.')
    return redirect('tourism:admin_package_list')

# ADMIN EVENT VIEWS
@user_passes_test(is_staff)
def admin_event_list(request):
    """Daftar event wisata untuk admin"""
    events = TourismEvent.objects.all().order_by('-start_date')
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Filter berdasarkan status menggunakan dynamic settings
    status = request.GET.get('status')
    if status and settings.time_filters:
        for time_config in settings.time_filters:
            if time_config.get('value') == status:
                if status == 'upcoming':
                    events = events.filter(start_date__gte=timezone.now())
                elif status == 'ongoing':
                    events = events.filter(
                        start_date__lte=timezone.now(),
                        end_date__gte=timezone.now()
                    )
                elif status == 'past':
                    events = events.filter(end_date__lt=timezone.now())
                break
    elif status:
        # Fallback to default behavior
        if status == 'upcoming':
            events = events.filter(start_date__gte=timezone.now())
        elif status == 'ongoing':
            events = events.filter(
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )
        elif status == 'past':
            events = events.filter(end_date__lt=timezone.now())
    
    # Pencarian
    search = request.GET.get('search')
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Pagination with dynamic settings
    paginator = Paginator(events, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_status': status,
        'current_search': search,
    }
    return render(request, 'public/tourism/admin/event_list.html', context)

@user_passes_test(is_staff)
def admin_event_create(request):
    """Buat event wisata baru"""
    if request.method == 'POST':
        form = TourismEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event wisata berhasil dibuat.')
            return redirect('tourism:admin_event_detail', event_id=event.id)
    else:
        form = TourismEventForm()
    
    context = {
        'form': form,
        'title': 'Tambah Event Wisata',
    }
    return render(request, 'public/tourism/admin/event_form.html', context)

@user_passes_test(is_staff)
def admin_event_detail(request, event_id):
    """Detail event wisata untuk admin"""
    event = get_object_or_404(TourismEvent, id=event_id)
    
    context = {
        'event': event,
    }
    return render(request, 'public/tourism/admin/event_detail.html', context)

@user_passes_test(is_staff)
def admin_event_edit(request, event_id):
    """Edit event wisata"""
    event = get_object_or_404(TourismEvent, id=event_id)
    
    if request.method == 'POST':
        form = TourismEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event wisata berhasil diperbarui.')
            return redirect('tourism:admin_event_detail', event_id=event.id)
    else:
        form = TourismEventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'title': f'Edit {event.title}',
    }
    return render(request, 'public/tourism/admin/event_form.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_event_delete(request, event_id):
    """Hapus event wisata"""
    event = get_object_or_404(TourismEvent, id=event_id)
    event.delete()
    messages.success(request, f'Event wisata "{event.title}" berhasil dihapus.')
    return redirect('tourism:admin_event_list')

# ADMIN REVIEW MANAGEMENT VIEWS
@user_passes_test(is_staff)
def admin_review_list(request):
    """Daftar ulasan untuk admin"""
    reviews = TourismReview.objects.all().order_by('-created_at')
    
    # Filter berdasarkan status approval
    status = request.GET.get('status')
    if status:
        if status == 'approved':
            reviews = reviews.filter(is_approved=True)
        elif status == 'pending':
            reviews = reviews.filter(is_approved=False)
    
    # Filter berdasarkan lokasi
    location_id = request.GET.get('location')
    if location_id:
        reviews = reviews.filter(location_id=location_id)
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Pagination with dynamic settings
    paginator = Paginator(reviews, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_status': status,
        'current_location': location_id,
        'locations': TourismLocation.objects.filter(status='published'),
    }
    return render(request, 'public/tourism/admin/review_list.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_review_approve(request, review_id):
    """Approve ulasan"""
    review = get_object_or_404(TourismReview, id=review_id)
    review.is_approved = True
    review.save()
    messages.success(request, f'Ulasan dari {review.user.username} berhasil disetujui.')
    return redirect('tourism:admin_review_list')

@user_passes_test(is_staff)
@require_POST
def admin_review_reject(request, review_id):
    """Reject ulasan"""
    review = get_object_or_404(TourismReview, id=review_id)
    review.is_approved = False
    review.save()
    messages.success(request, f'Ulasan dari {review.user.username} berhasil ditolak.')
    return redirect('tourism:admin_review_list')

@user_passes_test(is_staff)
@require_POST
def admin_review_delete(request, review_id):
    """Hapus ulasan"""
    review = get_object_or_404(TourismReview, id=review_id)
    username = review.user.username
    review.delete()
    messages.success(request, f'Ulasan dari {username} berhasil dihapus!')
    return redirect('tourism:admin_review_list')


def tourism_detail_by_id(request, location_id):
    """Redirect from ID-based URL to slug-based URL"""
    try:
        location = TourismLocation.objects.get(id=location_id, is_active=True)
        if location.status == 'published':
            return redirect('tourism:location_detail', slug=location.slug)
        else:
            from django.http import Http404
            raise Http404("Location not published")
    except TourismLocation.DoesNotExist:
        from django.http import Http404
        raise Http404("Location not found")

def debug_tourism(request):
    """Debug view to check tourism data"""
    locations = TourismLocation.objects.all()[:10]
    context = {
        'locations': locations,
        'total_locations': TourismLocation.objects.count(),
        'published_locations': TourismLocation.objects.filter(status='published', is_active=True).count(),
    }
    return render(request, 'public/tourism/debug.html', context)

@ensure_csrf_cookie
def get_csrf_token(request):
    """
    API endpoint untuk mendapatkan CSRF token
    """
    csrf_token = get_token(request)
    return JsonResponse({
        'success': True,
        'csrf_token': csrf_token,
        'message': 'CSRF token berhasil diambil'
    })

# ============= ADMIN PANEL INTEGRATION =============

# Admin Dashboard Views
@user_passes_test(is_staff)
def admin_panel_dashboard(request):
    """Dashboard admin panel untuk tourism"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    # Statistics
    total_locations = TourismLocation.objects.count()
    active_locations = TourismLocation.objects.filter(is_active=True).count()
    total_categories = TourismCategory.objects.count()
    total_packages = TourismPackage.objects.count()
    total_events = TourismEvent.objects.count()
    total_reviews = TourismReview.objects.count()
    pending_reviews = TourismReview.objects.filter(is_approved=False).count()
    
    # Recent activities
    recent_locations = TourismLocation.objects.order_by('-created_at')[:5]
    recent_reviews = TourismReview.objects.order_by('-created_at')[:5]
    recent_events = TourismEvent.objects.order_by('-created_at')[:5]
    
    # Monthly statistics
    current_month = datetime.now().replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    current_month_locations = TourismLocation.objects.filter(
        created_at__gte=current_month
    ).count()
    last_month_locations = TourismLocation.objects.filter(
        created_at__gte=last_month,
        created_at__lt=current_month
    ).count()
    
    # Rating statistics
    avg_rating = TourismRating.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    rating_distribution = TourismRating.objects.values('rating').annotate(
        count=Count('rating')
    ).order_by('rating')
    
    context = {
        'total_locations': total_locations,
        'active_locations': active_locations,
        'total_categories': total_categories,
        'total_packages': total_packages,
        'total_events': total_events,
        'total_reviews': total_reviews,
        'pending_reviews': pending_reviews,
        'recent_locations': recent_locations,
        'recent_reviews': recent_reviews,
        'recent_events': recent_events,
        'current_month_locations': current_month_locations,
        'last_month_locations': last_month_locations,
        'avg_rating': round(avg_rating, 2),
        'rating_distribution': rating_distribution,
    }
    return render(request, 'admin_panel/tourism/dashboard.html', context)

# Location Management Views
@user_passes_test(is_staff)
def admin_panel_location_list(request):
    """List semua lokasi wisata untuk admin panel"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    featured_filter = request.GET.get('featured', '')
    
    locations = TourismLocation.objects.all()
    
    if search_query:
        locations = locations.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    if category_filter:
        locations = locations.filter(category_id=category_filter)
    
    if status_filter:
        locations = locations.filter(status=status_filter)
    
    if featured_filter:
        locations = locations.filter(featured=featured_filter == 'true')
    
    locations = locations.order_by('-created_at')
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Pagination with dynamic settings
    paginator = Paginator(locations, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = TourismCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'featured_filter': featured_filter,
    }
    return render(request, 'admin_panel/tourism/location_list.html', context)

@user_passes_test(is_staff)
def admin_panel_location_create(request):
    """Create lokasi wisata baru"""
    if request.method == 'POST':
        form = TourismLocationForm(request.POST, request.FILES)
        if form.is_valid():
            location = form.save(commit=False)
            location.created_by = request.user
            location.save()
            messages.success(request, 'Lokasi wisata berhasil ditambahkan!')
            return JsonResponse({
                'success': True, 
                'message': 'Lokasi wisata berhasil ditambahkan!',
                'redirect': reverse('admin_panel:tourism_locations_list')
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TourismLocationForm()
    
    categories = TourismCategory.objects.all()
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'admin_panel/tourism/location_form.html', context)

@user_passes_test(is_staff)
def admin_panel_location_detail(request, location_id):
    """Detail lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    galleries = TourismGallery.objects.filter(tourism_location=location)
    reviews = TourismReview.objects.filter(tourism_location=location).order_by('-created_at')[:10]
    ratings = TourismRating.objects.filter(tourism_location=location)
    
    # Statistics
    total_reviews = reviews.count()
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'location': location,
        'galleries': galleries,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 2),
    }
    return render(request, 'admin_panel/tourism/location_detail.html', context)

@user_passes_test(is_staff)
def admin_panel_location_update(request, location_id):
    """Update lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    
    if request.method == 'POST':
        form = TourismLocationForm(request.POST, request.FILES, instance=location)
        if form.is_valid():
            location = form.save(commit=False)
            location.updated_by = request.user
            location.save()
            messages.success(request, 'Lokasi wisata berhasil diperbarui!')
            return JsonResponse({
                'success': True, 
                'message': 'Lokasi wisata berhasil diperbarui!',
                'redirect': reverse('admin_panel:tourism_locations_list')
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TourismLocationForm(instance=location)
    
    categories = TourismCategory.objects.all()
    context = {
        'form': form,
        'location': location,
        'categories': categories,
    }
    return render(request, 'admin_panel/tourism/location_form.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_panel_location_delete(request, location_id):
    """Delete lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    location.delete()
    messages.success(request, 'Lokasi wisata berhasil dihapus!')
    return JsonResponse({'success': True})

@user_passes_test(is_staff)
@require_POST
def admin_panel_location_toggle_status(request, location_id):
    """Toggle status aktif lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    location.is_active = not location.is_active
    location.save()
    
    status_text = 'diaktifkan' if location.is_active else 'dinonaktifkan'
    messages.success(request, f'Lokasi wisata berhasil {status_text}!')
    return JsonResponse({'success': True, 'is_active': location.is_active})

@user_passes_test(is_staff)
@require_POST
def admin_panel_location_toggle_featured(request, location_id):
    """Toggle featured status lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    location.featured = not location.featured
    location.save()
    
    status_text = 'ditampilkan' if location.featured else 'disembunyikan'
    messages.success(request, f'Lokasi wisata berhasil {status_text} dari featured!')
    return JsonResponse({'success': True, 'featured': location.featured})

# Category Management Views
@user_passes_test(is_staff)
def admin_panel_category_list(request):
    """List semua kategori wisata"""
    search_query = request.GET.get('search', '')
    
    categories = TourismCategory.objects.all()
    
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    categories = categories.annotate(
        total_locations=Count('tourismlocation')
    ).order_by('-created_at')
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Pagination with dynamic settings
    paginator = Paginator(categories, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'admin_panel/tourism/category_list.html', context)

@user_passes_test(is_staff)
def admin_panel_category_detail(request, category_id):
    """Detail kategori wisata"""
    category = get_object_or_404(TourismCategory, id=category_id)
    
    # Get locations in this category
    locations = TourismLocation.objects.filter(category=category)
    
    # Get statistics
    total_locations = locations.count()
    active_locations = locations.filter(is_active=True).count()
    featured_locations = locations.filter(featured=True).count()
    
    context = {
        'category': category,
        'locations': locations,
        'total_locations': total_locations,
        'active_locations': active_locations,
        'featured_locations': featured_locations,
    }
    return render(request, 'admin_panel/tourism/category_detail.html', context)

@user_passes_test(is_staff)
def admin_panel_category_create(request):
    """Create kategori wisata baru"""
    if request.method == 'POST':
        form = TourismCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori wisata berhasil ditambahkan!')
            return redirect('admin_panel:tourism_categories_list')
        else:
            messages.error(request, 'Terjadi kesalahan saat menambahkan kategori. Silakan periksa form.')
    else:
        form = TourismCategoryForm()
    
    context = {
        'form': form,
    }
    return render(request, 'admin_panel/tourism/category_form.html', context)

@user_passes_test(is_staff)
def admin_panel_category_update(request, category_id):
    """Update kategori wisata"""
    category = get_object_or_404(TourismCategory, id=category_id)
    
    if request.method == 'POST':
        form = TourismCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori wisata berhasil diperbarui!')
            return redirect('admin_panel:tourism_categories_list')
        else:
            messages.error(request, 'Terjadi kesalahan saat memperbarui kategori. Silakan periksa form.')
    else:
        form = TourismCategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'admin_panel/tourism/category_form.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_panel_category_delete(request, category_id):
    """Delete kategori wisata"""
    category = get_object_or_404(TourismCategory, id=category_id)
    
    # Check if category has locations
    if category.tourismlocation_set.exists():
        return JsonResponse({
            'success': False, 
            'error': 'Kategori tidak dapat dihapus karena masih memiliki lokasi wisata.'
        })
    
    category.delete()
    messages.success(request, 'Kategori wisata berhasil dihapus!')
    return JsonResponse({'success': True})

# Package Management Views
@user_passes_test(is_staff)
def admin_panel_package_list(request):
    """List semua paket wisata"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    packages = TourismPackage.objects.all()
    
    if search_query:
        packages = packages.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status_filter:
        if status_filter == 'active':
            packages = packages.filter(is_active=True)
        elif status_filter == 'inactive':
            packages = packages.filter(is_active=False)
    
    packages = packages.order_by('-created_at')
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Pagination with dynamic settings
    paginator = Paginator(packages, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_panel/tourism/package_list.html', context)

@user_passes_test(is_staff)
def admin_panel_package_create(request):
    """Create paket wisata baru"""
    if request.method == 'POST':
        form = TourismPackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paket wisata berhasil ditambahkan!')
            return JsonResponse({'success': True, 'redirect': reverse('admin_panel:tourism_package_list')})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TourismPackageForm()
    
    locations = TourismLocation.objects.filter(is_active=True)
    context = {
        'form': form,
        'locations': locations,
    }
    return render(request, 'admin_panel/tourism/package_form.html', context)

@user_passes_test(is_staff)
def admin_panel_package_detail(request, package_id):
    """Detail paket wisata"""
    package = get_object_or_404(TourismPackage, id=package_id)
    galleries = TourismPackageGallery.objects.filter(package=package)
    
    context = {
        'package': package,
        'galleries': galleries,
    }
    return render(request, 'admin_panel/tourism/package_detail.html', context)

@user_passes_test(is_staff)
def admin_panel_package_update(request, package_id):
    """Update paket wisata"""
    package = get_object_or_404(TourismPackage, id=package_id)
    
    if request.method == 'POST':
        form = TourismPackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paket wisata berhasil diperbarui!')
            return JsonResponse({'success': True, 'redirect': reverse('admin_panel:tourism_package_list')})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TourismPackageForm(instance=package)
    
    locations = TourismLocation.objects.filter(is_active=True)
    context = {
        'form': form,
        'package': package,
        'locations': locations,
    }
    return render(request, 'admin_panel/tourism/package_form.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_panel_package_delete(request, package_id):
    """Delete paket wisata"""
    package = get_object_or_404(TourismPackage, id=package_id)
    package.delete()
    messages.success(request, 'Paket wisata berhasil dihapus!')
    return JsonResponse({'success': True})

# Event Management Views
@user_passes_test(is_staff)
def admin_panel_event_list(request):
    """List semua event wisata"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    events = TourismEvent.objects.all()
    
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    if status_filter:
        if status_filter == 'active':
            events = events.filter(is_active=True)
        elif status_filter == 'inactive':
            events = events.filter(is_active=False)
    
    events = events.order_by('-start_date')
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Pagination with dynamic settings
    paginator = Paginator(events, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'admin_panel/tourism/event_list.html', context)

@user_passes_test(is_staff)
def admin_panel_event_create(request):
    """Create event wisata baru"""
    if request.method == 'POST':
        form = TourismEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event wisata berhasil ditambahkan!')
            return JsonResponse({'success': True, 'redirect': reverse('admin_panel:tourism_event_list')})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TourismEventForm()
    
    context = {
        'form': form,
    }
    return render(request, 'admin_panel/tourism/event_form.html', context)

@user_passes_test(is_staff)
def admin_panel_event_detail(request, event_id):
    """Detail event wisata"""
    event = get_object_or_404(TourismEvent, id=event_id)
    
    context = {
        'event': event,
    }
    return render(request, 'admin_panel/tourism/event_detail.html', context)

@user_passes_test(is_staff)
def admin_panel_event_update(request, event_id):
    """Update event wisata"""
    event = get_object_or_404(TourismEvent, id=event_id)
    
    if request.method == 'POST':
        form = TourismEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event wisata berhasil diperbarui!')
            return JsonResponse({'success': True, 'redirect': reverse('admin_panel:tourism_event_list')})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TourismEventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'admin_panel/tourism/event_form.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_panel_event_delete(request, event_id):
    """Delete event wisata"""
    event = get_object_or_404(TourismEvent, id=event_id)
    event.delete()
    messages.success(request, 'Event wisata berhasil dihapus!')
    return JsonResponse({'success': True})

# Review Management Views
@user_passes_test(is_staff)
def admin_panel_review_list(request):
    """List semua review wisata"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    location_filter = request.GET.get('location', '')
    
    reviews = TourismReview.objects.select_related('tourism_location', 'user')
    
    if search_query:
        reviews = reviews.filter(
            Q(comment__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(tourism_location__title__icontains=search_query)
        )
    
    if status_filter:
        reviews = reviews.filter(is_approved=status_filter == 'approved')
    
    if location_filter:
        reviews = reviews.filter(tourism_location_id=location_filter)
    
    reviews = reviews.order_by('-created_at')
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Pagination with dynamic settings
    paginator = Paginator(reviews, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    locations = TourismLocation.objects.all()
    
    context = {
        'page_obj': page_obj,
        'locations': locations,
        'search_query': search_query,
        'status_filter': status_filter,
        'location_filter': location_filter,
    }
    return render(request, 'admin_panel/tourism/review_list.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_panel_review_approve(request, review_id):
    """Approve review"""
    review = get_object_or_404(TourismReview, id=review_id)
    review.is_approved = True
    review.save()
    messages.success(request, 'Review berhasil disetujui!')
    return JsonResponse({'success': True})

@user_passes_test(is_staff)
@require_POST
def admin_panel_review_reject(request, review_id):
    """Reject review"""
    review = get_object_or_404(TourismReview, id=review_id)
    review.is_approved = False
    review.save()
    messages.success(request, 'Review berhasil ditolak!')
    return JsonResponse({'success': True})

@user_passes_test(is_staff)
@require_POST
def admin_panel_review_delete(request, review_id):
    """Delete review"""
    review = get_object_or_404(TourismReview, id=review_id)
    review.delete()
    messages.success(request, 'Review berhasil dihapus!')
    return JsonResponse({'success': True})

# Gallery Management Views
@user_passes_test(is_staff)
def admin_panel_gallery_list(request):
    """List semua gallery wisata"""
    location_filter = request.GET.get('location', '')
    
    galleries = TourismGallery.objects.select_related('tourism_location')
    
    if location_filter:
        galleries = galleries.filter(tourism_location_id=location_filter)
    
    galleries = galleries.order_by('-created_at')
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Pagination with dynamic settings
    paginator = Paginator(galleries, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    locations = TourismLocation.objects.all()
    
    context = {
        'page_obj': page_obj,
        'locations': locations,
        'location_filter': location_filter,
    }
    return render(request, 'admin_panel/tourism/gallery_list.html', context)

@user_passes_test(is_staff)
@require_POST
def admin_panel_gallery_delete(request, gallery_id):
    """Delete gallery item"""
    gallery = get_object_or_404(TourismGallery, id=gallery_id)
    gallery.delete()
    messages.success(request, 'Gallery berhasil dihapus!')
    return JsonResponse({'success': True})

# FAQ Management Views
@user_passes_test(is_staff)
def admin_panel_faq_list(request):
    """List semua FAQ wisata"""
    search_query = request.GET.get('search', '')
    
    faqs = TourismFAQ.objects.all()
    
    if search_query:
        faqs = faqs.filter(
            Q(question__icontains=search_query) |
            Q(answer__icontains=search_query)
        )
    
    faqs = faqs.order_by('order', '-created_at')
    
    # Get settings configuration
    settings = TourismSettings.get_settings()
    
    # Pagination with dynamic settings
    paginator = Paginator(faqs, settings.admin_items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'admin_panel/tourism/faq_list.html', context)

# Reports and Analytics
@user_passes_test(is_staff)
def admin_panel_reports(request):
    """Laporan dan analitik tourism"""
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Location statistics
    location_stats = TourismLocation.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Review statistics
    review_stats = TourismReview.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).values('is_approved').annotate(
        count=Count('id')
    )
    
    # Rating distribution
    rating_stats = TourismRating.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).values('rating').annotate(
        count=Count('id')
    ).order_by('rating')
    
    # Popular locations
    popular_locations = TourismLocation.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('ratings__rating')
    ).order_by('-review_count')[:10]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'location_stats': location_stats,
        'review_stats': review_stats,
        'rating_stats': rating_stats,
        'popular_locations': popular_locations,
    }
    return render(request, 'admin_panel/tourism/reports.html', context)

# Export Data
@user_passes_test(is_staff)
def admin_panel_export_data(request):
    """Export data tourism"""
    import csv
    from django.http import HttpResponse
    import json
    
    export_type = request.GET.get('type', 'locations')
    format_type = request.GET.get('format', 'csv')
    
    if export_type == 'locations':
        data = TourismLocation.objects.all().values(
            'id', 'title', 'category__name', 'address', 'status',
            'is_active', 'featured', 'created_at'
        )
        filename = 'tourism_locations'
    elif export_type == 'reviews':
        data = TourismReview.objects.all().values(
            'id', 'tourism_location__title', 'user__username', 'comment',
            'is_approved', 'created_at'
        )
        filename = 'tourism_reviews'
    elif export_type == 'packages':
        data = TourismPackage.objects.all().values(
            'id', 'title', 'price', 'duration', 'is_active', 'created_at'
        )
        filename = 'tourism_packages'
    else:
        data = []
        filename = 'tourism_data'
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        if data:
            writer = csv.DictWriter(response, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        return response
    
    elif format_type == 'json':
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        
        # Convert datetime objects to strings
        data_list = list(data)
        for item in data_list:
            for key, value in item.items():
                if hasattr(value, 'isoformat'):
                    item[key] = value.isoformat()
        
        response.write(json.dumps(data_list, indent=2))
        return response
    
    return JsonResponse({'error': 'Invalid format type'})

# Bulk Operations
@user_passes_test(is_staff)
@require_POST
def admin_panel_bulk_operations(request):
    """Bulk operations untuk tourism"""
    action = request.POST.get('action')
    selected_ids = request.POST.getlist('selected_ids')
    
    if not selected_ids:
        return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'})
    
    if action == 'delete_locations':
        TourismLocation.objects.filter(id__in=selected_ids).delete()
        messages.success(request, f'{len(selected_ids)} lokasi wisata berhasil dihapus!')
    
    elif action == 'activate_locations':
        TourismLocation.objects.filter(id__in=selected_ids).update(is_active=True)
        messages.success(request, f'{len(selected_ids)} lokasi wisata berhasil diaktifkan!')
    
    elif action == 'deactivate_locations':
        TourismLocation.objects.filter(id__in=selected_ids).update(is_active=False)
        messages.success(request, f'{len(selected_ids)} lokasi wisata berhasil dinonaktifkan!')
    
    elif action == 'feature_locations':
        TourismLocation.objects.filter(id__in=selected_ids).update(featured=True)
        messages.success(request, f'{len(selected_ids)} lokasi wisata berhasil dijadikan featured!')
    
    elif action == 'unfeature_locations':
        TourismLocation.objects.filter(id__in=selected_ids).update(featured=False)
        messages.success(request, f'{len(selected_ids)} lokasi wisata berhasil dihapus dari featured!')
    
    elif action == 'approve_reviews':
        TourismReview.objects.filter(id__in=selected_ids).update(is_approved=True)
        messages.success(request, f'{len(selected_ids)} review berhasil disetujui!')
    
    elif action == 'reject_reviews':
        TourismReview.objects.filter(id__in=selected_ids).update(is_approved=False)
        messages.success(request, f'{len(selected_ids)} review berhasil ditolak!')
    
    elif action == 'delete_reviews':
        TourismReview.objects.filter(id__in=selected_ids).delete()
        messages.success(request, f'{len(selected_ids)} review berhasil dihapus!')
    
    else:
        return JsonResponse({'success': False, 'error': 'Aksi tidak valid'})
    
    return JsonResponse({'success': True})

# API Endpoints for Admin Panel
@user_passes_test(is_staff)
def admin_panel_api_locations(request):
    """API endpoint untuk lokasi wisata"""
    locations = TourismLocation.objects.all().values(
        'id', 'title', 'category__name', 'status', 'is_active', 'featured'
    )
    return JsonResponse(list(locations), safe=False)

@user_passes_test(is_staff)
def admin_panel_api_categories(request):
    """API endpoint untuk kategori wisata"""
    categories = TourismCategory.objects.all().values(
        'id', 'name', 'description'
    )
    return JsonResponse(list(categories), safe=False)

@user_passes_test(is_staff)
def admin_panel_api_statistics(request):
    """API endpoint untuk statistik tourism"""
    from django.db.models import Count, Avg
    
    stats = {
        'total_locations': TourismLocation.objects.count(),
        'active_locations': TourismLocation.objects.filter(is_active=True).count(),
        'total_categories': TourismCategory.objects.count(),
        'total_packages': TourismPackage.objects.count(),
        'total_events': TourismEvent.objects.count(),
        'total_reviews': TourismReview.objects.count(),
        'pending_reviews': TourismReview.objects.filter(is_approved=False).count(),
        'avg_rating': TourismRating.objects.aggregate(Avg('rating'))['rating__avg'] or 0,
    }
    
    return JsonResponse(stats)

# Settings Management
@user_passes_test(is_staff)
def admin_panel_settings(request):
    """Pengaturan tourism"""
    dashboard_config = TourismDashboard.objects.first()
    
    if request.method == 'POST':
        # Update dashboard configuration
        if dashboard_config:
            dashboard_config.title = request.POST.get('title', dashboard_config.title)
            dashboard_config.description = request.POST.get('description', dashboard_config.description)
            dashboard_config.hero_youtube = request.POST.get('hero_youtube', dashboard_config.hero_youtube)
            dashboard_config.is_active = request.POST.get('is_active') == 'on'
            
            if 'hero_background' in request.FILES:
                dashboard_config.hero_background = request.FILES['hero_background']
            if 'hero_video' in request.FILES:
                dashboard_config.hero_video = request.FILES['hero_video']
            
            dashboard_config.save()
            messages.success(request, 'Pengaturan berhasil disimpan!')
        else:
            # Create new dashboard config
            dashboard_config = TourismDashboard.objects.create(
                title=request.POST.get('title', 'Wisata Desa'),
                description=request.POST.get('description', ''),
                hero_youtube=request.POST.get('hero_youtube', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, 'Konfigurasi dashboard berhasil dibuat!')
        
        return redirect('admin_panel:tourism_settings')
    
    context = {
        'dashboard_config': dashboard_config,
    }
    return render(request, 'admin_panel/tourism/settings.html', context)

# Helper Views
@user_passes_test(is_staff)
def admin_panel_search_locations(request):
    """Search lokasi wisata untuk autocomplete"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse([])
    
    locations = TourismLocation.objects.filter(
        title__icontains=query
    ).values('id', 'title')[:10]
    
    return JsonResponse(list(locations), safe=False)

@user_passes_test(is_staff)
def admin_panel_location_stats(request, location_id):
    """Statistik detail lokasi wisata"""
    location = get_object_or_404(TourismLocation, id=location_id)
    
    stats = {
        'total_reviews': location.reviews.count(),
        'approved_reviews': location.reviews.filter(is_approved=True).count(),
        'pending_reviews': location.reviews.filter(is_approved=False).count(),
        'total_ratings': location.ratings.count(),
        'avg_rating': location.ratings.aggregate(Avg('rating'))['rating__avg'] or 0,
        'total_galleries': location.gallery.count(),
    }
    
    return JsonResponse(stats)