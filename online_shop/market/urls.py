from django.urls import path
from . import views
from django.http import HttpResponse
from .api import views as api_views



app_name = "main"

urlpatterns = [
    path('search/', views.catalog, name='search'),
    path('product/<slug:slug>', views.product, name='product'),
    path('cart/', views.cart_view, name='cart'),
    path('cart_add/', api_views.CartAdd.as_view(), name='cart_add'),
    path('cart_change/', api_views.CartChange.as_view(), name='cart_change'),
    path('cart_delete/', api_views.CartChange.as_view(), name='cart_delete'),
    path('catalog/', views.catalog, {'slug': 'all'}, name='catalog_default'),
    path('catalog/<slug:slug>', views.catalog, name='catalog'),
]