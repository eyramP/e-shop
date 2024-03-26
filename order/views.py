from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from product.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def new_order(request):
    user = request.user
    data = request.data

    order_items = data['order_items']
    if order_items and len(order_items) == 0:
        return Response({"error": "No order items, please add at least one product."}, status=status.HTTP_400_BAD_REQUEST)

    # create order
    total_amount = sum(item["price"] * item["quantity"] for item in order_items)
    order = Order.objects.create(
        user=user,
        street=data["street"],
        city=data["city"],
        state=data["state"],
        zip=data["zip"],
        phone_number=data["phone_number"],
        country=data["country"],
        total_amount=total_amount,
    )

    # create order items and add them to the order
    for item in order_items:
        product = Product.objects.get(id=item["product"])

        item = OrderItem.objects.create(
            product=product,
            order=order,
            product_name=product.name,
            quantity=item["quantity"],
            price=item["price"]
        )

        # update product stock
        product.stock -= item.quantity
        product.save()

        serializer = OrderSerializer(order)

        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_orders(request):
    orders = Order.objects.prefetch_related("items").all()
    serrializer = OrderSerializer(orders, many=True)

    return Response({"orders": serrializer.data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order_details(request, id):
    try:
        order = Order.objects.prefetch_related("items").get(id=id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status.HTTP_404_NOT_FOUND)
    serrializer = OrderSerializer(order)

    return Response({"order": serrializer.data})

