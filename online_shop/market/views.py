from django.shortcuts import render, get_list_or_404
from .models import Categories, Item, Cart
from django.http import JsonResponse
from .utils import get_user_carts, query_search
from django.template.loader import render_to_string
from django.core.paginator import Paginator


def catalog(request, slug=None):
    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', None)
    query = request.GET.get('q', None)

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
    carts = Cart.objects.filter(user=request.user)
    context = {'carts': carts}
    return render(request=request, template_name='cart.html', context=context)


def cart_add(request, product_id):

    product =  Item.objects.get(id=product_id)

    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user, contents=product)

        if carts.exists():
            cart = carts.first()
            if cart:
                cart.quantity += 1
                cart.save()
        else:
            Cart.objects.create(user=request.user, contents=product, quantity=1)
    else:
        carts = Cart.objects.filter(session_key=request.session.session_key, contents=product)
        if carts.exists():
            cart = carts.first()
            if cart:
                cart.quantity += 1
                cart.save()
        else:
            Cart.objects.create(session_key=request.session.session_key, contents=product, quantity=1)
    
    user_cart = get_user_carts(request)
    cart_html = render_to_string('cart.html', {"cart": user_cart}, request=request)
    response_data = {
        'cart_html': cart_html
    }
    return JsonResponse(response_data)


def cart_change(request, product_id):
    pass


def cart_delete(request, product_id):
    pass
