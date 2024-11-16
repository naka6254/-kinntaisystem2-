# custom_filters.py
from django import template
from django.forms import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    if isinstance(field, BoundField):
        return field.as_widget(attrs={'class': css_class})
    # BoundField でない場合は、そのまま返す
    return field

def display_if_not_empty(value):
    """値が存在する場合のみ表示"""
    return value if value else ""