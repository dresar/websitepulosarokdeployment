from django import template

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    """
    Format nilai menjadi mata uang Rupiah Indonesia
    Contoh: 1000000 -> Rp 1.000.000
    """
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        return 'Rp 0'
    
    # Konversi ke integer untuk menghilangkan desimal
    amount_int = int(round(amount))
    
    # Format dengan titik sebagai pemisah ribuan
    formatted = f"{amount_int:,}".replace(',', '.')
    
    return f"Rp {formatted}"

@register.filter(name='format_number')
def format_number(value):
    """
    Format angka dengan titik sebagai pemisah ribuan
    Contoh: 1000000 -> 1.000.000
    """
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        return '0'
    
    # Konversi ke integer untuk menghilangkan desimal
    amount_int = int(round(amount))
    
    # Format dengan titik sebagai pemisah ribuan
    return f"{amount_int:,}".replace(',', '.')


