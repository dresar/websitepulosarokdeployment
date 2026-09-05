from django import template
from django.utils.safestring import mark_safe
import locale

register = template.Library()

@register.filter
def rupiah(value):
    """
    Format number as Indonesian Rupiah currency
    """
    if value is None or value == '':
        return 'Rp 0'
    
    try:
        # Convert to float first
        float_value = float(value)
        
        # Format with Indonesian locale
        locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
        formatted = locale.currency(float_value, grouping=True, symbol=False)
        
        # Add Rp prefix
        return f"Rp {formatted}"
    except (ValueError, TypeError, locale.Error):
        # Fallback if locale is not available
        try:
            float_value = float(value)
            # Manual formatting for Indonesian Rupiah
            formatted = f"{float_value:,.0f}".replace(',', '.')
            return f"Rp {formatted}"
        except (ValueError, TypeError):
            return 'Rp 0'

@register.filter
def rupiah_short(value):
    """
    Format number as Indonesian Rupiah with short notation (K, M, B)
    """
    if value is None or value == '':
        return 'Rp 0'
    
    try:
        float_value = float(value)
        
        if float_value >= 1_000_000_000:
            return f"Rp {float_value/1_000_000_000:.1f}B"
        elif float_value >= 1_000_000:
            return f"Rp {float_value/1_000_000:.1f}M"
        elif float_value >= 1_000:
            return f"Rp {float_value/1_000:.1f}K"
        else:
            return f"Rp {float_value:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return 'Rp 0'

@register.filter
def format_number(value):
    """
    Format number with Indonesian thousand separator
    """
    if value is None or value == '':
        return '0'
    
    try:
        float_value = float(value)
        return f"{float_value:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return '0'

@register.filter
def rating_stars(value):
    """
    Generate star rating HTML
    """
    if value is None or value == '':
        return ''
    
    try:
        rating = float(value)
        stars_html = ''
        
        for i in range(1, 6):
            if i <= rating:
                stars_html += '<i class="fas fa-star text-yellow-400"></i>'
            elif i - 0.5 <= rating:
                stars_html += '<i class="fas fa-star-half-alt text-yellow-400"></i>'
            else:
                stars_html += '<i class="far fa-star text-gray-300"></i>'
        
        return mark_safe(f'{stars_html} ({rating}/5)')
    except (ValueError, TypeError):
        return ''
