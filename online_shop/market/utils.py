from .models import Cart, Item
from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from django.core.cache import cache


def get_user_carts(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).select_related('contents')
    
    else:
        if not request.session.session_key:
            request.session.create()
        return Cart.objects.filter(session_key=request.session.session_key).select_related('contents')


def query_search(query):
    if query.isdigit() and len(query) <= 5:
        return Item.objects.filter(id=int(query))
    
    qset = Item.objects.annotate(searchv=SearchVector('title', 'description')).filter(searchv=query)
    return qset
