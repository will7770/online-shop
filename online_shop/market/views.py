from django.shortcuts import redirect, render, get_list_or_404
from .models import Categories, Item, Cart
from django.http import JsonResponse
from .utils import get_user_carts, query_search
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import F



def catalog(request, slug=None):
    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', None)
    query = request.GET.get('q', None)

    slug = slug or 'all'

    if slug == 'all':
        goods = Item.objects.all()
    elif query:
        goods = query_search(query)
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
    product = Item.objects.get(slug=slug)
    return render(request, 'product.html', context={'product': product})


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