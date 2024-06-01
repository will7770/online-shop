from django.contrib import admin
from .models import Item, Categories, Cart

# admin.site.register(Item)
# admin.site.register(Categories)

@admin.register(Item)
class RegisterItem(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Categories)
class RegisterCategories(admin.ModelAdmin):
    prepopulated_fields = {"category_slug": ("name",)}

admin.site.register(Cart)
# @admin.register(Cart)
# class RegisterCart(admin.ModelAdmin):
