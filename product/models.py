from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_delete


User = get_user_model()


class Category(models.TextChoices):
    ELECTRONICS = "Electronics"
    LAPTOPS = "Laptops"
    ARTS = "Arts"
    FOOD = "Food"
    HOME = "Home"
    KITCHEN = "Kitchen"
    CLOTHING = "Clothing"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    brand = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=Category.choices)
    ratings = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    user = models.ForeignKey(User, related_name="products", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImages(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/")


@receiver(post_delete, sender=ProductImages)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.comment)