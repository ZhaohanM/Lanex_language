from django import template
from lanex.models import Language

register = template.Library()

@register.inclusion_tag('lanex/languages.html')
def get_language_list(current_language=None):
    return {'languages': Language.objects.all(), 'current_language': current_language}