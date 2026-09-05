from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
import uuid

User = get_user_model()

class TourismPageHeader(models.Model):
    title = models.CharField(
        max_length=200, 
        default='Wisata Desa', 
        verbose_name="Judul Halaman"
    )
    description = models.TextField(
        default='Jelajahi keindahan alam, kekayaan budaya, dan kelezatan kuliner yang menanti Anda di setiap sudut desa kami.',
        verbose_name="Deskripsi Halaman"
    )
    background_image = models.ImageField(
        upload_to='tourism/page_headers/', 
        blank=True, 
        null=True, 
        verbose_name="Gambar Background"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Header Halaman Wisata"
        verbose_name_plural = "Header Halaman Wisata"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class TourismCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nama Kategori")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug URL", blank=True, null=True)
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icon FontAwesome")
    color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Warna")
    image = models.ImageField(upload_to='tourism/categories/', blank=True, null=True, verbose_name="Gambar Kategori")
    video = models.FileField(upload_to='tourism/categories/videos/', blank=True, null=True, verbose_name="Video Kategori")
    youtube_link = models.URLField(blank=True, null=True, verbose_name="Link YouTube")
    hero_image = models.ImageField(upload_to='tourism/categories/hero/', blank=True, null=True, verbose_name="Gambar Hero")
    hero_video = models.FileField(upload_to='tourism/categories/hero/videos/', blank=True, null=True, verbose_name="Video Hero")
    hero_youtube = models.URLField(blank=True, null=True, verbose_name="YouTube Hero")
    
    # SEO dan Meta
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_featured = models.BooleanField(default=False, verbose_name="Kategori Unggulan")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kategori Wisata"
        verbose_name_plural = "Kategori Wisata"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    @property
    def location_count(self):
        """Return the number of locations in this category"""
        return self.tourismlocation_set.filter(is_active=True).count()

class TourismLocation(models.Model):
    LOCATION_TYPE_CHOICES = [
        ('natural', 'Wisata Alam'),
        ('cultural', 'Wisata Budaya'),
        ('historical', 'Wisata Sejarah'),
        ('religious', 'Wisata Religi'),
        ('culinary', 'Wisata Kuliner'),
        ('adventure', 'Wisata Petualangan'),
        ('education', 'Wisata Edukasi'),
        ('other', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Dipublikasi'),
        ('archived', 'Diarsipkan'),
    ]

    title = models.CharField(max_length=200, verbose_name="Judul Wisata")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug URL", blank=True, default='')
    category = models.ForeignKey(TourismCategory, on_delete=models.CASCADE, verbose_name="Kategori")
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES, default='natural', verbose_name="Jenis Wisata")
    
    # Deskripsi
    short_description = models.TextField(max_length=500, verbose_name="Deskripsi Singkat")
    full_description = models.TextField(verbose_name="Deskripsi Lengkap")
    
    # Lokasi
    address = models.TextField(verbose_name="Alamat Lengkap")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Longitude")
    
    # Informasi Wisata
    opening_hours = models.CharField(max_length=200, blank=True, verbose_name="Jam Buka")
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Biaya Masuk")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Nomor Telepon")
    contact_email = models.EmailField(blank=True, verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Website")
    
    # Fitur dan Fasilitas
    facilities = models.TextField(default='[]', blank=True, verbose_name="Fasilitas", help_text='List of facilities in JSON format')
    activities = models.TextField(default='[]', blank=True, verbose_name="Aktivitas yang Tersedia", help_text='List of activities in JSON format')
    
    # Status dan Meta
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    featured = models.BooleanField(default=False, verbose_name="Wisata Unggulan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Gambar Utama
    main_image = models.ImageField(upload_to='tourism/locations/', null=True, blank=True, verbose_name="Gambar Utama")
    hero_image = models.ImageField(upload_to='tourism/locations/hero/', blank=True, null=True, verbose_name="Gambar Hero")
    hero_video = models.FileField(upload_to='tourism/locations/hero/videos/', blank=True, null=True, verbose_name="Video Hero")
    hero_youtube = models.URLField(blank=True, null=True, verbose_name="YouTube Hero")
    
    # SEO dan Meta
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")
    
    # Timestamps
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tourism_created', verbose_name="Dibuat Oleh")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tourism_updated', verbose_name="Diupdate Oleh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Tanggal Publikasi")

    class Meta:
        verbose_name = "Lokasi Wisata"
        verbose_name_plural = "Lokasi Wisata"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while TourismLocation.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('tourism:location_detail', kwargs={'slug': self.slug})
            
    @property
    def get_featured_image(self):
        """Return the featured image for this location"""
        if self.main_image:
            return self.main_image.url
        
        # Try to get a featured image from gallery
        featured_image = self.gallery.filter(is_active=True, is_featured=True, media_type='image').first()
        if featured_image and featured_image.image:
            return featured_image.image.url
        
        # Otherwise get the first image from gallery
        first_image = self.gallery.filter(is_active=True, media_type='image').first()
        if first_image and first_image.image:
            return first_image.image.url
        
        # Return a placeholder if no image is available
        return '/static/img/placeholder.jpg'
    
    @property
    def location_type_display(self):
        """Return the display value of location_type"""
        return dict(self.LOCATION_TYPE_CHOICES).get(self.location_type, self.location_type)
        
    @property
    def average_rating(self):
        """Calculate the average rating for this location"""
        from django.db.models import Avg
        # Get average from TourismReview
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        return 0

    @property
    def total_reviews(self):
        return self.ratings.count()
        

class TourismGallery(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Gambar'),
        ('video', 'Video'),
        ('360', 'Foto 360°'),
    ]

    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='gallery', verbose_name="Lokasi Wisata", null=True, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image', verbose_name="Jenis Media")
    title = models.CharField(max_length=200, verbose_name="Judul")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    
    # Media files
    image = models.ImageField(upload_to='tourism/gallery/', null=True, blank=True, verbose_name="Gambar")
    video_url = models.URLField(blank=True, verbose_name="URL Video")
    video_file = models.FileField(upload_to='tourism/videos/', null=True, blank=True, verbose_name="File Video")
    
    # Metadata
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Alt Text")
    caption = models.CharField(max_length=300, blank=True, verbose_name="Caption")
    is_featured = models.BooleanField(default=False, verbose_name="Gambar Unggulan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Ordering
    order = models.PositiveIntegerField(default=0, verbose_name="Urutan")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Galeri Wisata"
        verbose_name_plural = "Galeri Wisata"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.tourism_location.title}"

class TourismReview(models.Model):
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='reviews', verbose_name="Lokasi Wisata")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Pengguna")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Rating")
    title = models.CharField(max_length=200, verbose_name="Judul Review")
    comment = models.TextField(verbose_name="Komentar")
    
    # Review details
    visit_date = models.DateField(null=True, blank=True, verbose_name="Tanggal Kunjungan")
    visit_type = models.CharField(max_length=20, choices=[
        ('personal', 'Pribadi'),
        ('family', 'Keluarga'),
        ('group', 'Grup'),
        ('business', 'Bisnis'),
    ], default='personal', verbose_name="Jenis Kunjungan")
    
    # Moderation
    is_approved = models.BooleanField(default=False, verbose_name="Disetujui")
    is_flagged = models.BooleanField(default=False, verbose_name="Ditandai")
    flagged_reason = models.TextField(blank=True, verbose_name="Alasan Ditandai")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review Wisata"
        verbose_name_plural = "Review Wisata"
        ordering = ['-created_at']
        # Remove unique_together constraint since we now support anonymous reviews

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.tourism_location.title}"
        else:
            return f"Anonim - {self.tourism_location.title}"

class TourismRating(models.Model):
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='ratings', verbose_name="Lokasi Wisata")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Pengguna")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Rating")
    
    # Rating categories
    cleanliness = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Kebersihan")
    accessibility = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Aksesibilitas")
    facilities = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Fasilitas")
    service = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Pelayanan")
    value = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Nilai")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rating Wisata"
        verbose_name_plural = "Rating Wisata"
        unique_together = ['tourism_location', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.tourism_location.title} ({self.rating}/5)"

class TourismEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('festival', 'Festival'),
        ('exhibition', 'Pameran'),
        ('workshop', 'Workshop'),
        ('competition', 'Kompetisi'),
        ('ceremony', 'Upacara'),
        ('other', 'Lainnya'),
    ]

    title = models.CharField(max_length=200, verbose_name="Judul Event")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug URL", blank=True, null=True)
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='events', verbose_name="Lokasi Wisata")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='festival', verbose_name="Jenis Event")
    
    # Event details
    description = models.TextField(verbose_name="Deskripsi Event")
    start_date = models.DateTimeField(verbose_name="Tanggal Mulai")
    end_date = models.DateTimeField(verbose_name="Tanggal Selesai")
    start_time = models.TimeField(blank=True, null=True, verbose_name="Waktu Mulai")
    end_time = models.TimeField(blank=True, null=True, verbose_name="Waktu Selesai")
    
    # Event info
    organizer = models.CharField(max_length=200, blank=True, verbose_name="Penyelenggara")
    contact_person = models.CharField(max_length=200, blank=True, verbose_name="Kontak Person")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Nomor Telepon")
    email = models.EmailField(blank=True, verbose_name="Email")
    contact_info = models.TextField(blank=True, verbose_name="Informasi Kontak")
    registration_required = models.BooleanField(default=False, verbose_name="Pendaftaran Diperlukan")
    registration_deadline = models.DateTimeField(blank=True, null=True, verbose_name="Deadline Pendaftaran")
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name="Maksimal Peserta")
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Biaya Pendaftaran")
    registration_link = models.URLField(blank=True, verbose_name="Link Pendaftaran")
    
    # Media
    image = models.ImageField(upload_to='tourism/events/', blank=True, null=True, verbose_name="Gambar Event")
    hero_image = models.ImageField(upload_to='tourism/events/hero/', blank=True, null=True, verbose_name="Gambar Hero")
    hero_video = models.FileField(upload_to='tourism/events/hero/videos/', blank=True, null=True, verbose_name="Video Hero")
    hero_youtube = models.URLField(blank=True, null=True, verbose_name="YouTube Hero")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_featured = models.BooleanField(default=False, verbose_name="Event Unggulan")
    
    # Timestamps
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tourism_events_created', verbose_name="Dibuat Oleh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Wisata"
        verbose_name_plural = "Event Wisata"
        ordering = ['start_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.tourism_location.title}"

class TourismPackage(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('day_trip', 'Perjalanan Sehari'),
        ('weekend', 'Paket Weekend'),
        ('week_long', 'Paket Seminggu'),
        ('custom', 'Paket Kustom'),
    ]

    title = models.CharField(max_length=200, verbose_name="Judul Paket")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug URL", blank=True, null=True)
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='packages', verbose_name="Lokasi Wisata")
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES, default='day_trip', verbose_name="Jenis Paket")
    
    # Package details
    description = models.TextField(verbose_name="Deskripsi Paket")
    duration = models.CharField(max_length=100, verbose_name="Durasi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Harga")
    currency = models.CharField(max_length=3, default='IDR', verbose_name="Mata Uang")
    
    # Contact info
    whatsapp = models.CharField(max_length=20, blank=True, null=True, verbose_name="Nomor WhatsApp")
    
    # Media
    image = models.ImageField(upload_to='tourism/packages/', null=True, blank=True, verbose_name="Gambar Paket")
    video = models.FileField(upload_to='tourism/packages/videos/', null=True, blank=True, verbose_name="Video Paket")
    youtube_link = models.URLField(blank=True, null=True, verbose_name="Link YouTube")
    hero_image = models.ImageField(upload_to='tourism/packages/hero/', blank=True, null=True, verbose_name="Gambar Hero")
    hero_video = models.FileField(upload_to='tourism/packages/hero/videos/', blank=True, null=True, verbose_name="Video Hero")
    hero_youtube = models.URLField(blank=True, null=True, verbose_name="YouTube Hero")
    
    # Package features
    includes = models.TextField(default='[]', verbose_name="Yang Termasuk", help_text='Included items in JSON format')
    excludes = models.TextField(default='[]', verbose_name="Yang Tidak Termasuk", help_text='Excluded items in JSON format')
    itinerary = models.TextField(default='[]', verbose_name="Itinerary", help_text='Itinerary in JSON format')
    
    # Booking info
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name="Maksimal Peserta")
    min_participants = models.PositiveIntegerField(default=1, verbose_name="Minimal Peserta")
    booking_deadline = models.PositiveIntegerField(default=7, verbose_name="Deadline Booking (hari)")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_featured = models.BooleanField(default=False, verbose_name="Paket Unggulan")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paket Wisata"
        verbose_name_plural = "Paket Wisata"
        ordering = ['price']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.tourism_location.title}"

class TourismPackageGallery(models.Model):
    package = models.ForeignKey(TourismPackage, on_delete=models.CASCADE, related_name='gallery', verbose_name="Paket Wisata", null=True, blank=True)
    image = models.ImageField(upload_to='tourism/packages/gallery/', verbose_name="Gambar")
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Judul Gambar")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi Gambar")
    order = models.PositiveIntegerField(default=0, verbose_name="Urutan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Galeri Paket Wisata"
        verbose_name_plural = "Galeri Paket Wisata"
        ordering = ['order']

    def __str__(self):
        return f"Gambar {self.order} - {self.package.title}"

class TourismFAQ(models.Model):
    tourism_location = models.ForeignKey(TourismLocation, on_delete=models.CASCADE, related_name='faqs', verbose_name="Lokasi Wisata")
    question = models.TextField(verbose_name="Pertanyaan")
    answer = models.TextField(verbose_name="Jawaban")
    
    # FAQ metadata
    category = models.CharField(max_length=100, blank=True, verbose_name="Kategori")
    priority = models.PositiveIntegerField(default=3, verbose_name="Prioritas", help_text="1 = Sangat Penting, 5 = Tidak Penting")
    tags = models.CharField(max_length=255, blank=True, verbose_name="Tags", help_text="Pisahkan dengan koma")
    order = models.PositiveIntegerField(default=0, verbose_name="Urutan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_featured = models.BooleanField(default=False, verbose_name="FAQ Unggulan")
    
    # Media
    image = models.ImageField(upload_to='tourism/faqs/', blank=True, null=True, verbose_name="Gambar FAQ")
    video = models.FileField(upload_to='tourism/faqs/videos/', blank=True, null=True, verbose_name="Video FAQ")
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0, verbose_name="Jumlah Dilihat")
    helpful_count = models.PositiveIntegerField(default=0, verbose_name="Jumlah Membantu")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ Wisata"
        verbose_name_plural = "FAQ Wisata"
        ordering = ['order', 'question']

    def __str__(self):
        return f"{self.question[:50]}... - {self.tourism_location.title}"
    
    @property
    def tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

class TourismSettings(models.Model):
    """Model untuk konfigurasi dinamis tourism"""
    # Dashboard Limits
    featured_locations_limit = models.PositiveIntegerField(default=6, verbose_name="Limit Destinasi Unggulan")
    categories_limit = models.PositiveIntegerField(default=8, verbose_name="Limit Kategori")
    upcoming_events_limit = models.PositiveIntegerField(default=4, verbose_name="Limit Event Mendatang")
    featured_packages_limit = models.PositiveIntegerField(default=4, verbose_name="Limit Paket Unggulan")
    
    # Pagination Settings
    locations_per_page = models.PositiveIntegerField(default=12, verbose_name="Lokasi per Halaman")
    packages_per_page = models.PositiveIntegerField(default=12, verbose_name="Paket per Halaman")
    events_per_page = models.PositiveIntegerField(default=12, verbose_name="Event per Halaman")
    admin_items_per_page = models.PositiveIntegerField(default=20, verbose_name="Item Admin per Halaman")
    
    # Review Settings
    reviews_per_page = models.PositiveIntegerField(default=10, verbose_name="Review per Halaman")
    related_locations_limit = models.PositiveIntegerField(default=4, verbose_name="Limit Lokasi Terkait")
    related_packages_limit = models.PositiveIntegerField(default=6, verbose_name="Limit Paket Terkait")
    
    # Price Range Settings (JSON format)
    price_ranges = models.JSONField(
        default=list,
        verbose_name="Rentang Harga",
        help_text="Format: [{'label': '0-100K', 'min': 0, 'max': 100000}, ...]"
    )
    
    # Duration Settings (JSON format)
    duration_filters = models.JSONField(
        default=list,
        verbose_name="Filter Durasi",
        help_text="Format: [{'label': '1 Hari', 'value': '1 hari'}, ...]"
    )
    
    # Time Filter Settings
    time_filters = models.JSONField(
        default=list,
        verbose_name="Filter Waktu",
        help_text="Format: [{'label': 'Akan Datang', 'value': 'upcoming'}, ...]"
    )
    
    # Sort Options (JSON format)
    sort_options = models.JSONField(
        default=list,
        verbose_name="Opsi Sorting",
        help_text="Format: [{'label': 'Nama A-Z', 'value': 'name'}, ...]"
    )
    
    # Contact Settings
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name="Nomor WhatsApp")
    whatsapp_message_template = models.TextField(
        default="Halo, saya tertarik dengan {item_name}",
        verbose_name="Template Pesan WhatsApp"
    )
    
    # Statistics Settings
    enable_real_statistics = models.BooleanField(default=True, verbose_name="Aktifkan Statistik Real")
    cache_statistics_duration = models.PositiveIntegerField(default=300, verbose_name="Durasi Cache Statistik (detik)")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pengaturan Wisata"
        verbose_name_plural = "Pengaturan Wisata"
        ordering = ['-created_at']
    
    def __str__(self):
        return "Pengaturan Wisata"
    
    @classmethod
    def get_settings(cls):
        """Get or create settings instance"""
        settings, created = cls.objects.get_or_create(is_active=True)
        if created:
            # Set default values
            settings.price_ranges = [
                {'label': '0-100K', 'min': 0, 'max': 100000},
                {'label': '100K-500K', 'min': 100000, 'max': 500000},
                {'label': '500K-1M', 'min': 500000, 'max': 1000000},
                {'label': '1M+', 'min': 1000000, 'max': None}
            ]
            settings.duration_filters = [
                {'label': '1 Hari', 'value': '1 hari'},
                {'label': '2 Hari', 'value': '2 hari'},
                {'label': '3 Hari', 'value': '3 hari'},
                {'label': '4+ Hari', 'value': '4+'}
            ]
            settings.time_filters = [
                {'label': 'Akan Datang', 'value': 'upcoming'},
                {'label': 'Sedang Berlangsung', 'value': 'ongoing'},
                {'label': 'Selesai', 'value': 'past'}
            ]
            settings.sort_options = [
                {'label': 'Terbaru', 'value': '-created_at'},
                {'label': 'Nama A-Z', 'value': 'title'},
                {'label': 'Nama Z-A', 'value': '-title'},
                {'label': 'Rating Tertinggi', 'value': 'rating'},
                {'label': 'Harga Terendah', 'value': 'price'},
                {'label': 'Harga Tertinggi', 'value': '-price'}
            ]
            settings.save()
        return settings

class TourismDashboard(models.Model):
    """Model untuk mengelola dashboard wisata"""
    title = models.CharField(max_length=200, default="Wisata Desa Pulosarok", verbose_name="Judul Dashboard")
    subtitle = models.CharField(max_length=300, blank=True, verbose_name="Sub Judul")
    description = models.TextField(
        default="Jelajahi keindahan alam, kekayaan budaya, dan kelezatan kuliner yang menanti Anda di setiap sudut desa kami.",
        verbose_name="Deskripsi"
    )
    
    # Background Images
    hero_background = models.ImageField(
        upload_to='tourism/dashboard/hero/', 
        blank=True, null=True, 
        verbose_name="Background Hero"
    )
    hero_video = models.FileField(
        upload_to='tourism/dashboard/hero/videos/', 
        blank=True, null=True, 
        verbose_name="Video Hero"
    )
    hero_youtube = models.URLField(blank=True, null=True, verbose_name="YouTube Hero")
    
    # Section Backgrounds
    featured_bg = models.ImageField(
        upload_to='tourism/dashboard/sections/', 
        blank=True, null=True, 
        verbose_name="Background Destinasi Unggulan"
    )
    categories_bg = models.ImageField(
        upload_to='tourism/dashboard/sections/', 
        blank=True, null=True, 
        verbose_name="Background Kategori"
    )
    events_bg = models.ImageField(
        upload_to='tourism/dashboard/sections/', 
        blank=True, null=True, 
        verbose_name="Background Event"
    )
    packages_bg = models.ImageField(
        upload_to='tourism/dashboard/sections/', 
        blank=True, null=True, 
        verbose_name="Background Paket"
    )
    
    # Colors and Styling
    primary_color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Warna Primer")
    secondary_color = models.CharField(max_length=7, default="#10B981", verbose_name="Warna Sekunder")
    accent_color = models.CharField(max_length=7, default="#8B5CF6", verbose_name="Warna Aksen")
    
    # Statistics Display
    show_statistics = models.BooleanField(default=True, verbose_name="Tampilkan Statistik")
    show_featured_locations = models.BooleanField(default=True, verbose_name="Tampilkan Destinasi Unggulan")
    show_categories = models.BooleanField(default=True, verbose_name="Tampilkan Kategori")
    show_events = models.BooleanField(default=True, verbose_name="Tampilkan Event")
    show_packages = models.BooleanField(default=True, verbose_name="Tampilkan Paket")
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name="Meta Keywords")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard Wisata"
        verbose_name_plural = "Dashboard Wisata"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Generate meta fields if not provided
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.description[:160]
        super().save(*args, **kwargs)