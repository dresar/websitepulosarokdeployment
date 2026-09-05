from django import template
from django.utils.safestring import mark_safe
import locale

register = template.Library()

@register.filter
def currency_idr(value):
    """
    Format number as Indonesian Rupiah currency
    """
    if value is None:
        return "Rp 0"
    
    try:
        # Convert to float if it's a string
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        # Format as currency
        formatted = f"Rp {value:,.0f}".replace(',', '.')
        return formatted
    except (ValueError, TypeError):
        return "Rp 0"

@register.filter
def currency_format(value, currency="IDR"):
    """
    Format number as currency with specified currency code
    """
    if value is None:
        return f"{currency} 0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        if currency == "IDR":
            formatted = f"Rp {value:,.0f}".replace(',', '.')
        elif currency == "USD":
            formatted = f"$ {value:,.2f}"
        elif currency == "EUR":
            formatted = f"€ {value:,.2f}"
        else:
            formatted = f"{currency} {value:,.2f}"
        
        return formatted
    except (ValueError, TypeError):
        return f"{currency} 0"

@register.filter
def number_format(value, decimals=0):
    """
    Format number with thousand separators
    """
    if value is None:
        return "0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        if decimals == 0:
            formatted = f"{value:,.0f}".replace(',', '.')
        else:
            formatted = f"{value:,.{decimals}f}".replace(',', '.')
        
        return formatted
    except (ValueError, TypeError):
        return "0"

@register.filter
def percentage_format(value, decimals=1):
    """
    Format number as percentage
    """
    if value is None:
        return "0%"
    
    try:
        if isinstance(value, str):
            value = float(value)
        
        formatted = f"{value:.{decimals}f}%"
        return formatted
    except (ValueError, TypeError):
        return "0%"

@register.filter
def thousand_format(value):
    """
    Format large numbers with K, M, B suffixes
    """
    if value is None:
        return "0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        if value >= 1_000_000_000:
            return f"{value/1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return "0"

@register.filter
def compact_currency(value, currency="IDR"):
    """
    Format currency in compact form (K, M, B)
    """
    if value is None:
        return f"{currency} 0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        if currency == "IDR":
            if value >= 1_000_000_000:
                return f"Rp {value/1_000_000_000:.1f}B"
            elif value >= 1_000_000:
                return f"Rp {value/1_000_000:.1f}M"
            elif value >= 1_000:
                return f"Rp {value/1_000:.1f}K"
            else:
                return f"Rp {value:,.0f}".replace(',', '.')
        else:
            if value >= 1_000_000_000:
                return f"{currency} {value/1_000_000_000:.1f}B"
            elif value >= 1_000_000:
                return f"{currency} {value/1_000_000:.1f}M"
            elif value >= 1_000:
                return f"{currency} {value/1_000:.1f}K"
            else:
                return f"{currency} {value:,.0f}"
    except (ValueError, TypeError):
        return f"{currency} 0"

@register.filter
def rupiah_format(value):
    """
    Alias for currency_idr for backward compatibility
    """
    return currency_idr(value)

@register.filter
def money_format(value):
    """
    Format money with proper Indonesian formatting
    """
    if value is None:
        return "Rp 0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        # Format with dots as thousand separators and commas as decimal separators
        formatted = f"Rp {value:,.0f}".replace(',', '.')
        return formatted
    except (ValueError, TypeError):
        return "Rp 0"

@register.filter
def budget_format(value):
    """
    Format budget amounts with proper Indonesian formatting
    """
    if value is None:
        return "Rp 0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        # For large amounts, use compact format
        if value >= 1_000_000:
            if value >= 1_000_000_000:
                return f"Rp {value/1_000_000_000:.1f}M"
            else:
                return f"Rp {value/1_000_000:.1f}M"
        else:
            return f"Rp {value:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return "Rp 0"

@register.filter
def salary_format(value):
    """
    Format salary amounts
    """
    if value is None:
        return "Rp 0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        return f"Rp {value:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return "Rp 0"

@register.filter
def price_format(value):
    """
    Format price amounts
    """
    if value is None:
        return "Rp 0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        return f"Rp {value:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return "Rp 0"

@register.filter
def currency_idr_simple(value):
    """
    Simple currency formatting without Rp prefix
    """
    if value is None:
        return "0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        formatted = f"{value:,.0f}".replace(',', '.')
        return formatted
    except (ValueError, TypeError):
        return "0"

@register.filter
def currency_idr_with_symbol(value):
    """
    Currency formatting with symbol
    """
    return currency_idr(value)

@register.filter
def financial_format(value, format_type="currency"):
    """
    Universal financial formatting
    """
    if value is None:
        return "0"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', ''))
        
        if format_type == "currency":
            return currency_idr(value)
        elif format_type == "percentage":
            return percentage_format(value)
        elif format_type == "compact":
            return thousand_format(value)
        elif format_type == "number":
            return number_format(value)
        else:
            return str(value)
    except (ValueError, TypeError):
        return "0"
