"""
Script untuk membuat data dummy wisata Pulosarok Aceh Singkil
Jalankan dengan: python manage.py shell < dumppy/create_tourism_data.py
"""

import json
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from tourism.models import (
    TourismCategory, TourismLocation, TourismGallery, 
    TourismPackage, TourismEvent, TourismFAQ
)

User = get_user_model()

def create_tourism_categories():
    """Membuat kategori wisata"""
    categories_data = [
        {
            'name': 'Wisata Pantai',
            'description': 'Destinasi wisata pantai dengan keindahan alam laut',
            'icon': 'fas fa-water',
            'color': '#3B82F6',
            'is_featured': True
        },
        {
            'name': 'Wisata Pulau',
            'description': 'Pulau-pulau eksotis di Kepulauan Banyak',
            'icon': 'fas fa-island-tropical',
            'color': '#10B981',
            'is_featured': True
        },
        {
            'name': 'Wisata Alam',
            'description': 'Destinasi wisata alam dengan keindahan hutan dan mangrove',
            'icon': 'fas fa-tree',
            'color': '#059669',
            'is_featured': True
        },
        {
            'name': 'Wisata Edukasi',
            'description': 'Destinasi wisata edukasi dan konservasi',
            'icon': 'fas fa-graduation-cap',
            'color': '#8B5CF6',
            'is_featured': False
        },
        {
            'name': 'Wisata Petualangan',
            'description': 'Destinasi wisata petualangan dan diving',
            'icon': 'fas fa-mountain',
            'color': '#F59E0B',
            'is_featured': False
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = TourismCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories.append(category)
        print(f"Kategori '{category.name}' {'dibuat' if created else 'sudah ada'}")
    
    return categories

def create_tourism_locations():
    """Membuat 15 data lokasi wisata Pulosarok Aceh Singkil"""
    
    # Get categories
    pantai_cat = TourismCategory.objects.get(name='Wisata Pantai')
    pulau_cat = TourismCategory.objects.get(name='Wisata Pulau')
    alam_cat = TourismCategory.objects.get(name='Wisata Alam')
    edukasi_cat = TourismCategory.objects.get(name='Wisata Edukasi')
    petualangan_cat = TourismCategory.objects.get(name='Wisata Petualangan')
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@pulosarok.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    locations_data = [
        {
            'title': 'Pantai Pulo Sarok',
            'category': pantai_cat,
            'location_type': 'natural',
            'short_description': 'Pantai favorit masyarakat lokal dengan berbagai sarana hiburan dan pondok peristirahatan',
            'full_description': '''Pantai Pulo Sarok merupakan destinasi wisata pantai yang sangat populer di Aceh Singkil. 
            Pantai ini terletak strategis di antara Pelabuhan PT ASDP Ferry dan Pelabuhan Cargo Syahbandar, 
            menjadikannya mudah diakses oleh wisatawan. Pantai ini menawarkan berbagai fasilitas hiburan 
            seperti permainan anak-anak, pondok peristirahatan, dan area bersantai yang nyaman. 
            Air lautnya yang jernih dan pasir pantai yang bersih membuat tempat ini cocok untuk 
            liburan keluarga dan rekreasi.''',
            'address': 'Pulo Sarok, Kecamatan Singkil, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.2875,
            'longitude': 97.7847,
            'opening_hours': '24 Jam',
            'entry_fee': 0,
            'contact_phone': '0852-1234-5678',
            'facilities': json.dumps([
                'Pondok peristirahatan',
                'Area parkir',
                'Toilet umum',
                'Warung makan',
                'Permainan anak',
                'Area bersantai'
            ]),
            'activities': json.dumps([
                'Berenang',
                'Berjemur',
                'Bersantai',
                'Fotografi',
                'Makan seafood',
                'Bermain di pantai'
            ]),
            'featured': True,
            'status': 'published'
        },
        {
            'title': 'Hutan Mangrove Pulo Sarok',
            'category': alam_cat,
            'location_type': 'natural',
            'short_description': 'Destinasi wisata alam dengan keindahan hutan mangrove yang dikelilingi sungai dan laut',
            'full_description': '''Hutan Mangrove Pulo Sarok menawarkan pengalaman wisata alam yang unik dengan 
            ekosistem mangrove yang terjaga. Wisatawan dapat menikmati keindahan alam sambil belajar tentang 
            pentingnya konservasi mangrove. Fasilitas yang tersedia meliputi kafetaria dan toko suvenir 
            yang menjual produk khas seperti Lokan Krispi. Hutan mangrove ini juga menjadi habitat bagi 
            berbagai jenis burung dan satwa liar lainnya.''',
            'address': 'Pulo Sarok, Kecamatan Singkil, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.2900,
            'longitude': 97.7800,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 15000,
            'contact_phone': '0852-1234-5679',
            'facilities': json.dumps([
                'Kafetaria',
                'Toko suvenir',
                'Jalur tracking',
                'Area edukasi',
                'Toilet umum',
                'Area parkir'
            ]),
            'activities': json.dumps([
                'Tracking mangrove',
                'Bird watching',
                'Fotografi alam',
                'Belajar konservasi',
                'Membeli suvenir',
                'Makan di kafetaria'
            ]),
            'featured': True,
            'status': 'published'
        },
        {
            'title': 'Pulau Bengkaru',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau eksotis di Kepulauan Banyak dengan pantai indah dan kegiatan wisata tirta',
            'full_description': '''Pulau Bengkaru merupakan salah satu pulau terindah di Kepulauan Banyak yang 
            menawarkan keindahan alam bawah laut yang spektakuler. Pulau ini terkenal dengan pantai berpasir 
            putih yang bersih dan air laut yang sangat jernih. Wisatawan dapat menikmati berbagai aktivitas 
            seperti snorkeling, diving, dan berjemur di pantai. Pulau ini juga memiliki ekosistem terumbu 
            karang yang masih terjaga dengan baik.''',
            'address': 'Kepulauan Banyak, Kecamatan Pulau Banyak Barat, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.1000,
            'longitude': 97.2000,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 25000,
            'contact_phone': '0852-1234-5680',
            'facilities': json.dumps([
                'Pondok wisata',
                'Peralatan snorkeling',
                'Peralatan diving',
                'Toilet umum',
                'Area parkir kapal',
                'Warung makan'
            ]),
            'activities': json.dumps([
                'Snorkeling',
                'Diving',
                'Berjemur',
                'Fotografi bawah laut',
                'Tracking pulau',
                'Bersantai di pantai'
            ]),
            'featured': True,
            'status': 'published'
        },
        {
            'title': 'Pulau Pandan',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau dengan pantai indah dan fasilitas lengkap termasuk toilet umum dan jalur evakuasi',
            'full_description': '''Pulau Pandan menawarkan pengalaman wisata pantai yang nyaman dengan fasilitas 
            yang cukup lengkap. Pulau ini memiliki pantai berpasir putih yang indah dengan air laut yang 
            jernih. Fasilitas yang tersedia meliputi toilet umum, jalur evakuasi, dan area bersantai. 
            Pulau ini cocok untuk wisatawan yang ingin menikmati keindahan alam sambil tetap merasa nyaman 
            dengan fasilitas yang memadai.''',
            'address': 'Asantola, Pulau Banyak Barat, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.1200,
            'longitude': 97.2500,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 20000,
            'contact_phone': '0852-1234-5681',
            'facilities': json.dumps([
                'Toilet umum',
                'Jalur evakuasi',
                'Area bersantai',
                'Pondok wisata',
                'Area parkir kapal',
                'Warung makan'
            ]),
            'activities': json.dumps([
                'Berjemur',
                'Berenang',
                'Fotografi',
                'Bersantai',
                'Tracking pulau',
                'Makan seafood'
            ]),
            'featured': False,
            'status': 'published'
        },
        {
            'title': 'Pulau Sikandang',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau dengan wisata alam yang menawarkan fasilitas toilet umum dan tempat ibadah',
            'full_description': '''Pulau Sikandang merupakan destinasi wisata alam yang menawarkan keindahan 
            alam yang masih alami. Pulau ini dilengkapi dengan fasilitas dasar seperti toilet umum dan 
            tempat ibadah, sehingga wisatawan dapat menikmati keindahan alam sambil tetap merasa nyaman. 
            Pulau ini cocok untuk wisatawan yang ingin menikmati keindahan alam yang masih terjaga keasliannya.''',
            'address': 'Kecamatan Pulau Banyak Barat, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.1500,
            'longitude': 97.3000,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 15000,
            'contact_phone': '0852-1234-5682',
            'facilities': json.dumps([
                'Toilet umum',
                'Tempat ibadah',
                'Area bersantai',
                'Pondok wisata',
                'Area parkir kapal'
            ]),
            'activities': json.dumps([
                'Tracking alam',
                'Fotografi',
                'Bersantai',
                'Beribadah',
                'Bird watching',
                'Menikmati keindahan alam'
            ]),
            'featured': False,
            'status': 'published'
        },
        {
            'title': 'Budidaya dan Penetasan Penyu Pulo Bangkaru',
            'category': edukasi_cat,
            'location_type': 'education',
            'short_description': 'Destinasi wisata edukasi yang menawarkan pengalaman melihat proses budidaya dan penetasan penyu',
            'full_description': '''Destinasi wisata edukasi yang unik ini menawarkan pengalaman langsung melihat 
            proses budidaya dan penetasan penyu. Wisatawan dapat belajar tentang konservasi penyu dan 
            pentingnya menjaga kelestarian satwa laut. Fasilitas edukasi yang tersedia meliputi area 
            penetasan, kolam budidaya, dan area edukasi yang informatif. Destinasi ini sangat cocok 
            untuk wisata edukasi keluarga dan kelompok sekolah.''',
            'address': 'Pulo Bangkaru, Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.0800,
            'longitude': 97.1500,
            'opening_hours': '08:00 - 17:00',
            'entry_fee': 30000,
            'contact_phone': '0852-1234-5683',
            'facilities': json.dumps([
                'Area penetasan penyu',
                'Kolam budidaya',
                'Area edukasi',
                'Panduan wisata',
                'Toilet umum',
                'Area parkir'
            ]),
            'activities': json.dumps([
                'Belajar konservasi penyu',
                'Melihat penetasan',
                'Edukasi lingkungan',
                'Fotografi edukasi',
                'Interaksi dengan penyu',
                'Belajar budidaya'
            ]),
            'featured': True,
            'status': 'published'
        },
        {
            'title': 'Pulau Panjang',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau dengan keindahan pantai, fasilitas penginapan, dan atraksi hiburan',
            'full_description': '''Pulau Panjang menawarkan pengalaman wisata yang lengkap dengan keindahan 
            pantai yang memukau, fasilitas penginapan yang nyaman, dan berbagai atraksi hiburan. 
            Pulau ini cocok untuk wisatawan yang ingin menghabiskan waktu lebih lama untuk menikmati 
            keindahan alam. Fasilitas penginapan yang tersedia memungkinkan wisatawan untuk menginap 
            dan menikmati keindahan pulau selama beberapa hari.''',
            'address': 'Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.2000,
            'longitude': 97.3500,
            'opening_hours': '24 Jam',
            'entry_fee': 35000,
            'contact_phone': '0852-1234-5684',
            'facilities': json.dumps([
                'Penginapan',
                'Restoran',
                'Atraksi hiburan',
                'Area pantai',
                'Toilet umum',
                'Area parkir kapal'
            ]),
            'activities': json.dumps([
                'Menginap',
                'Berenang',
                'Hiburan',
                'Makan di restoran',
                'Bersantai',
                'Fotografi'
            ]),
            'featured': True,
            'status': 'published'
        },
        {
            'title': 'Pulau Tailana',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau dengan pemandangan alam bawah laut yang spektakuler',
            'full_description': '''Pulau Tailana terkenal dengan pemandangan alam bawah laut yang sangat 
            spektakuler. Pulau ini menawarkan keindahan terumbu karang yang masih terjaga dengan baik 
            dan berbagai jenis ikan laut yang berwarna-warni. Wisatawan dapat menikmati aktivitas 
            snorkeling dan diving untuk melihat keindahan bawah laut yang menakjubkan.''',
            'address': 'Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.1800,
            'longitude': 97.2800,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 25000,
            'contact_phone': '0852-1234-5685',
            'facilities': json.dumps([
                'Peralatan snorkeling',
                'Peralatan diving',
                'Pondok wisata',
                'Toilet umum',
                'Area parkir kapal'
            ]),
            'activities': json.dumps([
                'Snorkeling',
                'Diving',
                'Fotografi bawah laut',
                'Berjemur',
                'Bersantai',
                'Menikmati keindahan alam'
            ]),
            'featured': False,
            'status': 'published'
        },
        {
            'title': 'Pulau Palambak',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau dengan pantai berpasir putih dan air laut yang jernih',
            'full_description': '''Pulau Palambak menawarkan keindahan pantai berpasir putih yang sangat 
            bersih dengan air laut yang jernih. Pulau ini cocok untuk wisatawan yang ingin menikmati 
            keindahan alam sambil bersantai. Pantai yang bersih dan air laut yang jernih membuat 
            tempat ini sangat cocok untuk berenang dan berjemur.''',
            'address': 'Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.2500,
            'longitude': 97.4000,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 20000,
            'contact_phone': '0852-1234-5686',
            'facilities': json.dumps([
                'Area pantai',
                'Pondok wisata',
                'Toilet umum',
                'Area parkir kapal',
                'Warung makan'
            ]),
            'activities': json.dumps([
                'Berenang',
                'Berjemur',
                'Bersantai',
                'Fotografi',
                'Makan seafood',
                'Menikmati keindahan alam'
            ]),
            'featured': False,
            'status': 'published'
        },
        {
            'title': 'Pulau Asok',
            'category': petualangan_cat,
            'location_type': 'adventure',
            'short_description': 'Pulau dengan keindahan alam dan fasilitas menyewakan peralatan diving lengkap',
            'full_description': '''Pulau Asok merupakan destinasi wisata petualangan yang menawarkan keindahan 
            alam yang memukau. Pulau ini dilengkapi dengan fasilitas menyewakan peralatan diving yang 
            lengkap, sehingga wisatawan dapat menikmati aktivitas diving dengan aman dan nyaman. 
            Pulau ini cocok untuk wisatawan yang menyukai petualangan bawah laut.''',
            'address': 'Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.3000,
            'longitude': 97.4500,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 40000,
            'contact_phone': '0852-1234-5687',
            'facilities': json.dumps([
                'Peralatan diving lengkap',
                'Panduan diving',
                'Pondok wisata',
                'Toilet umum',
                'Area parkir kapal',
                'Restoran'
            ]),
            'activities': json.dumps([
                'Diving',
                'Snorkeling',
                'Fotografi bawah laut',
                'Petualangan',
                'Bersantai',
                'Menikmati keindahan alam'
            ]),
            'featured': True,
            'status': 'published'
        },
        {
            'title': 'Pulau Lambudung',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau dengan keindahan pantai pasir putih dan air laut yang jernih',
            'full_description': '''Pulau Lambudung menawarkan keindahan pantai dengan pasir putih yang sangat 
            bersih dan air laut yang jernih. Pulau ini cocok untuk wisatawan yang ingin menikmati 
            keindahan alam sambil bersantai. Pantai yang bersih dan air laut yang jernih membuat 
            tempat ini sangat cocok untuk berenang dan berjemur.''',
            'address': 'Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.3500,
            'longitude': 97.5000,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 20000,
            'contact_phone': '0852-1234-5688',
            'facilities': json.dumps([
                'Area pantai',
                'Pondok wisata',
                'Toilet umum',
                'Area parkir kapal',
                'Warung makan'
            ]),
            'activities': json.dumps([
                'Berenang',
                'Berjemur',
                'Bersantai',
                'Fotografi',
                'Makan seafood',
                'Menikmati keindahan alam'
            ]),
            'featured': False,
            'status': 'published'
        },
        {
            'title': 'Pulau Biawak',
            'category': alam_cat,
            'location_type': 'natural',
            'short_description': 'Pulau yang dikenal sebagai habitat bagi hewan purba langka yaitu biawak',
            'full_description': '''Pulau Biawak merupakan destinasi wisata alam yang unik karena menjadi habitat 
            bagi hewan purba langka yaitu biawak. Pulau ini menawarkan pengalaman wisata alam yang 
            berbeda dengan kesempatan untuk melihat biawak dalam habitat aslinya. Pulau ini cocok 
            untuk wisatawan yang tertarik dengan satwa liar dan konservasi alam.''',
            'address': 'Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.4000,
            'longitude': 97.5500,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 25000,
            'contact_phone': '0852-1234-5689',
            'facilities': json.dumps([
                'Area observasi',
                'Panduan wisata',
                'Pondok wisata',
                'Toilet umum',
                'Area parkir kapal'
            ]),
            'activities': json.dumps([
                'Melihat biawak',
                'Wildlife watching',
                'Fotografi satwa',
                'Tracking alam',
                'Belajar konservasi',
                'Menikmati keindahan alam'
            ]),
            'featured': False,
            'status': 'published'
        },
        {
            'title': 'Pulau Matahari',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau dengan pemandangan matahari terbit yang mempesona dan pantai putih yang indah',
            'full_description': '''Pulau Matahari terkenal dengan pemandangan matahari terbit yang sangat 
            mempesona dan pantai putih yang indah. Pulau ini menawarkan pengalaman wisata yang unik 
            dengan kesempatan untuk menikmati keindahan matahari terbit di atas laut. Pantai putih 
            yang indah membuat tempat ini sangat cocok untuk fotografi dan bersantai.''',
            'address': 'Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.4500,
            'longitude': 97.6000,
            'opening_hours': '05:00 - 18:00',
            'entry_fee': 30000,
            'contact_phone': '0852-1234-5690',
            'facilities': json.dumps([
                'Area sunrise',
                'Pondok wisata',
                'Toilet umum',
                'Area parkir kapal',
                'Warung makan'
            ]),
            'activities': json.dumps([
                'Melihat sunrise',
                'Fotografi sunrise',
                'Berenang',
                'Berjemur',
                'Bersantai',
                'Menikmati keindahan alam'
            ]),
            'featured': True,
            'status': 'published'
        },
        {
            'title': 'Pulau Silailik',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau dengan keindahan pantai pasir putih dan air laut yang jernih',
            'full_description': '''Pulau Silailik menawarkan keindahan pantai dengan pasir putih yang sangat 
            bersih dan air laut yang jernih. Pulau ini cocok untuk wisatawan yang ingin menikmati 
            keindahan alam sambil bersantai. Pantai yang bersih dan air laut yang jernih membuat 
            tempat ini sangat cocok untuk berenang dan berjemur.''',
            'address': 'Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.5000,
            'longitude': 97.6500,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 20000,
            'contact_phone': '0852-1234-5691',
            'facilities': json.dumps([
                'Area pantai',
                'Pondok wisata',
                'Toilet umum',
                'Area parkir kapal',
                'Warung makan'
            ]),
            'activities': json.dumps([
                'Berenang',
                'Berjemur',
                'Bersantai',
                'Fotografi',
                'Makan seafood',
                'Menikmati keindahan alam'
            ]),
            'featured': False,
            'status': 'published'
        },
        {
            'title': 'Pulau Rangit Besar',
            'category': pulau_cat,
            'location_type': 'natural',
            'short_description': 'Pulau dengan keindahan pantai pasir putih dan air laut yang jernih',
            'full_description': '''Pulau Rangit Besar menawarkan keindahan pantai dengan pasir putih yang sangat 
            bersih dan air laut yang jernih. Pulau ini cocok untuk wisatawan yang ingin menikmati 
            keindahan alam sambil bersantai. Pantai yang bersih dan air laut yang jernih membuat 
            tempat ini sangat cocok untuk berenang dan berjemur.''',
            'address': 'Kepulauan Banyak, Kabupaten Aceh Singkil, Aceh',
            'latitude': 2.5500,
            'longitude': 97.7000,
            'opening_hours': '06:00 - 18:00',
            'entry_fee': 20000,
            'contact_phone': '0852-1234-5692',
            'facilities': json.dumps([
                'Area pantai',
                'Pondok wisata',
                'Toilet umum',
                'Area parkir kapal',
                'Warung makan'
            ]),
            'activities': json.dumps([
                'Berenang',
                'Berjemur',
                'Bersantai',
                'Fotografi',
                'Makan seafood',
                'Menikmati keindahan alam'
            ]),
            'featured': False,
            'status': 'published'
        }
    ]
    
    locations = []
    for loc_data in locations_data:
        location, created = TourismLocation.objects.get_or_create(
            title=loc_data['title'],
            defaults={
                **loc_data,
                'created_by': admin_user,
                'updated_by': admin_user,
                'published_at': timezone.now()
            }
        )
        locations.append(location)
        print(f"Lokasi '{location.title}' {'dibuat' if created else 'sudah ada'}")
    
    return locations

def create_tourism_gallery():
    """Membuat data galeri untuk lokasi wisata"""
    locations = TourismLocation.objects.all()
    
    gallery_data = []
    for location in locations:
        # Create 3-5 gallery items per location
        for i in range(3):
            gallery_item = TourismGallery.objects.create(
                tourism_location=location,
                media_type='image',
                title=f'Gambar {i+1} - {location.title}',
                description=f'Gambar keindahan {location.title} yang menakjubkan',
                alt_text=f'Gambar {location.title}',
                caption=f'Keindahan {location.title}',
                is_featured=(i == 0),  # First image is featured
                order=i,
                is_active=True
            )
            gallery_data.append(gallery_item)
    
    print(f"Dibuat {len(gallery_data)} item galeri")
    return gallery_data

def create_tourism_packages():
    """Membuat paket wisata untuk beberapa lokasi"""
    locations = TourismLocation.objects.filter(featured=True)[:5]
    
    packages_data = [
        {
            'title': 'Paket Wisata Pantai Pulo Sarok 1 Hari',
            'tourism_location': locations[0] if locations else TourismLocation.objects.first(),
            'package_type': 'day_trip',
            'description': 'Paket wisata pantai Pulo Sarok untuk 1 hari dengan berbagai aktivitas menarik',
            'duration': '1 Hari',
            'price': 150000,
            'currency': 'IDR',
            'whatsapp': '0852-1234-5678',
            'includes': json.dumps([
                'Transportasi',
                'Makan siang',
                'Pemandu wisata',
                'Asuransi perjalanan'
            ]),
            'excludes': json.dumps([
                'Makan malam',
                'Penginapan',
                'Biaya pribadi'
            ]),
            'itinerary': json.dumps([
                '08:00 - Meeting point',
                '09:00 - Perjalanan ke Pulo Sarok',
                '10:00 - Tiba di pantai',
                '10:00-12:00 - Aktivitas pantai',
                '12:00-13:00 - Makan siang',
                '13:00-16:00 - Aktivitas bebas',
                '16:00 - Kembali'
            ]),
            'max_participants': 20,
            'min_participants': 2,
            'is_featured': True
        },
        {
            'title': 'Paket Diving Pulau Bengkaru 2 Hari',
            'tourism_location': locations[2] if len(locations) > 2 else TourismLocation.objects.first(),
            'package_type': 'weekend',
            'description': 'Paket diving di Pulau Bengkaru dengan keindahan bawah laut yang menakjubkan',
            'duration': '2 Hari 1 Malam',
            'price': 800000,
            'currency': 'IDR',
            'whatsapp': '0852-1234-5680',
            'includes': json.dumps([
                'Transportasi kapal',
                'Peralatan diving',
                'Panduan diving',
                'Penginapan',
                'Makan 3x',
                'Asuransi'
            ]),
            'excludes': json.dumps([
                'Biaya pribadi',
                'Tips panduan'
            ]),
            'itinerary': json.dumps([
                'Hari 1: 08:00 - Meeting point',
                'Hari 1: 10:00 - Perjalanan ke Bengkaru',
                'Hari 1: 12:00 - Check in penginapan',
                'Hari 1: 14:00 - Diving session 1',
                'Hari 1: 18:00 - Makan malam',
                'Hari 2: 08:00 - Diving session 2',
                'Hari 2: 12:00 - Makan siang',
                'Hari 2: 14:00 - Kembali'
            ]),
            'max_participants': 15,
            'min_participants': 4,
            'is_featured': True
        },
        {
            'title': 'Paket Edukasi Konservasi Penyu',
            'tourism_location': locations[5] if len(locations) > 5 else TourismLocation.objects.first(),
            'package_type': 'day_trip',
            'description': 'Paket edukasi konservasi penyu di Pulo Bangkaru untuk keluarga dan kelompok',
            'duration': '1 Hari',
            'price': 200000,
            'currency': 'IDR',
            'whatsapp': '0852-1234-5683',
            'includes': json.dumps([
                'Transportasi',
                'Panduan edukasi',
                'Makan siang',
                'Materi edukasi',
                'Sertifikat partisipasi'
            ]),
            'excludes': json.dumps([
                'Biaya pribadi',
                'Makan malam'
            ]),
            'itinerary': json.dumps([
                '08:00 - Meeting point',
                '09:00 - Perjalanan ke Pulo Bangkaru',
                '10:00 - Edukasi konservasi penyu',
                '12:00 - Makan siang',
                '13:00 - Praktik konservasi',
                '15:00 - Penyerahan sertifikat',
                '16:00 - Kembali'
            ]),
            'max_participants': 25,
            'min_participants': 5,
            'is_featured': False
        }
    ]
    
    packages = []
    for pkg_data in packages_data:
        package, created = TourismPackage.objects.get_or_create(
            title=pkg_data['title'],
            defaults=pkg_data
        )
        packages.append(package)
        print(f"Paket '{package.title}' {'dibuat' if created else 'sudah ada'}")
    
    return packages

def create_tourism_events():
    """Membuat event wisata untuk beberapa lokasi"""
    locations = TourismLocation.objects.filter(featured=True)[:3]
    
    events_data = [
        {
            'title': 'Festival Pantai Pulo Sarok 2024',
            'tourism_location': locations[0] if locations else TourismLocation.objects.first(),
            'event_type': 'festival',
            'description': 'Festival pantai tahunan dengan berbagai pertunjukan dan aktivitas menarik',
            'start_date': timezone.now() + timedelta(days=30),
            'end_date': timezone.now() + timedelta(days=30, hours=8),
            'start_time': '08:00',
            'end_time': '18:00',
            'organizer': 'Pemerintah Desa Pulosarok',
            'contact_person': 'Budi Santoso',
            'phone': '0852-1234-5678',
            'email': 'festival@pulosarok.com',
            'registration_required': True,
            'max_participants': 500,
            'is_featured': True
        },
        {
            'title': 'Workshop Diving untuk Pemula',
            'tourism_location': locations[2] if len(locations) > 2 else TourismLocation.objects.first(),
            'event_type': 'workshop',
            'description': 'Workshop diving untuk pemula dengan instruktur berpengalaman',
            'start_date': timezone.now() + timedelta(days=15),
            'end_date': timezone.now() + timedelta(days=15, hours=6),
            'start_time': '09:00',
            'end_time': '15:00',
            'organizer': 'Diving Club Aceh Singkil',
            'contact_person': 'Ahmad Diver',
            'phone': '0852-1234-5680',
            'email': 'diving@acehsingkil.com',
            'registration_required': True,
            'registration_fee': 500000,
            'max_participants': 20,
            'is_featured': False
        },
        {
            'title': 'Edukasi Konservasi Penyu',
            'tourism_location': locations[5] if len(locations) > 5 else TourismLocation.objects.first(),
            'event_type': 'workshop',
            'description': 'Edukasi konservasi penyu untuk siswa sekolah dan masyarakat umum',
            'start_date': timezone.now() + timedelta(days=20),
            'end_date': timezone.now() + timedelta(days=20, hours=4),
            'start_time': '08:00',
            'end_time': '12:00',
            'organizer': 'Konservasi Penyu Aceh',
            'contact_person': 'Dr. Sari Konservasi',
            'phone': '0852-1234-5683',
            'email': 'konservasi@penyu.com',
            'registration_required': True,
            'max_participants': 50,
            'is_featured': True
        }
    ]
    
    events = []
    for event_data in events_data:
        event, created = TourismEvent.objects.get_or_create(
            title=event_data['title'],
            defaults={
                **event_data,
                'created_by': User.objects.get(username='admin')
            }
        )
        events.append(event)
        print(f"Event '{event.title}' {'dibuat' if created else 'sudah ada'}")
    
    return events

def create_tourism_faqs():
    """Membuat FAQ untuk lokasi wisata"""
    locations = TourismLocation.objects.filter(featured=True)[:5]
    
    faqs_data = []
    for location in locations:
        faqs = [
            {
                'tourism_location': location,
                'question': f'Berapa biaya masuk ke {location.title}?',
                'answer': f'Biaya masuk ke {location.title} adalah Rp {location.entry_fee:,} per orang.',
                'category': 'Biaya',
                'priority': 1,
                'is_featured': True
            },
            {
                'tourism_location': location,
                'question': f'Jam berapa {location.title} buka?',
                'answer': f'{location.title} buka pada {location.opening_hours}.',
                'category': 'Jam Operasional',
                'priority': 1,
                'is_featured': True
            },
            {
                'tourism_location': location,
                'question': f'Apa saja fasilitas yang tersedia di {location.title}?',
                'answer': f'{location.title} menyediakan berbagai fasilitas seperti toilet umum, area parkir, dan warung makan.',
                'category': 'Fasilitas',
                'priority': 2,
                'is_featured': False
            }
        ]
        
        for faq_data in faqs:
            faq, created = TourismFAQ.objects.get_or_create(
                tourism_location=faq_data['tourism_location'],
                question=faq_data['question'],
                defaults=faq_data
            )
            faqs_data.append(faq)
    
    print(f"Dibuat {len(faqs_data)} FAQ")
    return faqs_data

# Menjalankan semua fungsi
print("=== Membuat Data Dummy Wisata Pulosarok Aceh Singkil ===")

# Create categories
print("\n1. Membuat kategori wisata...")
categories = create_tourism_categories()

# Create locations
print("\n2. Membuat lokasi wisata...")
locations = create_tourism_locations()

# Create gallery
print("\n3. Membuat galeri wisata...")
gallery = create_tourism_gallery()

# Create packages
print("\n4. Membuat paket wisata...")
packages = create_tourism_packages()

# Create events
print("\n5. Membuat event wisata...")
events = create_tourism_events()

# Create FAQs
print("\n6. Membuat FAQ wisata...")
faqs = create_tourism_faqs()

print("\n=== Data Dummy Wisata Berhasil Dibuat ===")
print(f"Kategori: {len(categories)}")
print(f"Lokasi: {len(locations)}")
print(f"Galeri: {len(gallery)}")
print(f"Paket: {len(packages)}")
print(f"Event: {len(events)}")
print(f"FAQ: {len(faqs)}")
