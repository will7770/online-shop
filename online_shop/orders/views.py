from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import OrderForm
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem
from market.models import Cart, Item
from django.db.models import F
from django.core.cache import cache


class CreateOrder(FormView, LoginRequiredMixin):
    template_name = 'orders/create_order.html'
    form_class = OrderForm
    success_url = reverse_lazy('users:profile')

    def get_initial(self):
        initial = super().get_initial()
        initial['first_name'] = self.request.user.first_name
        initial['last_name'] = self.request.user.last_name
        return initial
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = self.request.user
                user_cart = Cart.objects.filter(user=user)

                if user_cart.exists():
                    order = Order.objects.create(
                        user = user,
                        phone_number = form.cleaned_data.get('phone_number'),
                        requires_delivery = form.cleaned_data.get('requires_delivery'),
                        delivery_address = form.cleaned_data.get('delivery_adress'),
                        payment_on_get = form.cleaned_data.get('payment_on_get'),
                    )
                    new_orders = []
                    for cart in user_cart.select_related('contents').select_for_update():
                        if cart.quantity >= cart.contents.quantity:
                            raise ValidationError(f"There is no more {cart.contents.title} in stock, please try again.")
                        
                        new_orders.append(OrderItem(order=order,
                                            product=cart.contents,
                                            name=cart.contents.title,
                                            price=cart.contents.price,
                                            quantity=cart.quantity))
                        Item.objects.filter(id=cart.contents_id).update(quantity=F('quantity') - cart.quantity)
                    
                    OrderItem.objects.bulk_create(new_orders)
                    user_cart.delete()

                    # delete cached data
                    cache.delete(f'users:orders:{self.request.session.session_key}')

                    messages.success(self.request, 'Order created successfully')
                    return redirect('users:profile')

        except ValidationError as err:
            messages.success(self.request, str(err))
            return redirect('users:profile')
    
    def form_invalid(self, form):
        messages.success(self.request, 'Make sure you entered the form correctly.')
        return redirect('orders:create_order')
