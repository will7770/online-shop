from django.contrib import admin
from .models import User
from market.admin import CartInline
from orders.admin import OrderInline

@admin.register(User)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ["username", "first_name", "last_name", "email",]
    search_fields = ["username", "first_name", "last_name", "email",]

    

    inlines = [CartInline, OrderInline]