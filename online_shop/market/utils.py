from .models import Cart, Item
from django.db.models import Q

def get_user_carts(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).select_related('contents')
    
    if not request.session.session_key:
        request.session.create()
    return Cart.objects.filter(session_key=request.session.session_key).select_related('contents')


def query_search(query):
    if query.isdigit() and len(query) <= 5:
        return Item.objects.filter(id=int(query))
    
    keywords = [word for word in query.split() if len(word) > 2]
    q_obj = Q()

    for keyword in keywords:
        q_obj |= Q(description__icontains=keyword)
        q_obj |= Q(title__icontains=keyword)

    return Item.objects.filter(q_obj)
