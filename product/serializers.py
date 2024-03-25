from rest_framework import serializers
from .models import Product, ProductImages



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ["id", "product", "image"]


class SimpleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ["image"]


class ProductSerializer(serializers.ModelSerializer):
    images = SimpleImageSerializer(many=True, read_only=True)

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
            "images",
        ]

        # extra_kwargs = {
        #     "name": {"required": True, 'allow_blank': False},
        #     "brand": {"required": True, 'allow_blank': False},
        #     "stock": {"required": True, 'allow_blank': False},
        #     "category": {"required": True, 'allow_blank': False},
        # }
