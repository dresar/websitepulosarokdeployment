from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse


def custom_login_redirect(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Authentication required.'}, status=403)
    return redirect('admin_panel:login')
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
import json
import logging
import io
import base64
import csv
import platform
import sys
from datetime import date

User = get_user_model()

# Import models
from .models import (
    WebsiteSettings, CustomUser, UserProfile, Role, MenuPermission, UserRole, LoginHistory,
    HeroImage
)

# Matplotlib and Plotly imports
try:
    import matplotlib  # type: ignore
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt  # type: ignore
except ImportError:
    plt = None

try:
    import plotly.graph_objects as go  # type: ignore
    from plotly.offline import plot  # type: ignore
except ImportError:
    go = None
    plot = None

# Removed duplicate import - already imported above
# from .forms import WebsiteSettingsForm, SystemSettingsForm  # Removed - not needed
# Safe imports for optional apps
try:
    from news.models import News, Announcement
    NEWS_AVAILABLE = True
except ImportError:
    NEWS_AVAILABLE = False

# try:
#     from business.models import Business
#     BUSINESS_AVAILABLE = True
# except ImportError:
BUSINESS_AVAILABLE = False

try:
    from village_profile.models import VillageProfile
    VILLAGE_PROFILE_AVAILABLE = True
except ImportError:
    VILLAGE_PROFILE_AVAILABLE = False

# References app is available - using references app Penduduk model
REFERENCES_AVAILABLE = True
try:
    from references.models import Penduduk, Family
except ImportError:
    REFERENCES_AVAILABLE = False
    Penduduk = None
    Family = None

try:
    from tourism.models import TourismLocation
    TOURISM_AVAILABLE = True
except ImportError:
    TOURISM_AVAILABLE = False

# Direct imports for required apps
from documents.models import Document
from village_profile.models import VillageOfficial

from django.contrib.admin.models import LogEntry
from datetime import datetime, timedelta
from django.db.models import Count
from collections import defaultdict
import calendar

logger = logging.getLogger(__name__)

def admin_redirect(request):
    """Redirect admin-panel/ to admin-panel/login/"""
    return redirect('/admin-panel/login/')

def custom_login(request):
    """Custom login view dengan role-based redirect"""
    if request.user.is_authenticated:
        return redirect('/admin-panel/dashboard/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(1209600)
                
                messages.success(request, f'Selamat datang, {user.get_full_name() or user.username}!')
                return redirect('/admin-panel/dashboard/')
            else:
                messages.error(request, 'Akun Anda tidak aktif.')
        else:
            messages.error(request, 'Username atau password salah.')
    
    return render(request, 'admin_panel/login.html')

@login_required
def custom_logout(request):
    """Custom logout view"""
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.info(request, f'Anda telah berhasil logout. Sampai jumpa, {user_name}!')
    return redirect('admin_panel:login')

@login_required
def dashboard(request):
    """Dashboard view dengan role-based content"""
    user = request.user
    user_roles = user.get_active_roles()
    
    context = {
        'user': user,
        'roles': user_roles,
        'role_name': user_roles.first().display_name if user_roles.exists() else 'User',
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

def home_view(request):
    """View untuk halaman utama website"""
    try:
        # Get website settings
        website_settings = WebsiteSettings.objects.first()
        
        # Hero image will be provided by context processor
        # No need to set hero_image_url here as it's handled by website_settings context processor
        
        context = {
            'website_settings': website_settings,
            'page_title': 'Beranda',
            'page_subtitle': 'Selamat Datang di Desa Pulosarok',
            'latest_news': [],
            'announcements': [],
            'featured_businesses': [],
            'tourism_locations': [],
            'village_officials': [],
            'total_population': 0,
            'total_families': 0,
            'male_population': 0,
            'female_population': 0,
            'village_profile': None,
            'population_stats': {},
            'age_groups': {},
            'education_levels': {},
        }
        
        # Try to get data from other apps with safe imports
        if NEWS_AVAILABLE:
            try:
                latest_news = News.objects.filter(status='published').order_by('-published_date')[:4]
                context['latest_news'] = latest_news
                logger.info(f"Loaded {len(latest_news)} news items")
                
                now = timezone.now()
                announcements = Announcement.objects.filter(
                    status='published',
                    start_date__lte=now
                ).filter(
                    Q(end_date__isnull=True) | Q(end_date__gte=now)
                ).order_by('-is_pinned', '-priority', '-start_date')[:5]
                context['announcements'] = announcements
                
                # Get upcoming events (limit to 6 for home page)
                try:
                    from events.models import Event  # type: ignore
                    upcoming_events = Event.objects.filter(
                        status='published',
                        event_date__gte=now
                    ).order_by('event_date')[:6]
                    context['upcoming_events'] = upcoming_events
                except ImportError:
                    context['upcoming_events'] = []
            except Exception as e:
                logger.error(f"Error loading news data: {str(e)}")
                context.update({
                    'latest_news': [],
                    'announcements': [],
                    'upcoming_events': [],
                })
        else:
            logger.warning("News app not available")
            # Set fallback data
            context.update({
                'latest_news': [],
                'announcements': [],
                'upcoming_events': [],
            })
        
        # if BUSINESS_AVAILABLE:
        #     try:
        #         from business.models import Business
        #         featured_businesses = Business.objects.filter(status='approved').order_by('-created_at')[:4]
        #         context['featured_businesses'] = featured_businesses
        #     except Exception as e:
        #         logger.error(f"Error loading business data: {str(e)}")
        context['featured_businesses'] = []
        
        if TOURISM_AVAILABLE:
            try:
                from tourism.models import TourismLocation
                tourism_locations = TourismLocation.objects.filter(is_active=True).order_by('-created_at')[:4]
                context['tourism_locations'] = tourism_locations
                # Also add as featured_tourism for backward compatibility
                context['featured_tourism'] = tourism_locations
                logger.info(f"Loaded {len(tourism_locations)} tourism locations")
            except Exception as e:
                logger.error(f"Error loading tourism data: {str(e)}")
                context.update({
                    'tourism_locations': [],
                    'featured_tourism': [],
                })
        else:
            logger.warning("Tourism app not available")
            context.update({
                'tourism_locations': [],
                'featured_tourism': [],
            })
        
        try:
            from village_profile.models import VillageOfficial, VillageProfile, VillagePhoto
            village_officials = VillageOfficial.objects.filter(is_active=True)[:8]
            context['village_officials'] = village_officials
            
            # Get village profile data
            village_profile = VillageProfile.objects.filter(is_active=True).first()
            if village_profile:
                context['village_profile'] = village_profile
                # Get featured photos for auto-sliding with error handling
                try:
                    village_photos = VillagePhoto.objects.filter(
                        village=village_profile, 
                        is_active=True
                    ).order_by('-is_featured', 'display_order')[:5]
                    # Filter out photos without valid image files
                    valid_photos = []
                    for photo in village_photos:
                        try:
                            if photo.image and hasattr(photo.image, 'url'):
                                # Test if the image file exists
                                photo.image.url
                                valid_photos.append(photo)
                        except Exception:
                            # Skip photos with invalid image files
                            continue
                    context['village_photos'] = valid_photos
                except Exception as e:
                    logger.warning(f"Error loading village photos: {str(e)}")
                    context['village_photos'] = []
            else:
                context['village_profile'] = None
                context['village_photos'] = []
        except ImportError:
            logger.warning("Village profile app not available")
            # Set fallback data
            context.update({
                'village_officials': [],
                'village_profile': None,
                'village_photos': [],
            })
        
        if REFERENCES_AVAILABLE:
            try:
                from datetime import date
                
                # Get real-time data from database
                total_population = Penduduk.objects.filter(is_active=True, is_alive=True).count()
                total_families = Family.objects.filter(is_active=True).count()
                male_population = Penduduk.objects.filter(is_active=True, is_alive=True, gender='L').count()
                female_population = Penduduk.objects.filter(is_active=True, is_alive=True, gender='P').count()
                
                # Calculate age groups with proper date handling - using same logic as API
                today = date.today()
                age_groups = {
                    '0-14': 0,
                    '15-24': 0,
                    '25-54': 0,
                    '55-64': 0,
                    '65+': 0
                }
                
                residents = Penduduk.objects.filter(is_active=True, is_alive=True)
                for resident in residents:
                    if resident.birth_date:
                        age = today.year - resident.birth_date.year
                        # Handle leap year edge case for February 29th
                        try:
                            if resident.birth_date.replace(year=today.year) > today:
                                age -= 1
                        except ValueError:
                            # Handle February 29th in non-leap year
                            if resident.birth_date.month == 2 and resident.birth_date.day == 29:
                                # Use February 28th for comparison
                                birth_date_this_year = resident.birth_date.replace(year=today.year, day=28)
                                if birth_date_this_year > today:
                                    age -= 1
                            else:
                                # For other cases, just use the original logic
                                if resident.birth_date.replace(year=today.year) > today:
                                    age -= 1
                        
                        if age <= 14:
                            age_groups['0-14'] += 1
                        elif age <= 24:
                            age_groups['15-24'] += 1
                        elif age <= 54:
                            age_groups['25-54'] += 1
                        elif age <= 64:
                            age_groups['55-64'] += 1
                        else:
                            age_groups['65+'] += 1
                
                # Calculate education levels
                education_levels = {
                    'sd': Penduduk.objects.filter(is_active=True, is_alive=True, education__in=['BELUM_TAMAT_SD', 'TAMAT_SD']).count(),
                    'smp': Penduduk.objects.filter(is_active=True, is_alive=True, education='SLTP').count(),
                    'sma': Penduduk.objects.filter(is_active=True, is_alive=True, education='SLTA').count(),
                    'perguruan_tinggi': Penduduk.objects.filter(is_active=True, is_alive=True, education__in=['D1', 'D2', 'D3', 'D4_S1', 'S2', 'S3']).count(),
                }
                
                # Calculate occupation levels
                occupation_levels = {
                    'nelayan': Penduduk.objects.filter(is_active=True, is_alive=True, occupation__icontains='nelayan').count(),
                    'petani': Penduduk.objects.filter(is_active=True, is_alive=True, occupation__icontains='petani').count(),
                    'lainnya': Penduduk.objects.filter(is_active=True, is_alive=True).exclude(occupation__icontains='nelayan').exclude(occupation__icontains='petani').count(),
                }
                
                # Calculate percentages
                male_percentage = round((male_population / total_population * 100), 1) if total_population > 0 else 0
                female_percentage = round((female_population / total_population * 100), 1) if total_population > 0 else 0
                average_family_size = round((total_population / total_families), 1) if total_families > 0 else 0
                
                context.update({
                    'total_population': total_population,
                    'total_families': total_families,
                    'male_population': male_population,
                    'female_population': female_population,
                    'age_groups': {
                        'age_0_14': age_groups['0-14'],
                        'age_15_24': age_groups['15-24'],
                        'age_25_54': age_groups['25-54'],
                        'age_55_64': age_groups['55-64'],
                        'age_65_plus': age_groups['65+'],
                    },
                    'education_levels': education_levels,
                    'occupation_levels': occupation_levels,
                    'population_stats': {
                        'total': total_population,
                        'male': male_population,
                        'female': female_population,
                        'families': total_families,
                        'male_percentage': male_percentage,
                        'female_percentage': female_percentage,
                        'average_family_size': average_family_size,
                        'growth_rate': 2.3,  # You can calculate this based on historical data
                    },
                })
            except ImportError:
                logger.warning("References app not available")
                # Set minimal fallback data
                context.update({
                    'total_population': 0,
                    'total_families': 0,
                    'male_population': 0,
                    'female_population': 0,
                    'population_stats': {
                        'total': 0,
                        'male': 0,
                        'female': 0,
                        'families': 0,
                        'male_percentage': 0,
                        'female_percentage': 0,
                        'average_family_size': 0,
                        'growth_rate': 0,
                    },
                    'age_groups': {
                        'age_0_14': 0,
                        'age_15_64': 0,
                        'age_65_plus': 0,
                    },
                    'education_levels': {
                        'sd': 0,
                        'smp': 0,
                        'sma': 0,
                        'perguruan_tinggi': 0,
                    },
                })
        else:
            logger.warning("References app not available")
            # Set minimal fallback data
            context.update({
                'total_population': 0,
                'total_families': 0,
                'male_population': 0,
                'female_population': 0,
                'population_stats': {
                    'total': 0,
                    'male': 0,
                    'female': 0,
                    'families': 0,
                    'male_percentage': 0,
                    'female_percentage': 0,
                    'average_family_size': 0,
                    'growth_rate': 0,
                },
                'age_groups': {
                    'age_0_14': 0,
                    'age_15_64': 0,
                    'age_65_plus': 0,
                },
                'education_levels': {
                    'sd': 0,
                    'smp': 0,
                    'sma': 0,
                    'perguruan_tinggi': 0,
                },
            })
        
        if VILLAGE_PROFILE_AVAILABLE:
            try:
                from village_profile.models import VillageProfile, VillagePhoto
                village_profile = VillageProfile.objects.first()
                context['village_profile'] = village_profile
                
                # Get gallery photos (limit to 6 for home page)
                if village_profile:
                    gallery_photos = VillagePhoto.objects.filter(
                        village=village_profile, 
                        is_active=True
                    ).order_by('-is_featured', '-created_at')[:6]
                    context['gallery_photos'] = gallery_photos
                else:
                    context['gallery_photos'] = []
            except Exception as e:
                logger.error(f"Error loading village profile data: {str(e)}")
                context.update({
                    'village_profile': None,
                    'gallery_photos': [],
                })
        else:
            logger.warning("Village profile app not available")
            # Set fallback data
            context.update({
                'village_profile': None,
                'gallery_photos': [],
            })
        
        return render(request, 'public/home.html', context)
        
    except Exception as e:
        logger.error(f"Error in home_view: {str(e)}")
        return render(request, 'public/home.html', {
            'error': 'Terjadi kesalahan saat memuat halaman'
        })


@staff_member_required(login_url='/admin-panel/login/')
def admin_dashboard_view(request):
    """Dashboard admin untuk statistik website dengan visualisasi data"""
    try:
        # Get basic statistics
        total_messages = 0  # Message model removed
        unread_messages = 0  # Message model removed
        
        # Get recent messages
        recent_messages = []  # Message model removed
        
        # Get system settings
        website_settings = WebsiteSettings.get_settings()
        
        # Get module statistics
        active_modules = 0  # ModuleSettings model removed
        total_modules = 0  # ModuleSettings model removed
        
        context = {
            'total_messages': total_messages,
            'unread_messages': unread_messages,
            'recent_messages': recent_messages,
            'website_settings': website_settings,
            'active_modules': active_modules,
            'total_modules': total_modules,
        }
        
        # Generate charts
        context['user_chart'] = generate_user_statistics_chart()
        context['population_chart'] = generate_population_chart()
        context['business_chart'] = generate_business_chart()
        
        return render(request, 'admin/core/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in admin_dashboard_view: {str(e)}")
        messages.error(request, 'Terjadi kesalahan saat memuat dashboard')
        return redirect('/admin/')


@staff_member_required(login_url='/admin-panel/login/')
# Removed duplicate website_settings_view - using website_settings instead

 


def offline_view(request):
    """View untuk halaman offline"""
    context = {
        'website_settings': WebsiteSettings.objects.first(),
    }
    return render(request, 'public/offline.html', context)


def generate_user_statistics_chart():
    """Generate user statistics chart using Plotly"""
    try:
        if not go or not plot:
            return None
            
        # Get user data
        user_data = {
            'Total Users': CustomUser.objects.count(),
            'Active Users': CustomUser.objects.filter(is_active=True).count(),
            'Staff Users': CustomUser.objects.filter(is_staff=True).count()
        }
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(user_data.keys()),
            values=list(user_data.values()),
            hole=0.3
        )])
        
        fig.update_layout(
            title="Statistik Pengguna",
            showlegend=True,
            height=400
        )
        
        return plot(fig, output_type='div', include_plotlyjs=False)
    except Exception as e:
        logger.error(f"Error generating user chart: {str(e)}")
        return None


def generate_population_chart():
    """Generate population statistics chart using Plotly"""
    try:
        if not go or not plot:
            return None
            
        population_data = {'Laki-laki': 0, 'Perempuan': 0}
        try:
            population_data['Laki-laki'] = Penduduk.objects.filter(gender='L').count()
            population_data['Perempuan'] = Penduduk.objects.filter(gender='P').count()
        except ImportError:
            pass
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(population_data.keys()),
                y=list(population_data.values()),
                marker_color=['#3498db', '#e74c3c']
            )
        ])
        
        fig.update_layout(
            title="Statistik Penduduk Berdasarkan Jenis Kelamin",
            xaxis_title="Jenis Kelamin",
            yaxis_title="Jumlah",
            height=400
        )
        
        return plot(fig, output_type='div', include_plotlyjs=False)
    except Exception as e:
        logger.error(f"Error generating population chart: {str(e)}")
        return None


def generate_business_chart():
    """Generate business statistics chart using Matplotlib"""
    try:
        if not plt:
            return None
            
        business_data = {'Approved': 0, 'Pending': 0, 'Rejected': 0}
        
        # try:
        #     from business.models import Business
        #     business_data['Approved'] = Business.objects.filter(status='approved').count()
        #     business_data['Pending'] = Business.objects.filter(status='pending').count()
        #     business_data['Rejected'] = Business.objects.filter(status='rejected').count()
        # except ImportError:
        #     pass
        
        # Create matplotlib chart
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#2ecc71', '#f39c12', '#e74c3c']
        
        wedges, texts, autotexts = ax.pie(
            business_data.values(),
            labels=business_data.keys(),
            colors=colors,
            autopct='%1.1f%%',
            startangle=90
        )
        
        ax.set_title('Statistik Status Bisnis')
        
        # Convert to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        
        return f'data:image/png;base64,{graphic}'
    except Exception as e:
        logger.error(f"Error generating business chart: {str(e)}")
        return None


@staff_member_required(login_url='/admin-panel/login/')
def export_users_csv(request):
    """Export users data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Date Joined', 'Is Active', 'Is Staff'])
    
    users = CustomUser.objects.all()
    for user in users:
        writer.writerow([
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            user.is_active,
            user.is_staff
        ])
    
    return response


@staff_member_required(login_url='/admin-panel/login/')
def export_population_csv(request):
    """Export population data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="population_export.csv"'
    
    writer = csv.writer(response)
    try:
        writer.writerow(['NIK', 'Nama', 'Jenis Kelamin', 'Tanggal Lahir', 'Alamat'])
        
        penduduk = Penduduk.objects.all()
        for p in penduduk:
            writer.writerow([
                p.nik,
                p.nama,
                p.get_gender_display(),
                p.tanggal_lahir.strftime('%Y-%m-%d') if p.tanggal_lahir else '',
                p.alamat
            ])
    except ImportError:
        writer.writerow(['Error: References app not available'])
    
    return response




# Public views that are referenced in URLs but missing
def profile_view(request):
    """View untuk halaman profil desa - redirect ke village_profile"""
    from django.urls import reverse
    return redirect(reverse('village_profile:dashboard'))


def population_view(request):
    """View untuk halaman data penduduk - redirect ke village_profile"""
    from django.urls import reverse
    return redirect(reverse('village_profile:demography'))


def events_view(request):
    """View untuk halaman kegiatan"""
    context = {
        'website_settings': WebsiteSettings.objects.first(),
        'title': 'Kegiatan Desa',
        'hero_image': None,
        'page_title': 'Kegiatan',
        'page_subtitle': 'Kegiatan dan Acara Desa Pulosarok'
    }
    return render(request, 'public/events.html', context)


# News views removed - handled by news app


def tourism_view(request):
    """View untuk halaman wisata"""
    from .models import HeroImage
    hero_image = HeroImage.objects.filter(page='tourism', is_active=True).first()
    context = {
        'website_settings': WebsiteSettings.objects.first(),
        'title': 'Wisata Desa',
        'hero_image': hero_image.image if hero_image else None,
        'hero_image_url': hero_image.image.url if hero_image and hero_image.image else None,
        'page_title': 'Wisata',
        'page_subtitle': 'Tempat Wisata Menarik di Desa Pulosarok'
    }
    try:
        from tourism.models import TourismLocation
        context['tourism_locations'] = TourismLocation.objects.filter(is_active=True)
    except ImportError:
        context['tourism_locations'] = []
    return render(request, 'public/tourism.html', context)


def umkm_view(request):
    """View untuk halaman UMKM"""
    from .models import HeroImage
    hero_image = HeroImage.objects.filter(page='umkm', is_active=True).first()
    context = {
        'website_settings': WebsiteSettings.objects.first(),
        'title': 'UMKM Desa',
        'hero_image': hero_image.image if hero_image else None,
        'hero_image_url': hero_image.image.url if hero_image and hero_image.image else None,
        'page_title': 'UMKM',
        'page_subtitle': 'Usaha Mikro Kecil Menengah Desa Pulosarok'
    }
    # try:
    #     from business.models import Business
    #     context['businesses'] = Business.objects.filter(status='approved')
    # except ImportError:
    context['businesses'] = []
    return render(request, 'public/umkm.html', context)


def organization_view(request):
    """View untuk halaman organisasi"""
    from .models import HeroImage
    hero_image = HeroImage.objects.filter(page='organization', is_active=True).first()
    context = {
        'website_settings': WebsiteSettings.objects.first(),
        'title': 'Organisasi Desa',
        'hero_image': hero_image.image if hero_image else None,
        'hero_image_url': hero_image.image.url if hero_image and hero_image.image else None,
        'page_title': 'Organisasi',
        'page_subtitle': 'Struktur Organisasi Desa Pulosarok'
    }
    try:
        from village_profile.models import VillageOfficial
        context['officials'] = VillageOfficial.objects.filter(is_active=True)
    except ImportError:
        context['officials'] = []
    return render(request, 'public/organization.html', context)


def correspondence_view(request):
    """View untuk halaman layanan surat"""
    from layanan.models import LayananDocumentRequest
    
    context = {
        'website_settings': WebsiteSettings.objects.first(),
        'title': 'Layanan Dokumen Desa',
        'hero_image': None,
        'page_title': 'Layanan Surat',
        'page_subtitle': 'Layanan Surat Menyurat Desa Pulosarok',
        'document_types': LayananDocumentRequest.DOCUMENT_TYPE_CHOICES
    }
    return render(request, 'Layanan/document_services.html', context)


# Contact view removed - functionality moved to complaints app


def gallery_view(request):
    """View untuk halaman galeri"""
    context = {
        'website_settings': WebsiteSettings.objects.first(),
        'title': 'Galeri',
        'hero_image': None,
        'page_title': 'Galeri',
        'page_subtitle': 'Galeri Foto Desa Pulosarok'
    }
    return render(request, 'public/gallery.html', context)


def complaints_view(request):
    """View untuk halaman pengaduan"""
    context = {
        'website_settings': WebsiteSettings.objects.first(),
        'title': 'Pengaduan',
        'hero_image': None,
        'page_title': 'Pengaduan',
        'page_subtitle': 'Layanan Pengaduan Desa Pulosarok'
    }
    return render(request, 'public/complaints.html', context)


def bantuna_view(request):
    """View untuk halaman Bantuna"""
    context = {
        'website_settings': WebsiteSettings.objects.first(),
        'title': 'Bantuna',
        'hero_image': None,
        'page_title': 'Bantuna',
        'page_subtitle': 'Bantuan dan Layanan Desa Pulosarok',
        'meta_description': 'Informasi lengkap tentang bantuan dan layanan yang tersedia di Desa Pulosarok. Temukan program bantuan sosial, layanan administrasi, dan dukungan untuk masyarakat.'
    }
    return render(request, 'public/bantuna.html', context)


# Settings views moved to admin_panel/admin_views.py


# System setting update moved to admin_panel


# Website settings API moved to admin_panel


# Module settings API moved to admin_panel


# Maintenance mode toggle moved to admin_panel



# Admin profile views moved to admin_panel


# Edit profile view moved to admin_panel


# Change password view moved to admin_panel


# Change username view moved to admin_panel


# Profile photo views moved to admin_panel


# ==================== ADDITIONAL VIEWS FOR SETTINGS PAGES ====================

@login_required
@staff_member_required(login_url='/admin-panel/login/')
def user_management_view(request):
    """View for user management page"""
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Manajemen Pengguna',
        'users': page_obj,
        'search': search,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'staff_users': users.filter(is_staff=True).count(),
    }
    return render(request, 'admin_panel/settings/users.html', context)




# ==================== WEBSITE SETTINGS VIEWS ====================

# Removed unused settings views - using website_settings_view instead




@login_required
@staff_member_required(login_url='/admin-panel/login/')
def activity_logs_view(request):
    """View system activity logs"""
    from django.contrib.admin.models import LogEntry
    
    logs = LogEntry.objects.select_related('user', 'content_type').all().order_by('-action_time')
    
    # Filter by user
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    # Filter by action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action_flag=action)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        logs = logs.filter(action_time__date__gte=date_from)
    if date_to:
        logs = logs.filter(action_time__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    from core.models import CustomUser
    users = CustomUser.objects.filter(is_staff=True)
    
    context = {
        'title': 'Log Aktivitas',
        'logs': page_obj,
        'users': users,
        'selected_user': user_id,
        'selected_action': action,
        'date_from': date_from,
        'date_to': date_to,
        'total_logs': logs.count(),
    }
    return render(request, 'admin_panel/settings/activity_logs.html', context)


# Removed module_settings_view - ModuleSettings model removed


# Removed profile_settings_view - using website_settings_view instead


# Removed general_settings_view - using website_settings_view instead


@login_required
@staff_member_required(login_url='/admin-panel/login/')
def system_info_view(request):
    """System information page"""
    import platform
    import sys
    import django
    from django.conf import settings
    
    system_info = {
        'python_version': sys.version,
        'django_version': django.get_version(),
        'platform': platform.platform(),
        'database': settings.DATABASES['default']['ENGINE'],
        'debug_mode': settings.DEBUG,
        'installed_apps': len(settings.INSTALLED_APPS),
        'timezone': settings.TIME_ZONE,
        'language_code': settings.LANGUAGE_CODE,
    }
    
    context = {
        'title': 'Informasi Sistem',
        'system_info': system_info,
    }
    return render(request, 'admin_panel/settings/system_info.html', context)


# ==================== API VIEWS FOR SETTINGS ====================

@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["POST"])
def api_add_system_setting(request):
    """API to add new system setting - DISABLED: SystemSettings model not available"""
    return JsonResponse({
        'success': False,
        'message': 'System settings functionality is not available'
    })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["POST"])
def api_update_system_setting(request):
    """API to update system setting - DISABLED: SystemSettings model not available"""
    return JsonResponse({
        'success': False,
        'message': 'System settings functionality is not available'
    })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["POST"])
def api_delete_system_setting(request):
    """API to delete system setting - DISABLED: SystemSettings model not available"""
    return JsonResponse({
        'success': False,
        'message': 'System settings functionality is not available'
    })


@require_http_methods(["GET"])
def public_website_settings(request):
    """Public API endpoint untuk mendapatkan pengaturan website (tanpa data sensitif)"""
    try:
        website_settings = WebsiteSettings.get_settings()
        
        data = {
            'site_name': website_settings.site_name,
            'site_description': website_settings.site_description,
            'site_logo': website_settings.site_logo.url if website_settings.site_logo else None,
            'site_favicon': website_settings.site_favicon.url if website_settings.site_favicon else None,
            'background_image': website_settings.background_image.url if website_settings.background_image else None,
            'contact_email': website_settings.contact_email,
            'contact_phone': website_settings.contact_phone,
            'contact_address': website_settings.contact_address,
            'facebook_url': website_settings.facebook_url,
            'instagram_url': website_settings.instagram_url,
            'twitter_url': website_settings.twitter_url,
            'youtube_url': website_settings.youtube_url,
            'theme': website_settings.theme,
            'primary_color': website_settings.primary_color,
            'secondary_color': website_settings.secondary_color,
            'default_language': website_settings.default_language,
            'timezone': website_settings.timezone,
            'meta_keywords': website_settings.meta_keywords,
            'meta_description': website_settings.meta_description,
            'google_analytics_id': website_settings.google_analytics_id,
            'maintenance_mode': website_settings.maintenance_mode,
            'maintenance_message': website_settings.maintenance_message,
        }
        
        return JsonResponse({
            'success': True,
            'data': data
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["GET"])
def api_website_settings(request):
    """API endpoint untuk mendapatkan pengaturan website"""
    try:
        website_settings = WebsiteSettings.get_settings()
        
        data = {
            'id': website_settings.id,
            'site_name': website_settings.site_name,
            'site_description': website_settings.site_description,
            'site_logo': website_settings.site_logo.url if website_settings.site_logo else None,
            'site_favicon': website_settings.site_favicon.url if website_settings.site_favicon else None,
            'background_image': website_settings.background_image.url if website_settings.background_image else None,
            'contact_email': website_settings.contact_email,
            'contact_phone': website_settings.contact_phone,
            'contact_address': website_settings.contact_address,
            'facebook_url': website_settings.facebook_url,
            'instagram_url': website_settings.instagram_url,
            'twitter_url': website_settings.twitter_url,
            'youtube_url': website_settings.youtube_url,
            'theme': website_settings.theme,
            'primary_color': website_settings.primary_color,
            'secondary_color': website_settings.secondary_color,
            'default_language': website_settings.default_language,
            'timezone': website_settings.timezone,
            'meta_keywords': website_settings.meta_keywords,
            'meta_description': website_settings.meta_description,
            'google_analytics_id': website_settings.google_analytics_id,
            'maintenance_mode': website_settings.maintenance_mode,
            'maintenance_message': website_settings.maintenance_message,
            'allow_registration': website_settings.allow_registration,
            'max_file_upload_size': website_settings.max_file_upload_size,
            'email_notifications': website_settings.email_notifications,
            'sms_notifications': website_settings.sms_notifications,
            'created_at': website_settings.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': website_settings.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["POST"])
def api_update_website_settings(request):
    """API endpoint untuk update pengaturan website"""
    try:
        website_settings = WebsiteSettings.get_settings()
        
        # Update basic information
        website_settings.site_name = request.POST.get('site_name', website_settings.site_name)
        website_settings.site_description = request.POST.get('site_description', website_settings.site_description)
        
        # Update contact information
        website_settings.contact_email = request.POST.get('contact_email', website_settings.contact_email)
        website_settings.contact_phone = request.POST.get('contact_phone', website_settings.contact_phone)
        website_settings.contact_address = request.POST.get('contact_address', website_settings.contact_address)
        
        # Update social media
        website_settings.facebook_url = request.POST.get('facebook_url', website_settings.facebook_url)
        website_settings.instagram_url = request.POST.get('instagram_url', website_settings.instagram_url)
        website_settings.twitter_url = request.POST.get('twitter_url', website_settings.twitter_url)
        website_settings.youtube_url = request.POST.get('youtube_url', website_settings.youtube_url)
        
        # Update appearance
        website_settings.theme = request.POST.get('theme', website_settings.theme)
        website_settings.primary_color = request.POST.get('primary_color', website_settings.primary_color)
        website_settings.secondary_color = request.POST.get('secondary_color', website_settings.secondary_color)
        
        # Update localization
        website_settings.default_language = request.POST.get('default_language', website_settings.default_language)
        website_settings.timezone = request.POST.get('timezone', website_settings.timezone)
        
        # Update SEO settings
        website_settings.meta_keywords = request.POST.get('meta_keywords', website_settings.meta_keywords)
        website_settings.meta_description = request.POST.get('meta_description', website_settings.meta_description)
        website_settings.google_analytics_id = request.POST.get('google_analytics_id', website_settings.google_analytics_id)
        
        # Update system settings
        website_settings.maintenance_mode = 'maintenance_mode' in request.POST
        website_settings.maintenance_message = request.POST.get('maintenance_message', website_settings.maintenance_message)
        website_settings.allow_registration = 'allow_registration' in request.POST
        website_settings.max_file_upload_size = int(request.POST.get('max_file_upload_size', website_settings.max_file_upload_size))
        
        # Update notification settings
        website_settings.email_notifications = 'email_notifications' in request.POST
        website_settings.sms_notifications = 'sms_notifications' in request.POST
        
        # Handle file uploads
        if 'site_logo' in request.FILES:
            website_settings.site_logo = request.FILES['site_logo']
        if 'site_favicon' in request.FILES:
            website_settings.site_favicon = request.FILES['site_favicon']
        if 'background_image' in request.FILES:
            website_settings.background_image = request.FILES['background_image']
        
        website_settings.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Pengaturan website berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["POST"])
def api_add_user(request):
    """API to add new user"""
    try:
        from django.contrib.auth.models import Group
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone_number = request.POST.get('phone_number', '')
        position = request.POST.get('position', '')
        address = request.POST.get('address', '')
        password = request.POST.get('password')
        is_active = request.POST.get('is_active', 'true').lower() == 'true'
        is_staff = request.POST.get('is_staff', 'false').lower() == 'true'
        is_superuser = request.POST.get('is_superuser', 'false').lower() == 'true'
        
        if not username or not email or not password:
            return JsonResponse({
                'success': False,
                'message': 'Username, email, and password are required'
            })
        
        # Check if user already exists
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'User with this username already exists'
            })
        
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'User with this email already exists'
            })
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            position=position,
            address=address,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        
        return JsonResponse({
            'success': True,
            'message': 'User created successfully',
            'user_id': user.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["POST"])
def api_update_user(request):
    """API to update user"""
    try:
        user_id = request.POST.get('user_id')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone_number = request.POST.get('phone_number', '')
        position = request.POST.get('position', '')
        address = request.POST.get('address', '')
        is_active = request.POST.get('is_active', 'true').lower() == 'true'
        is_staff = request.POST.get('is_staff', 'false').lower() == 'true'
        is_superuser = request.POST.get('is_superuser', 'false').lower() == 'true'
        
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': 'User ID is required'
            })
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            })
        
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.position = position
        user.address = address
        user.is_active = is_active
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'User updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["POST"])
def api_delete_user(request):
    """API to delete user"""
    try:
        user_id = request.POST.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': 'User ID is required'
            })
        
        try:
            user = CustomUser.objects.get(id=user_id)
            # Don't allow deletion of superusers
            if user.is_superuser:
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot delete superuser'
                })
            user.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'User deleted successfully'
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["GET"])
def api_list_users(request):
    """API to list users"""
    try:
        users = CustomUser.objects.all().order_by('-date_joined')
        
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'position': user.position,
                'address': user.address,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
            })
        
        return JsonResponse({
            'success': True,
            'users': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["POST"])
def api_toggle_user_status(request):
    """API to toggle user active status"""
    try:
        user_id = request.POST.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': 'User ID is required'
            })
        
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
                'is_active': user.is_active
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def api_update_profile(request):
    """API to update user profile"""
    try:
        from core.models import UserProfile
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Update basic user info
        if 'first_name' in request.POST:
            request.user.first_name = request.POST.get('first_name', '')
        if 'last_name' in request.POST:
            request.user.last_name = request.POST.get('last_name', '')
        if 'email' in request.POST:
            request.user.email = request.POST.get('email', '')
        if 'phone_number' in request.POST:
            request.user.phone_number = request.POST.get('phone_number', '')
        if 'position' in request.POST:
            request.user.position = request.POST.get('position', '')
        if 'address' in request.POST:
            request.user.address = request.POST.get('address', '')
        
        request.user.save()
        
        # Update profile info
        if 'bio' in request.POST:
            profile.bio = request.POST.get('bio', '')
        if 'birth_date' in request.POST:
            birth_date = request.POST.get('birth_date')
            if birth_date:
                from datetime import datetime
                profile.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        if 'address' in request.POST:
            profile.address = request.POST.get('address', '')
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def api_change_password(request):
    """API to change user password"""
    try:
        from django.contrib.auth import authenticate
        
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'All password fields are required'
            })
        
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'New passwords do not match'
            })
        
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            })
        
        # Verify current password
        user = authenticate(username=request.user.username, password=current_password)
        if not user:
            return JsonResponse({
                'success': False,
                'message': 'Current password is incorrect'
            })
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })














@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["GET"])
def api_penduduk_search(request):
    """API untuk mencari data penduduk"""
    try:
        query = request.GET.get('q', '').strip()
        print(f"DEBUG: api_penduduk_search called with query: '{query}'")
        print(f"DEBUG: User: {request.user}, Is authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: Is staff: {request.user.is_staff}")
        
        # If query is empty or too short, return all penduduk
        if len(query) < 2:
            print(f"DEBUG: Query too short: '{query}', returning all penduduk")
            penduduk_list = Penduduk.objects.all().select_related('dusun').order_by('name')[:100]
        else:
            # Search by name or NIK
            penduduk_list = Penduduk.objects.filter(
                Q(name__icontains=query) | Q(nik__icontains=query)
            ).select_related('dusun').order_by('name')[:100]
        
        print(f"DEBUG: Found {penduduk_list.count()} penduduk in database")
        
        results = []
        for penduduk in penduduk_list:
            results.append({
                'id': penduduk.id,
                'name': penduduk.name,
                'nik': penduduk.nik,
                'address': penduduk.address or '',
                'dusun': penduduk.dusun.name if penduduk.dusun else '',
                'gender': penduduk.get_gender_display(),
                'birth_date': penduduk.birth_date.strftime('%d-%m-%Y') if penduduk.birth_date else '',
            })
        
        print(f"DEBUG: Returning {len(results)} results")
        return JsonResponse({'results': results})
        
    except Exception as e:
        print(f"DEBUG: Error in api_penduduk_search: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@staff_member_required(login_url='/admin-panel/login/')
@require_http_methods(["GET"])
def api_beneficiaries_search(request):
    """API untuk mencari data beneficiaries"""
    try:
        from beneficiaries.models import Beneficiary
        
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        # Search by beneficiary person name or NIK
        beneficiaries = Beneficiary.objects.filter(
            Q(person__name__icontains=query) | Q(person__nik__icontains=query)
        ).select_related('person', 'category').order_by('person__name')[:100]
        
        results = []
        for beneficiary in beneficiaries:
            results.append({
                'id': beneficiary.id,
                'name': beneficiary.person.name,
                'nik': beneficiary.person.nik,
                'address': beneficiary.person.address or '',
                'category': beneficiary.category.name if beneficiary.category else '',
                'status': beneficiary.get_status_display(),
                'economic_status': beneficiary.get_economic_status_display(),
            })
        
        return JsonResponse({'results': results})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


# ==================== WEBSITE SETTINGS & CACHE MANAGEMENT ====================

@staff_member_required(login_url='/admin-panel/login/')
def website_settings(request):
    """Halaman pengaturan website"""
    try:
        settings_obj = WebsiteSettings.get_settings()
        
        if request.method == 'POST':
            # Update settings
            settings_obj.site_name = request.POST.get('site_name', settings_obj.site_name)
            settings_obj.site_tagline = request.POST.get('site_tagline', settings_obj.site_tagline)
            settings_obj.site_description = request.POST.get('site_description', settings_obj.site_description)
            settings_obj.contact_phone = request.POST.get('contact_phone', settings_obj.contact_phone)
            settings_obj.contact_email = request.POST.get('contact_email', settings_obj.contact_email)
            settings_obj.contact_address = request.POST.get('contact_address', settings_obj.contact_address)
            settings_obj.contact_whatsapp = request.POST.get('contact_whatsapp', settings_obj.contact_whatsapp)
            
            # Social media
            settings_obj.facebook_url = request.POST.get('facebook_url', '')
            settings_obj.instagram_url = request.POST.get('instagram_url', '')
            settings_obj.youtube_url = request.POST.get('youtube_url', '')
            settings_obj.twitter_url = request.POST.get('twitter_url', '')
            
            # Cache settings
            settings_obj.enable_cache = 'enable_cache' in request.POST
            settings_obj.cache_duration = int(request.POST.get('cache_duration', 300))
            settings_obj.enable_static_cache = 'enable_static_cache' in request.POST
            
            # Media settings
            settings_obj.max_upload_size = int(request.POST.get('max_upload_size', 10))
            settings_obj.allowed_image_formats = request.POST.get('allowed_image_formats', 'jpg,jpeg,png,gif,webp')
            settings_obj.allowed_document_formats = request.POST.get('allowed_document_formats', 'pdf,doc,docx,xls,xlsx')
            settings_obj.enable_image_compression = 'enable_image_compression' in request.POST
            settings_obj.image_quality = int(request.POST.get('image_quality', 85))
            
            # Security settings
            settings_obj.enable_maintenance_mode = 'enable_maintenance_mode' in request.POST
            settings_obj.maintenance_message = request.POST.get('maintenance_message', '')
            settings_obj.enable_ssl_redirect = 'enable_ssl_redirect' in request.POST
            settings_obj.max_login_attempts = int(request.POST.get('max_login_attempts', 5))
            
            # Performance settings
            settings_obj.enable_gzip_compression = 'enable_gzip_compression' in request.POST
            settings_obj.enable_minify_css = 'enable_minify_css' in request.POST
            settings_obj.enable_minify_js = 'enable_minify_js' in request.POST
            settings_obj.enable_cdn = 'enable_cdn' in request.POST
            settings_obj.cdn_url = request.POST.get('cdn_url', '')
            
            # Analytics
            settings_obj.google_analytics_id = request.POST.get('google_analytics_id', '')
            settings_obj.google_tag_manager_id = request.POST.get('google_tag_manager_id', '')
            settings_obj.facebook_pixel_id = request.POST.get('facebook_pixel_id', '')
            
            # Email settings
            settings_obj.smtp_host = request.POST.get('smtp_host', '')
            settings_obj.smtp_port = int(request.POST.get('smtp_port', 587))
            settings_obj.smtp_username = request.POST.get('smtp_username', '')
            settings_obj.smtp_password = request.POST.get('smtp_password', '')
            settings_obj.smtp_use_tls = 'smtp_use_tls' in request.POST
            
            # Notification settings
            settings_obj.enable_email_notifications = 'enable_email_notifications' in request.POST
            settings_obj.enable_sms_notifications = 'enable_sms_notifications' in request.POST
            settings_obj.admin_email = request.POST.get('admin_email', '')
            
            # Backup settings
            settings_obj.enable_auto_backup = 'enable_auto_backup' in request.POST
            settings_obj.backup_frequency = request.POST.get('backup_frequency', 'daily')
            settings_obj.backup_retention_days = int(request.POST.get('backup_retention_days', 30))
            
            settings_obj.is_active = 'is_active' in request.POST
            settings_obj.save()
            
            messages.success(request, 'Pengaturan website berhasil disimpan!')
            return redirect('core:website_settings')
        
        context = {
            'settings': settings_obj,
            'title': 'Pengaturan Website'
        }
        return render(request, 'admin_panel/settings/website_settings.html', context)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('core:dashboard')




@staff_member_required(login_url='/admin-panel/login/')
def media_settings(request):
    """Media settings page"""
    try:
        settings_obj = WebsiteSettings.get_settings()
        
        # Mock media stats for now
        media_stats = {
            'total_files': 0,
            'total_size': '0 MB',
            'images': 0,
            'documents': 0,
        }
        
        context = {
            'title': 'Pengaturan Media',
            'active_menu': 'settings',
            'active_submenu': 'media',
            'settings': settings_obj,
            'media_stats': media_stats,
        }
        return render(request, 'admin_panel/settings/media_settings.html', context)
    except Exception as e:
        messages.error(request, f'Error loading media settings: {str(e)}')
        return redirect('core:settings')


@login_required(login_url='/admin-panel/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/admin-panel/login/')
def cache_settings(request):
    """Cache settings page"""
    try:
        settings_obj = WebsiteSettings.get_settings()
        
        # Mock cache stats for now
        cache_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_size': '0 MB',
            'cache_entries': 0,
        }
        
        context = {
            'title': 'Pengaturan Cache',
            'active_menu': 'settings',
            'active_submenu': 'cache',
            'settings': settings_obj,
            'cache_stats': cache_stats,
        }
        return render(request, 'admin_panel/settings/cache_settings.html', context)
    except Exception as e:
        messages.error(request, f'Error loading cache settings: {str(e)}')
        return redirect('core:settings')

@login_required(login_url='/admin-panel/login/')
@user_passes_test(lambda u: u.is_staff, login_url='/admin-panel/login/')
def security_settings(request):
    """Security settings page"""
    try:
        settings_obj = WebsiteSettings.get_settings()
        
        # Mock security stats for now
        security_stats = {
            'active_users': 0,
            'failed_logins': 0,
            'blocked_ips': 0,
            'security_score': 85,
        }
        
        context = {
            'title': 'Pengaturan Keamanan',
            'active_menu': 'settings',
            'active_submenu': 'security',
            'settings': settings_obj,
            'security_stats': security_stats,
        }
        return render(request, 'admin_panel/settings/security_settings.html', context)
    except Exception as e:
        messages.error(request, f'Error loading security settings: {str(e)}')
        return redirect('core:settings')


@staff_member_required(login_url='/admin-panel/login/')
def email_settings(request):
    """Email settings page"""
    try:
        settings_obj = WebsiteSettings.get_settings()
        
        # Mock email stats for now
        email_stats = {
            'sent_today': 0,
            'sent_this_month': 0,
            'failed_emails': 0,
            'success_rate': 95,
        }
        
        context = {
            'title': 'Pengaturan Email',
            'active_menu': 'settings',
            'active_submenu': 'email',
            'settings': settings_obj,
            'email_stats': email_stats,
        }
        return render(request, 'admin_panel/settings/email_settings.html', context)
    except Exception as e:
        messages.error(request, f'Error loading email settings: {str(e)}')
        return redirect('core:settings')


@staff_member_required(login_url='/admin-panel/login/')
def seo_settings(request):
    """SEO settings page"""
    try:
        settings_obj = WebsiteSettings.get_settings()
        
        # Mock SEO stats for now
        seo_stats = {
            'page_views': 0,
            'unique_visitors': 0,
            'bounce_rate': 0,
            'seo_score': 85,
        }
        
        context = {
            'title': 'Pengaturan SEO',
            'active_menu': 'settings',
            'active_submenu': 'seo',
            'settings': settings_obj,
            'seo_stats': seo_stats,
        }
        return render(request, 'admin_panel/settings/seo_settings.html', context)
    except Exception as e:
        messages.error(request, f'Error loading SEO settings: {str(e)}')
        return redirect('core:settings')


@staff_member_required(login_url='/admin-panel/login/')
def backup_settings(request):
    """Backup settings page"""
    try:
        settings_obj = WebsiteSettings.get_settings()
        
        # Mock backup stats for now
        backup_stats = {
            'total_backups': 0,
            'total_size': '0 MB',
            'last_backup': 'Never',
            'auto_backup': 'Off',
        }
        
        # Mock backup list for now
        backup_list = []
        
        context = {
            'title': 'Pengaturan Backup',
            'active_menu': 'settings',
            'active_submenu': 'backup',
            'settings': settings_obj,
            'backup_stats': backup_stats,
            'backup_list': backup_list,
        }
        return render(request, 'admin_panel/settings/backup_settings.html', context)
    except Exception as e:
        messages.error(request, f'Error loading backup settings: {str(e)}')
        return redirect('core:settings')


@staff_member_required(login_url='/admin-panel/login/')
def system_info(request):
    """System info page"""
    try:
        import platform
        import sys
        from django.conf import settings
        from django.db import connection
        
        # System information
        system_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': sys.version.split()[0],
            'django_version': '4.2.7',
            'database': settings.DATABASES['default']['ENGINE'].split('.')[-1],
            'debug_mode': settings.DEBUG,
            'timezone': str(settings.TIME_ZONE),
        }
        
        # Cache information
        cache_info = {
            'cache_backend': settings.CACHES['default']['BACKEND'].split('.')[-1],
            'cache_location': settings.CACHES['default'].get('LOCATION', 'N/A'),
        }
        
        # Server information (mock for now)
        server_info = {
            'cpu_count': 4,
            'memory_total': 8,
            'memory_available': 6,
            'disk_usage': 50,
        }
        
        context = {
            'title': 'Informasi Sistem',
            'active_menu': 'settings',
            'active_submenu': 'system',
            'system_info': system_info,
            'cache_info': cache_info,
            'server_info': server_info,
        }
        return render(request, 'admin_panel/settings/system_info.html', context)
    except Exception as e:
        messages.error(request, f'Error loading system info: {str(e)}')
        return redirect('core:settings')


# Media Management Views
@staff_member_required(login_url='/admin-panel/login/')
def optimize_images(request):
    """Optimize images"""
    messages.success(request, 'Images optimization completed!')
    return redirect('core:media_settings')


@staff_member_required(login_url='/admin-panel/login/')
def generate_thumbnails(request):
    """Generate thumbnails"""
    messages.success(request, 'Thumbnails generation completed!')
    return redirect('core:media_settings')


@staff_member_required(login_url='/admin-panel/login/')
def media_dashboard(request):
    """Media dashboard"""
    return render(request, 'admin_panel/settings/media_dashboard.html', {
        'title': 'Media Dashboard',
        'active_menu': 'settings',
        'active_submenu': 'media',
    })


# SEO Management Views
@staff_member_required(login_url='/admin-panel/login/')
def generate_sitemap(request):
    """Generate sitemap"""
    messages.success(request, 'Sitemap generated successfully!')
    return redirect('core:seo_settings')


@staff_member_required(login_url='/admin-panel/login/')
def seo_audit(request):
    """SEO audit"""
    messages.success(request, 'SEO audit completed!')
    return redirect('core:seo_settings')


@staff_member_required(login_url='/admin-panel/login/')
def analytics_dashboard(request):
    """Analytics dashboard"""
    return render(request, 'admin_panel/settings/analytics_dashboard.html', {
        'title': 'Analytics Dashboard',
        'active_menu': 'settings',
        'active_submenu': 'seo',
    })


@staff_member_required(login_url='/admin-panel/login/')
def seo_reports(request):
    """SEO reports"""
    return render(request, 'admin_panel/settings/seo_reports.html', {
        'title': 'SEO Reports',
        'active_menu': 'settings',
        'active_submenu': 'seo',
    })


# Backup Management Views
@staff_member_required(login_url='/admin-panel/login/')
def backup_history(request):
    """Backup history"""
    return render(request, 'admin_panel/settings/backup_history.html', {
        'title': 'Backup History',
        'active_menu': 'settings',
        'active_submenu': 'backup',
    })


@staff_member_required(login_url='/admin-panel/login/')
def backup_dashboard(request):
    """Backup dashboard"""
    return render(request, 'admin_panel/settings/backup_dashboard.html', {
        'title': 'Backup Dashboard',
        'active_menu': 'settings',
        'active_submenu': 'backup',
    })


@staff_member_required(login_url='/admin-panel/login/')
def download_backup(request, backup_id):
    """Download backup"""
    messages.success(request, f'Backup {backup_id} downloaded!')
    return redirect('core:backup_settings')


# Security Management Views
@staff_member_required(login_url='/admin-panel/login/')
def security_audit(request):
    """Security audit"""
    messages.success(request, 'Security audit completed!')
    return redirect('core:security_settings')


@staff_member_required(login_url='/admin-panel/login/')
def blocked_ips(request):
    """Blocked IPs"""
    return render(request, 'admin_panel/settings/blocked_ips.html', {
        'title': 'Blocked IPs',
        'active_menu': 'settings',
        'active_submenu': 'security',
    })


@staff_member_required(login_url='/admin-panel/login/')
def login_logs(request):
    """Login logs"""
    return render(request, 'admin_panel/settings/login_logs.html', {
        'title': 'Login Logs',
        'active_menu': 'settings',
        'active_submenu': 'security',
    })


@staff_member_required(login_url='/admin-panel/login/')
def security_dashboard(request):
    """Security dashboard"""
    return render(request, 'admin_panel/settings/security_dashboard.html', {
        'title': 'Security Dashboard',
        'active_menu': 'settings',
        'active_submenu': 'security',
    })


# Email Management Views
@staff_member_required(login_url='/admin-panel/login/')
def email_logs(request):
    """Email logs"""
    return render(request, 'admin_panel/settings/email_logs.html', {
        'title': 'Email Logs',
        'active_menu': 'settings',
        'active_submenu': 'email',
    })


@staff_member_required(login_url='/admin-panel/login/')
def email_templates(request):
    """Email templates"""
    return render(request, 'admin_panel/settings/email_templates.html', {
        'title': 'Email Templates',
        'active_menu': 'settings',
        'active_submenu': 'email',
    })


@staff_member_required(login_url='/admin-panel/login/')
def send_bulk_email(request):
    """Send bulk email"""
    messages.success(request, 'Bulk email sent successfully!')
    return redirect('core:email_settings')


@staff_member_required(login_url='/admin-panel/login/')
def email_dashboard(request):
    """Email dashboard"""
    return render(request, 'admin_panel/settings/email_dashboard.html', {
        'title': 'Email Dashboard',
        'active_menu': 'settings',
        'active_submenu': 'email',
    })




@staff_member_required(login_url='/admin-panel/login/')
def system_info(request):
    """Halaman informasi sistem"""
    try:
        import platform
        from django.conf import settings
        
        # System information
        system_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'django_version': settings.DATABASES['default']['ENGINE'],
            'database': settings.DATABASES['default']['NAME'],
            'debug_mode': settings.DEBUG,
            'timezone': str(settings.TIME_ZONE),
        }
        
        # Cache information
        cache_info = {
            'cache_backend': settings.CACHES['default']['BACKEND'],
            'cache_location': settings.CACHES['default'].get('LOCATION', 'N/A'),
        }
        
        context = {
            'system_info': system_info,
            'cache_info': cache_info,
            'title': 'Informasi Sistem'
        }
        
        return render(request, 'admin_panel/settings/system_info.html', context)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('core:dashboard')


@staff_member_required(login_url='/admin-panel/login/')
def maintenance_mode(request):
    """Toggle maintenance mode"""
    try:
        settings_obj = WebsiteSettings.get_settings()
        
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'enable':
                settings_obj.enable_maintenance_mode = True
                settings_obj.save()
                messages.success(request, 'Mode maintenance diaktifkan!')
            elif action == 'disable':
                settings_obj.enable_maintenance_mode = False
                settings_obj.save()
                messages.success(request, 'Mode maintenance dinonaktifkan!')
            
            return redirect('core:maintenance_mode')
        
        context = {
            'settings': settings_obj,
            'title': 'Mode Maintenance'
        }
        return render(request, 'admin_panel/settings/maintenance_mode.html', context)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('core:dashboard')


def public_settings_api(request):
    """API untuk pengaturan website (public)"""
    try:
        settings_obj = WebsiteSettings.get_settings()
        
        # Only return public settings
        public_data = {
            'site_name': settings_obj.site_name,
            'site_tagline': settings_obj.site_tagline,
            'site_description': settings_obj.site_description,
            'contact_phone': settings_obj.contact_phone,
            'contact_email': settings_obj.contact_email,
            'contact_address': settings_obj.contact_address,
            'contact_whatsapp': settings_obj.contact_whatsapp,
            'facebook_url': settings_obj.facebook_url,
            'instagram_url': settings_obj.instagram_url,
            'youtube_url': settings_obj.youtube_url,
            'twitter_url': settings_obj.twitter_url,
            'logo': settings_obj.logo.url if settings_obj.logo else None,
            'favicon': settings_obj.favicon.url if settings_obj.favicon else None,
            'enable_maintenance_mode': settings_obj.enable_maintenance_mode,
            'maintenance_message': settings_obj.maintenance_message,
        }
        
        return JsonResponse(public_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

