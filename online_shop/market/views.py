from django.shortcuts import render
from .models import Categories, Item, Cart
from django.http import JsonResponse
from .utils import query_search, generate_catalog_cache_key
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import F, Prefetch, FilteredRelation, Q
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from reviews.forms import ReviewForm
from reviews.models import Review
from rest_framework.views import APIView
from rest_framework.request import Request




def catalog(request, slug=None):
    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', 'id')
    query = request.GET.get('q', None)
    price_min, price_max = request.GET.get('price_min', None), request.GET.get('price_max', None)

    filters_per_request = 0
    slug = slug or 'all'

    goods = Item.objects.all()
    if slug != 'all':
        goods = Item.objects.annotate(
            joined_category=FilteredRelation(relation_name='category', condition=Q(category__category_slug=slug))).filter(
                joined_category__isnull=False
            )

    if query:
        goods = query_search(query)

    if price_min:
        filters_per_request += 1
        goods = goods.filter(price__gte=price_min)
    if price_max:
        filters_per_request += 1
        goods = goods.filter(price__lte=price_max)

    if on_sale:
        filters_per_request += 1
        goods = goods.filter(sale__gt=0)
    if order_by and order_by != "default":
        filters_per_request += 1
        goods = goods.order_by(order_by)


    # Cache pages that get accessed more often, skip edge cases with a lot of filters
    paginator = Paginator(goods, 9)

    if filters_per_request < 3:
        key = generate_catalog_cache_key(request, slug, page)
        current_page = cache.get(key)
        if not current_page:
            current_page = paginator.page(int(page))
            cache.set(key, current_page, timeout=60*15)
    else:
        current_page = paginator.page(int(page))

    context = {
        'goods': current_page,
        'slug_url': slug
    }
    return render(request, 'store.html', context=context)



def product(request, slug):
    sorting_method = request.GET.get('sort_by', 'newest')
    base_queryset = Review.objects.all()

    if sorting_method == 'newest':
        base_queryset = base_queryset.order_by('-created_at')
    elif sorting_method == 'oldest':
        base_queryset = base_queryset.order_by('created_at')
    elif sorting_method == 'highest':
        base_queryset = base_queryset.order_by('-rating')
    elif sorting_method == 'lowest':
        base_queryset = base_queryset.order_by('rating')


    product = Item.objects.filter(slug=slug).prefetch_related(Prefetch('reviews', queryset=base_queryset)).first()
    review_percentages_qs = Review.objects.reviews_percentage(item_slug=slug)

    review_percentages = cache.get_or_set(f'review_percentages:{slug}', list(review_percentages_qs), timeout=60*30)

    context = {
        'product': product,
        'form': ReviewForm(),
        'percentages': review_percentages
    }

    return render(request, 'product.html', context=context)


def cart_view(request):
    return render(request, 'cart.html')
