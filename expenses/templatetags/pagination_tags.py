from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):

    query_dict = context['request'].GET.copy()

    for key, value in kwargs.items():
        query_dict[key] = value

    params = []
    for key in query_dict:
        values = query_dict.getlist(key)
        for val in values:
            params.append((key, val))
    return urlencode(params)
