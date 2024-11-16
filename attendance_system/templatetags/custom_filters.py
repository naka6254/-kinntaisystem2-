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

def hide_none(value):
    """None を非表示にする"""
    return "" if value is None else value