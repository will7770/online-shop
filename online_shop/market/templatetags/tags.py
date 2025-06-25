from django import template
from django.utils.http import urlencode

from market.models import Categories, Cart


register = template.Library()


@register.simple_tag()
def tag_categories():
    return Categories.objects.all()


@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)


@register.simple_tag()
def display_cart_items(request):
    user = request.user
    return Cart.objects.filter(user=user).select_related('contents')


@register.simple_tag()
def display_cart_quantity(request):
    user = request.user
    return Cart.objects.filter(user=user).total_items()