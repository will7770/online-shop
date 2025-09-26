from .models import Cart, Item
from django.db.models import Q, Count, Sum, F, Value, IntegerField, FloatField
from django.db.models.functions import Coalesce
from django.contrib.postgres.search import SearchVector
from django.core.cache import cache
import pickle
import hashlib


def get_user_carts(request):
    if request.user.is_authenticated:
        base = Cart.objects.filter(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        base = Cart.objects.filter(session_key=request.session.session_key)
    base = base.annotate(total_item_price=F('quantity')*F('contents__price')).select_related('contents')

    cart_totals = base.aggregate(
        total_count=Coalesce(Sum('quantity'), Value(0), output_field=IntegerField()),
        total_price=Coalesce(Sum('total_item_price'), Value(0.0), output_field=FloatField())
    )

    return {
        "data": base,
        "totals": cart_totals
    }


def query_search(query):
    if query.isdigit() and len(query) <= 5:
        return Item.objects.filter(id=int(query))
    
    qset = Item.objects.annotate(searchv=SearchVector('title', 'description')).filter(searchv=query)
    return qset


def generate_catalog_cache_key(request, slug, page):
    params = request.GET.items()
    hashed = pickle.dumps(sorted(params))
    digest = hashlib.sha256(hashed).hexdigest()

    return f"cache:catalog:{slug}:{page}:{digest}"