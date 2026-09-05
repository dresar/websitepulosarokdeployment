# Data Dummy untuk Aplikasi Documents

File ini berisi data dummy untuk aplikasi documents yang mencakup semua model yang diperlukan untuk testing dan development.

## Isi Data

Script ini akan memuat data dummy untuk:

### 1. Data Referensi
- **Dusun** (3 records): 
  - Dusun Mawar (DSN001) - 150 penduduk, 25.50 ha
  - Dusun Melati (DSN002) - 200 penduduk, 30.75 ha
  - Dusun Kenanga (DSN003) - 175 penduduk, 22.25 ha

### 2. Data Documents
- **DocumentType** (3 records): 
  - Surat Keterangan Domisili (Rp 5.000, 3 hari)
  - Surat Keterangan Tidak Mampu (Gratis, 5 hari)
  - Surat Pengantar Nikah (Rp 10.000, 7 hari)

Setiap DocumentType memiliki:
- Nama dan deskripsi
- Field yang diperlukan (dalam format JSON)
- Waktu pemrosesan (hari)
- Biaya administrasi
- Status aktif

## Cara Menggunakan

### 1. Load Data Dummy
```bash
# Load semua data dummy
python manage.py load_documents_dummy

# Load dengan output verbose
python manage.py load_documents_dummy --verbose

# Reset data sebelum load (hapus data lama)
python manage.py load_documents_dummy --reset --verbose
```

**Catatan**: Script ini menggunakan Django ORM langsung untuk menghindari masalah kompatibilitas dengan fixture JSON pada beberapa versi MySQL.

### 2. Verifikasi Data
```bash
# Cek data yang telah diload
python manage.py shell

# Di dalam shell Django:
from documents.models import *
from references.models import *

# Cek jumlah data
print(f"DocumentType: {DocumentType.objects.count()}")
print(f"Document: {Document.objects.count()}")
print(f"Penduduk: {Penduduk.objects.count()}")
print(f"Dusun: {Dusun.objects.count()}")
```

### 3. Reset Data (jika diperlukan)
```bash
# Hapus semua data
python manage.py flush

# Load ulang fixture
python manage.py loaddata documents/fixtures/documents_dummy_data.json
```

## Detail Data

### Penduduk
1. **Ahmad Suryadi** (NIK: 7301012345678901) - Kepala Keluarga, Dusun Mawar
2. **Siti Aminah** (NIK: 7301012345678902) - Istri Ahmad, Dusun Mawar
3. **Budi Santoso** (NIK: 7301012345678903) - Belum Kawin, Dusun Melati

### Status Dokumen
- **SKD/001/2024**: Completed (Ahmad Suryadi)
- **SKTM/002/2024**: Processing (Siti Aminah)
- **SPN/003/2024**: Submitted (Budi Santoso)

### Template Dokumen
- Template menggunakan format placeholder `{{variable}}`
- Sudah termasuk header dan footer resmi
- Dapat digunakan untuk generate dokumen otomatis

## Catatan
- Data dummy ini dibuat untuk keperluan development dan testing
- Semua NIK dan data personal adalah fiktif
- Pastikan untuk tidak menggunakan data ini di production
- Data dapat dimodifikasi sesuai kebutuhan testing