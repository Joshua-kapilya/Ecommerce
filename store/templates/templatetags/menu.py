from django import template

register = template.Library()

@register.inclusion_tag('core/menu.html')
def menu():
	return{}