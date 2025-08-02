from django.contrib import admin
from .models import Item, Categories, Cart


@admin.register(Item)
class RegisterItem(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ["title", "quantity", "price", "sale"]
    list_editable = ["sale",]
    search_fields = ["name", "description"]
    list_filter = ["sale", "quantity", "category", "rating"]
    fields = [
        "title",
        "category",
        "rating",
        "slug",
        "description",
        "image",
        ("price", "sale"),
        "quantity",
    ]

@admin.register(Categories)
class RegisterCategories(admin.ModelAdmin):
    prepopulated_fields = {"category_slug": ("name",)}
    list_display = ['name']

class CartInline(admin.TabularInline):
    model = Cart
    fields = "contents", "quantity",
    search_fields = "contents", "quantity",
    extra = 1

@admin.register(Cart)
class RegisterCart(admin.ModelAdmin):
    list_display = ["display_user", "display_contents", "quantity"]
    list_filter = ["user", "contents__title",]

    def display_user(self, obj):
        if obj.user:
            return str(obj.user)
        return "Anonymous"

    def display_contents(self, obj):
        return str(obj.contents.title)