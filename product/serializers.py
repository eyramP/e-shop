from rest_framework import serializers
from .models import Product, ProductImages


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ["id", "product", "image"]