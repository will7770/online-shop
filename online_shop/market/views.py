from django.shortcuts import render
from .models import Categories, Item, Cart
from django.http import JsonResponse
from .utils import query_search
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import F, Prefetch
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from reviews.forms import ReviewForm
from reviews.models import Review



def catalog(request, slug=None):
    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', 'id')
    query = request.GET.get('q', None)

    slug = slug or 'all'

    if query:
        goods = query_search(query)
    elif slug == 'all':
        goods = Item.objects.all()
    else:
        goods = Item.objects.filter(category__category_slug=slug)

    if on_sale:
        goods = goods.filter(sale__gt=0)
    if order_by and order_by != "default":
        goods = goods.order_by(order_by)

    paginator = Paginator(goods, 3)
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


@require_POST
def cart_add(request):
    with transaction.atomic():
        product = Item.objects.filter(id=request.POST.get('product_id')).first()
        if request.user.is_authenticated:
            cart_product, created = Cart.objects.select_for_update().get_or_create(user=request.user, contents=product, defaults={'quantity': 1})
        else:
            if not request.session.session_key:
                request.session.create()
            user_session = request.session.session_key
            cart_product, created = Cart.objects.select_for_update().get_or_create(session_key=user_session, contents=product, defaults={'quantity': 1})
        
        if not created:
            cart_product.quantity += 1
            cart_product.save()
    

    rendered_cart = render_to_string("includes/included_cart.html", request=request)
    response = {
        "message": "Added item to cart",
        "cart_items_html": rendered_cart
    }
    return JsonResponse(response)


@require_POST
def cart_change(request):
    cart_id, quantity = request.POST['cart_id'], request.POST['quantity']
    Cart.objects.filter(id=cart_id).update(quantity=quantity)

    rendered_cart = render_to_string('includes/included_cart.html', request=request)
    response = {
        "cart_items_html": rendered_cart
    }
    return JsonResponse(response)


@require_POST
def cart_delete(request):
    cart_product = Cart.objects.filter(id=request.POST.get('cart_id')).first()
    cart_product.delete()
    
    rendered_cart = render_to_string("includes/included_cart.html", request=request)
    response = {"message": "Deleted item from cart",
                "cart_items_html": rendered_cart}
    return JsonResponse(response)