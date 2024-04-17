# employees/templatetags/duration_filter.py
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def duration(value):
    if value:
        duration = value.total_seconds() / 3600  # Convert seconds to hours
        return '{:.2f} hours'.format(duration)
    return ''
