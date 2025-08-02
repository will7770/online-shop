from django.contrib import admin
from reviews.models import Review

@admin.register(Review)
class RegisterReview(admin.ModelAdmin):
    list_display = ["author", "item", "title", "rating", "created_at"]
    search_fields = ["name", "description"]
    list_filter = ["author", "item"]
    fields = [
        "author",
        "item",
        "title",
        "rating",
        "text",
    ]