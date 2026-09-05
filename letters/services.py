import hashlib
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import datetime, timedelta
import re
import logging
import os
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .models import LetterSettings, Letter

logger = logging.getLogger(__name__)

class LetterValidationService:
    """Service untuk validasi surat tanpa AI"""
    
    def __init__(self):
        pass
    
    def validate_letter(self, content, letter_type=None):
        """Validasi konten surat menggunakan aturan bisnis"""
        try:
            # Validasi dasar
            errors = []
            suggestions = []
            
            # Cek panjang konten
            if len(content.strip()) < 10:
                errors.append("Konten surat terlalu pendek")
                suggestions.append("Tambahkan detail lebih lengkap")
            
            # Cek struktur surat
            if not self._has_proper_structure(content):
                suggestions.append("Pastikan surat memiliki struktur yang jelas")
            
            # Cek ejaan dasar
            spelling_errors = self._check_basic_spelling(content)
            if spelling_errors:
                errors.extend(spelling_errors)
            
            # Hitung skor validasi
            score = self._calculate_validation_score(content, errors)
            
            return {
                'is_valid': len(errors) == 0,
                'score': score,
                'suggestions': suggestions,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Error validating letter: {e}")
            return {
                'is_valid': False,
                'score': 0,
                'suggestions': [f'Error: {str(e)}'],
                'errors': ['Terjadi kesalahan dalam validasi']
            }
    
    def _has_proper_structure(self, content):
        """Cek struktur surat dasar"""
        # Cek apakah ada salam pembuka
        greetings = ['dengan hormat', 'assalamualaikum', 'selamat', 'terima kasih']
        has_greeting = any(greeting in content.lower() for greeting in greetings)
        
        # Cek apakah ada penutup
        closings = ['hormat saya', 'terima kasih', 'wassalam', 'salam']
        has_closing = any(closing in content.lower() for closing in closings)
        
        return has_greeting and has_closing
    
    def _check_basic_spelling(self, content):
        """Cek ejaan dasar"""
        errors = []
        
        # Kata-kata yang sering salah eja
        common_mistakes = {
            'apakah': 'apakah',
            'bagaimana': 'bagaimana',
            'dimana': 'di mana',
            'kapan': 'kapan',
            'mengapa': 'mengapa'
        }
        
        for wrong, correct in common_mistakes.items():
            if wrong in content.lower():
                errors.append(f"Gunakan '{correct}' bukan '{wrong}'")
        
        return errors
    
    def _calculate_validation_score(self, content, errors):
        """Hitung skor validasi"""
        base_score = 1.0
        
        # Kurangi skor untuk setiap error
        error_penalty = len(errors) * 0.1
        
        # Bonus untuk panjang konten yang memadai
        if len(content) > 100:
            base_score += 0.1
        
        # Bonus untuk struktur yang baik
        if self._has_proper_structure(content):
            base_score += 0.2
        
        final_score = max(0.0, min(1.0, base_score - error_penalty))
        return round(final_score, 2)

def generate_letter_number():
    """Generate nomor surat otomatis"""
    try:
        today = timezone.now().date()
        year = today.year
        
        # Ambil nomor surat terakhir untuk tahun ini
        last_letter = Letter.objects.filter(
            created_at__year=year
        ).order_by('-letter_number').first()
        
        if last_letter and last_letter.letter_number:
            # Extract number from last letter number
            try:
                last_number = int(last_letter.letter_number.split('/')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        # Format: 001/SP/2024
        letter_number = f"{new_number:03d}/SP/{year}"
        return letter_number
        
    except Exception as e:
        logger.error(f"Error generating letter number: {e}")
        return f"001/SP/{timezone.now().year}"

def generate_qr_code(data):
    """Generate QR code untuk surat"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return None

def validate_file_upload(file):
    """Validasi file upload"""
    try:
        # Cek ukuran file (max 5MB)
        if file.size > 5 * 1024 * 1024:
            return False, "File terlalu besar (max 5MB)"
        
        # Cek tipe file
        allowed_types = ['application/pdf', 'application/msword', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        
        if file.content_type not in allowed_types:
            return False, "Tipe file tidak didukung (hanya PDF, DOC, DOCX)"
        
        return True, "File valid"
        
    except Exception as e:
        logger.error(f"Error validating file: {e}")
        return False, f"Error: {str(e)}"
