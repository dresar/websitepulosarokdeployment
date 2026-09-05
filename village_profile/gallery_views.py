from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
import json
import os

from .models import VillageProfile, VillagePhoto


def is_admin(user):
    """Check if user is admin or superuser"""
    return user.is_authenticated and (user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists())


# ==================== GALLERY API ====================
@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST", "DELETE"])
def gallery_api(request):
    """API for gallery CRUD operations"""
    try:
        village_profile = VillageProfile.objects.filter(is_active=True).first()
        if not village_profile:
            return JsonResponse({
                'success': False,
                'message': 'Profil desa tidak ditemukan'
            })
        
        if request.method == 'GET':
            return get_gallery_photos(request, village_profile)
        elif request.method == 'POST':
            return save_gallery_photo(request, village_profile)
        elif request.method == 'DELETE':
            return delete_gallery_photo(request, village_profile)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        })


def get_gallery_photos(request, village_profile):
    """Get all gallery photos"""
    try:
        photos = VillagePhoto.objects.filter(
            village=village_profile,
            is_active=True
        ).order_by('-created_at')
        
        photos_data = []
        for photo in photos:
            photos_data.append({
                'id': photo.id,
                'title': photo.title,
                'description': photo.description,
                'category': photo.photo_type,
                'tags': photo.tags or '',
                'date_taken': photo.photo_date.isoformat() if photo.photo_date else None,
                'location': photo.location,
                'photographer': photo.photographer,
                'image_url': photo.image.url if photo.image else None,
                'file_size': photo.image.size if photo.image else 0,
                'is_featured': photo.is_featured,
                'view_count': photo.view_count,
                'created_at': photo.created_at.isoformat(),
                'updated_at': photo.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'photos': photos_data,
            'total': len(photos_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal mengambil data galeri: {str(e)}'
        })


def save_gallery_photo(request, village_profile):
    """Save or update gallery photo"""
    try:
        photo_id = request.POST.get('photo_id')
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'OTHER')
        tags = request.POST.get('tags', '').strip()
        date_taken = request.POST.get('date_taken')
        location = request.POST.get('location', '').strip()
        photographer = request.POST.get('photographer', '').strip()
        
        # Validation
        if not title:
            return JsonResponse({
                'success': False,
                'errors': {'title': ['Judul foto harus diisi']}
            })
        
        if not photo_id and 'photo' not in request.FILES:
            return JsonResponse({
                'success': False,
                'errors': {'photo': ['Foto harus diupload']}
            })
        
        # Check file size (5MB limit)
        if 'photo' in request.FILES:
            photo_file = request.FILES['photo']
            if photo_file.size > 5 * 1024 * 1024:  # 5MB
                return JsonResponse({
                    'success': False,
                    'errors': {'photo': ['Ukuran foto maksimal 5MB']}
                })
        
        # Create or update photo
        if photo_id:
            photo = get_object_or_404(VillagePhoto, id=photo_id, village=village_profile)
            photo.title = title
            photo.description = description
            photo.photo_type = category
            photo.tags = tags
            photo.location = location
            photo.photographer = photographer
            
            if date_taken:
                from datetime import datetime
                photo.photo_date = datetime.strptime(date_taken, '%Y-%m-%d').date()
            
            if 'photo' in request.FILES:
                photo.image = request.FILES['photo']
            
            photo.save()
            message = 'Foto berhasil diperbarui!'
        else:
            photo = VillagePhoto.objects.create(
                village=village_profile,
                title=title,
                description=description,
                photo_type=category,
                tags=tags,
                location=location,
                photographer=photographer,
                image=request.FILES['photo']
            )
            
            if date_taken:
                from datetime import datetime
                photo.photo_date = datetime.strptime(date_taken, '%Y-%m-%d').date()
                photo.save()
            
            message = 'Foto berhasil ditambahkan!'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'photo_id': photo.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menyimpan foto: {str(e)}'
        })


def delete_gallery_photo(request, village_profile):
    """Delete gallery photo"""
    try:
        photo_id = request.POST.get('photo_id')
        if not photo_id:
            return JsonResponse({
                'success': False,
                'message': 'ID foto tidak ditemukan'
            })
        
        photo = get_object_or_404(VillagePhoto, id=photo_id, village=village_profile)
        
        # Delete image file if exists
        if photo.image:
            try:
                if os.path.isfile(photo.image.path):
                    os.remove(photo.image.path)
            except:
                pass  # Ignore file deletion errors
        
        photo.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Foto berhasil dihapus!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus foto: {str(e)}'
        })
