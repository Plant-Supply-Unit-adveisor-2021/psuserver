from django import template

from website.utils import geti18nTag

register = template.Library()

@register.simple_tag(takes_context=True)
def translate_url(context, language_code):
    """
    template tag to change out the i18n languauge identifier in the url
    """
    request = context['request']
    new_url = request.path.replace('/'+geti18nTag(request)+'/', '/'+language_code+'/')
    return new_url

@register.filter
def cut(value, arg):
    """
    template filter to replace all appearences of arg through nothing
    """
    return value.replace(arg, '')
