from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """
    Zachowuje aktualne parametry GET i aktualizuje je o nowe wartości.
    """
    query_dict = context['request'].GET.copy()  
    for key, value in kwargs.items():
        query_dict[key] = value  
    return urlencode(query_dict)  