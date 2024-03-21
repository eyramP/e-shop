from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "description",
        "price",
        "stock",
        "category",
        "brand",
        "ratings",
        "user",
        "created_at",
        ]
