from django import template
from delivery_service.translation import TRANSLATIONS

register = template.Library()


@register.simple_tag(takes_context=True)
def trans(context, text):
    """
    Tag for translating text in templates.
    """
    request = context.get('request')
    if not request:
        return text
    lang = request.session.get('language', 'en')
    if lang == 'uk':
        return TRANSLATIONS['uk'].get(text, text)
    return text
