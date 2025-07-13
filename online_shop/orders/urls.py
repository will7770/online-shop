from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create-order/', views.CreateOrder.as_view(), name='create_order')
]
