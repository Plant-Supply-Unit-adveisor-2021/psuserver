from django import template

from website.utils import get_i18n_tag

register = template.Library()


@register.simple_tag(takes_context=True)
def translate_url(context, language_code):
    """
    template tag to change out the i18n language identifier in the url
    """
    request = context['request']
    new_url = request.path.replace('/' + get_i18n_tag(request) + '/', '/' + language_code + '/')
    return new_url


@register.simple_tag(takes_context=True)
def i18n_code(context):
    """
    template tag to change out the i18n language identifier in the url
    """
    return get_i18n_tag(context['request'])


@register.filter
def cut(value, arg):
    """
    template filter to replace all appearances of arg through nothing
    """
    return value.replace(arg, '')

@register.filter
def round(value, digits):
    """
    template filter to round a floating point number
    """
    try:
        return '{0:.{1}f}'.format(float(value).__round__(digits), max(digits,0))
    except Exception:
        # some kind of error occured -> do not touch value
        return value


@register.filter
def plain(value):
    """
    template filter to get string representation
    """
    return str(value)
