from django import template
from django.forms.widgets import Widget

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Add CSS class to form field
    """
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    elif isinstance(field, str):
        # If it's already rendered HTML, wrap it with the class
        return f'<div class="{css_class}">{field}</div>'
    else:
        return field

@register.filter
def add_attr(field, attr_string):
    """
    Add attributes to form field
    Usage: {{ field|add_attr:"class:form-control,placeholder:Enter text" }}
    """
    if hasattr(field, 'as_widget'):
        attrs = {}
        for attr in attr_string.split(','):
            key, value = attr.split(':')
            attrs[key.strip()] = value.strip()
        return field.as_widget(attrs=attrs)
    elif isinstance(field, str):
        # If it's already rendered HTML, return as is
        return field
    else:
        return field

@register.filter
def widget_class(field, css_class):
    """
    Add CSS class to form field widget
    """
    if hasattr(field, 'field') and hasattr(field.field, 'widget'):
        return field.field.widget.attrs.update({'class': css_class}) or field
    elif hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    else:
        return field
