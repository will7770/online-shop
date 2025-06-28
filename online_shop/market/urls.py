from django.urls import path
from . import views
from django.http import HttpResponse

urlpatterns = [
    path('search/', views.catalog, name='search'),
    path('product/<slug:slug>', views.product, name='product'),
    path('cart/', views.cart_view, name='cart'),
    path('cart_add/', views.cart_add, name='cart_add'),
    path('cart_change/', views.cart_change, name='cart_change'),
    path('cart_delete/', views.cart_delete, name='cart_delete'),
    path('<slug:slug>/', views.catalog, name='catalog'),
]