from django import template

register = template.Library()


@register.filter
def get(directory, i):
    return directory.get(i)
