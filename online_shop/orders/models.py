from django.db import models
from users.models import User
from market.models import Item
from django.db.models import Sum


class OrderStatus(models.TextChoices):
    VERIFICATION = 'VF', 'Verification'
    DELIVERY = 'DV', 'Delivering'
    READY = 'RD', 'Ready'


class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20)
    requires_delivery = models.BooleanField(default=False)
    delivery_address = models.TextField(null=True, blank=True)
    payment_on_get = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(choices=OrderStatus.choices, default=OrderStatus.VERIFICATION)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order №{self.pk} / buyer: {self.user.first_name if self.user.first_name else self.user.username}"
    
    @property
    def get_readable_status(self):
        return OrderStatus(self.status).label


class OrderItemQueryset(models.QuerySet):
    
    def total_price(self):
        return sum(cart.products_price() for cart in self)
    
    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0


class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Item, on_delete=models.SET_DEFAULT, null=True, default=None)
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = "order_item"


    objects = OrderItemQueryset.as_manager()

    def item_total_price(self):
        return round(self.product.sell_price() * self.quantity, 2)

    def __str__(self):
        return f"Product {self.name} for order №{self.order.pk}"