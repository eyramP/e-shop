from django.db import models
from django.contrib.auth.models import User

from product.models import Product


# Create your models here.
class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = "Paid"
        UNPAID = "Unpaid"

    class OrderStatus(models.TextChoices):
        PROCESSING = "Processing"
        SHIPPED = "Shipped"
        DELIVERED = "Delivered"

    class PaymentMode(models.TextChoices):
        COD = "Cash on devliery"
        CARD = "Card"

    street = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=7, decimal_places=2)
    payment_status = models.CharField(
        max_length=100,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID)
    order_status = models.CharField(
        max_length=100,
        choices=OrderStatus.choices,
        default=OrderStatus.PROCESSING)
    payment_mode = models.CharField(
        max_length=100,
        choices=PaymentMode.choices,
        default=PaymentMode.COD
    )
    user = models.ForeignKey(
        User, related_name="Orders",
        on_delete=models.SET_NULL,
        null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.product_name
