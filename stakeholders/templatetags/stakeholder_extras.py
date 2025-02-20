from django import template

register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
    try:
        return value - arg
    except (TypeError, ValueError):
        return ''