from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Category(models.TextChoices):
    ELECTRONICS = "Electronics"
    LAPTOPS = "Laptops"
    ARTS = "Arts"
    FOOD = "Food"
    HOME = "Home"
    KITCHEN = "Kitchen"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    brand = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=Category.choices)
    ratings = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    user = models.ForeignKey(User, related_name="products", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
