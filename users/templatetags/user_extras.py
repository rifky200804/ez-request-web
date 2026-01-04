from django import template

register = template.Library()

@register.filter
def has_employee(user):
    return hasattr(user, 'employee')
