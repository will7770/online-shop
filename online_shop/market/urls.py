from django.urls import path
from . import views
from django.http import HttpResponse

urlpatterns = [
    path('search/', views.catalog, name='search'),
    path('product/<slug:slug>', views.product, name='product'),
    path('cart/', views.cart_view, name='cart'),
    path('cart_add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart_change/<int:product_id>/', views.cart_add, name='cart_change'),
    path('cart_delete/<int:product_id>/', views.cart_add, name='cart_delete'),
    path('<slug:slug>/', views.catalog, name='catalog'),
]