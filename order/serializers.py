from rest_framework import serializers
from order.models import Order, OrderItem
from product.serializers import SimpleProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    # items = OrderItemSerializer(many=True, read_only=True)
    items = serializers.SerializerMethodField(method_name="get_items", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "street",
            "state",
            "city",
            "zip",
            "phone_number",
            "country",
            "payment_status",
            "order_status",
            "user",
            "payment_mode",
            "created_at",
            "items"
        ]

    def get_items(self, obj):
        items = obj.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return (serializer.data)

