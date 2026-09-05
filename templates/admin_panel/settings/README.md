# Halaman Pengaturan Website Desa

Dokumentasi lengkap untuk semua halaman pengaturan dalam sistem admin panel.

## Daftar Halaman Pengaturan

### 1. Pengaturan Umum (`general.html`)
**URL:** `/admin/settings/general/`

Halaman untuk mengkonfigurasi pengaturan dasar website:
- **Informasi Dasar Website**: Nama, deskripsi, email, telepon, alamat
- **Logo dan Gambar**: Logo website, favicon, gambar background
- **Tampilan dan Warna**: Tema, warna primer/sekunder, bahasa default
- **Media Sosial**: Link Facebook, Instagram, Twitter, YouTube
- **Pengaturan SEO**: Meta description, keywords, Google Analytics
- **Pengaturan Sistem**: Ukuran upload, mode maintenance, notifikasi

**Fitur:**
- Preview gambar real-time
- Color picker untuk warna
- Validasi form real-time
- Auto-save (opsional)

### 2. Pengaturan Sistem (`system.html`)
**URL:** `/admin/settings/system/`

Halaman untuk mengelola konfigurasi sistem:
- **Informasi Sistem**: Status server, versi Django/Python, uptime
- **Pengaturan Sistem**: CRUD untuk system settings
- **Aksi Cepat**: Clear cache, run migrations, collect static, system check

**Fitur:**
- Tabel pengaturan dengan search dan filter
- Modal untuk add/edit settings
- Aksi cepat dengan konfirmasi
- Real-time system status

### 3. Manajemen Pengguna (`users.html`)
**URL:** `/admin/settings/users/`

Halaman untuk mengelola pengguna sistem:
- **Statistik Pengguna**: Total, aktif, staff, admin
- **Daftar Pengguna**: Tabel dengan search dan filter
- **Tambah/Edit Pengguna**: Form lengkap dengan validasi
- **Aksi Pengguna**: Toggle status, edit, hapus

**Fitur:**
- Search dan filter real-time
- Avatar preview
- Role-based permissions
- Bulk actions

### 4. Log Aktivitas (`activity_logs.html`)
**URL:** `/admin/settings/activity_logs/`

Halaman untuk melihat log aktivitas:
- **Statistik Log**: Total log, hari ini, error, pengguna aktif
- **Filter Log**: Level, pengguna, tanggal, kata kunci
- **Daftar Log**: Tampilan card dengan detail lengkap
- **Detail Log**: Modal dengan informasi lengkap

**Fitur:**
- Filter multi-kriteria
- Pagination
- Auto-refresh
- Export log

### 5. Backup & Restore (`backup_restore.html`)
**URL:** `/admin/settings/backup-restore/`

Halaman untuk mengelola backup:
- **Statistik Backup**: Total backup, ukuran, terakhir, auto backup
- **Buat Backup**: Form dengan opsi kompresi dan enkripsi
- **Restore Backup**: Upload dan restore dengan konfirmasi
- **Daftar Backup**: Kelola backup yang ada

**Fitur:**
- Drag & drop upload
- Progress bar real-time
- Konfirmasi restore
- Download backup

### 6. Pengaturan Modul (`modules.html`)
**URL:** `/admin/settings/modules/`

Halaman untuk mengelola modul:
- **Statistik Modul**: Total, aktif, nonaktif, core
- **Daftar Modul**: Grid layout dengan toggle switch
- **Konfigurasi Modul**: Modal untuk edit pengaturan
- **Aksi Modul**: Reset, uninstall (non-core)

**Fitur:**
- Toggle switch real-time
- Dependency checking
- Permission management
- Module configuration

### 7. Profil Pengguna (`profile.html`)
**URL:** `/admin/settings/profile/`

Halaman untuk mengelola profil pribadi:
- **Statistik Profil**: Bergabung, login terakhir, aktivitas, status
- **Informasi Dasar**: Nama, email, telepon, posisi, alamat, bio
- **Foto Profil**: Upload dan preview avatar
- **Keamanan**: Ubah password dengan strength checker

**Fitur:**
- Avatar upload dengan preview
- Password strength indicator
- Form validation
- Auto-save

### 8. Informasi Sistem (`system_info.html`)
**URL:** `/admin/settings/system-info/`

Halaman untuk melihat informasi sistem:
- **Ringkasan Sistem**: Uptime, pengguna, data, status
- **Informasi Sistem**: OS, hostname, IP, Python, Django
- **Metrik Performa**: Memory usage, CPU usage dengan progress bar
- **Status Aplikasi**: Tabel komponen dengan health indicator
- **Log Terbaru**: Aktivitas sistem terkini
- **Pemeriksaan Kesehatan**: Diagnostik sistem otomatis

**Fitur:**
- Real-time metrics
- Health check otomatis
- Copy to clipboard
- Export system info

### 9. Halaman Utama Pengaturan (`index.html`)
**URL:** `/admin/settings/`

Dashboard pengaturan dengan:
- **Ringkasan Statistik**: Total pengguna, modul aktif, backup, status
- **Aksi Cepat**: Buat backup, cek sistem, lihat log, tambah user
- **Kategori Pengaturan**: Card navigasi ke semua halaman pengaturan
- **Aktivitas Terbaru**: Log aktivitas terkini

## Struktur File

```
templates/admin_panel/settings/
├── index.html              # Halaman utama pengaturan
├── general.html            # Pengaturan umum website
├── system.html             # Pengaturan sistem
├── users.html              # Manajemen pengguna
├── activity_logs.html      # Log aktivitas
├── backup_restore.html     # Backup & restore
├── modules.html            # Pengaturan modul
├── profile.html            # Profil pengguna
├── system_info.html        # Informasi sistem
└── README.md              # Dokumentasi ini

static/css/admin/
└── settings.css           # CSS khusus pengaturan

static/js/admin/
└── settings.js            # JavaScript pengaturan
```

## CSS Classes

### Layout Classes
- `.settings-card` - Card container untuk setiap section
- `.settings-card-header` - Header card dengan gradient
- `.settings-card-body` - Body card dengan padding
- `.form-section` - Section form dengan border bottom
- `.section-title` - Title section dengan icon

### Form Classes
- `.required-field` - Field wajib dengan asterisk
- `.help-text` - Text bantuan di bawah field
- `.image-preview` - Container preview gambar
- `.color-preview` - Preview warna
- `.password-strength` - Container strength indicator

### Status Classes
- `.status-badge` - Badge status dengan warna
- `.status-active` - Status aktif (hijau)
- `.status-inactive` - Status nonaktif (merah)
- `.status-warning` - Status peringatan (kuning)
- `.status-info` - Status info (biru)

### Button Classes
- `.btn-save` - Tombol simpan dengan gradient
- `.btn-cancel` - Tombol batal abu-abu
- `.btn-action` - Tombol aksi kecil
- `.btn-edit` - Tombol edit biru
- `.btn-delete` - Tombol hapus merah
- `.btn-toggle` - Tombol toggle hijau

## JavaScript Functions

### Utility Functions
- `showAlert(message, type)` - Tampilkan alert
- `showLoading(element)` - Tampilkan loading spinner
- `hideLoading(element, content)` - Sembunyikan loading
- `confirmAction(message, callback)` - Konfirmasi aksi
- `formatFileSize(bytes)` - Format ukuran file
- `formatDate(dateString)` - Format tanggal

### Form Functions
- `validateField(field)` - Validasi field individual
- `validateForm(form)` - Validasi form lengkap
- `showFieldError(field, message)` - Tampilkan error field

### Image Functions
- `previewAvatar(input)` - Preview avatar upload
- `changeAvatar()` - Trigger avatar upload

### Password Functions
- `checkPasswordStrength(password)` - Cek kekuatan password
- `updatePasswordStrength(strength)` - Update tampilan strength

### Copy Functions
- `copyToClipboard(text, button)` - Copy ke clipboard
- `showCopySuccess(button)` - Tampilkan feedback copy

## API Endpoints

### General Settings
- `POST /admin/api/general-settings/` - Simpan pengaturan umum
- `GET /admin/api/general-settings/` - Ambil pengaturan umum

### System Settings
- `POST /admin/api/system-settings/` - Simpan pengaturan sistem
- `GET /admin/api/system-settings/` - Ambil pengaturan sistem
- `POST /admin/api/clear-cache/` - Clear cache
- `POST /admin/api/run-migrations/` - Run migrations

### User Management
- `POST /admin/api/users/` - Tambah pengguna
- `PUT /admin/api/users/{id}/` - Update pengguna
- `DELETE /admin/api/users/{id}/` - Hapus pengguna
- `POST /admin/api/users/{id}/toggle/` - Toggle status

### Activity Logs
- `GET /admin/api/activity-logs/` - Ambil log aktivitas
- `GET /admin/api/log-details/{id}/` - Detail log
- `DELETE /admin/api/logs/{id}/` - Hapus log

### Backup & Restore
- `POST /admin/api/backup/create/` - Buat backup
- `POST /admin/api/backup/upload/` - Upload backup
- `POST /admin/api/backup/restore/` - Restore backup
- `GET /admin/api/backup/download/{id}/` - Download backup

### Module Settings
- `POST /admin/api/modules/configure/` - Konfigurasi modul
- `POST /admin/api/modules/toggle/` - Toggle modul
- `POST /admin/api/modules/reset/` - Reset modul

### Profile
- `POST /admin/api/profile/update/` - Update profil
- `POST /admin/api/profile/change-password/` - Ubah password

### System Info
- `GET /admin/api/system-info/` - Informasi sistem
- `GET /admin/api/system-health/` - Health check
- `GET /admin/api/system-info/export/` - Export info

## Responsive Design

Semua halaman pengaturan dirancang responsive dengan:
- **Mobile First**: Optimized untuk mobile device
- **Breakpoints**: 
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px
- **Grid System**: CSS Grid dan Flexbox
- **Touch Friendly**: Button dan input yang mudah disentuh

## Browser Support

- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- **Lazy Loading**: Gambar dan konten dimuat saat diperlukan
- **Debounced Input**: Input search dengan debounce
- **Cached Data**: Data sering digunakan di-cache
- **Minified Assets**: CSS dan JS di-minify untuk production

## Security

- **CSRF Protection**: Semua form dilindungi CSRF token
- **Input Validation**: Validasi server-side dan client-side
- **XSS Protection**: Output di-escape untuk mencegah XSS
- **Permission Check**: Setiap aksi dicek permission-nya

## Accessibility

- **ARIA Labels**: Label yang jelas untuk screen reader
- **Keyboard Navigation**: Dapat diakses dengan keyboard
- **Color Contrast**: Kontras warna yang memadai
- **Focus Indicators**: Indikator focus yang jelas

## Maintenance

### Regular Tasks
1. **Backup Database**: Setiap hari
2. **Clear Cache**: Setiap minggu
3. **Update Dependencies**: Setiap bulan
4. **Security Audit**: Setiap 3 bulan

### Monitoring
1. **Error Logs**: Monitor error logs harian
2. **Performance**: Monitor response time
3. **Disk Space**: Monitor penggunaan disk
4. **Memory Usage**: Monitor penggunaan memory

## Troubleshooting

### Common Issues
1. **Form tidak tersimpan**: Cek CSRF token dan validasi
2. **Gambar tidak muncul**: Cek path dan permission file
3. **AJAX error**: Cek network tab dan console
4. **Permission denied**: Cek user role dan permission

### Debug Mode
Aktifkan debug mode untuk melihat error detail:
```python
DEBUG = True
```

### Log Files
Cek log files untuk error:
- `logs/django.log`
- `logs/error.log`
- `logs/access.log`
