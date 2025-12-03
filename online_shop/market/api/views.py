from django.shortcuts import render
from ..models import Categories, Item, Cart
from django.http import JsonResponse
from ..utils import query_search, generate_catalog_cache_key
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import F, Prefetch, FilteredRelation, Q
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.request import Request
from .serializers import CartAddSerializer, CartChangeSerializer, CartDeleteSerializer
from rest_framework import status
from rest_framework.response import Response




class CartAdd(APIView):
    def post(self, request: Request):
        serializer = CartAddSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        try:
            product = Item.objects.get(id=data['product_id'])
        except Item.DoesNotExist:
            return Response({"error": "item is not found"}, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
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
        return Response(response, status=status.HTTP_201_CREATED)


class CartChange(APIView):
    def post(self, request: Request):
        serializer = CartChangeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        cart_id, quantity = data['cart_id'], data['quantity']
        Cart.objects.filter(id=cart_id).update(quantity=quantity)

        rendered_cart = render_to_string('includes/included_cart.html', request=request)
        response = {
            "cart_items_html": rendered_cart
        }
        return Response(response)


class CartDelete(APIView):
    def post(self, request: Request):
        serializer = CartDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        cart_product = Cart.objects.filter(id=data['cart_id']).first()
        cart_product.delete()
        
        rendered_cart = render_to_string("includes/included_cart.html", request=request)
        response = {"message": "Deleted item from cart",
                    "cart_items_html": rendered_cart}
        return Response(response)