from rest_framework import serializers

from account.serializers import SimpleUserSerializer
from .models import Product, ProductImages, Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "product", "user", "comment", "rating"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ["id", "product", "image"]


class SimpleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ["image"]


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name"]


class ProductSerializer(serializers.ModelSerializer):
    images = SimpleImageSerializer(many=True, read_only=True)
    user = SimpleUserSerializer(read_only=True)
    # reviews = ReviewSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField(method_name="get_reviews")

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
            "reviews"
        ]

        # extra_kwargs = {
        #     "name": {"required": True, 'allow_blank': False},
        #     "brand": {"required": True, 'allow_blank': False},
        #     "stock": {"required": True, 'allow_blank': False},
        #     "category": {"required": True, 'allow_blank': False},
        # }

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)

        return serializer.data

