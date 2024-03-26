from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from product.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer
from .filters import OrderFilter

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
    filterset = OrderFilter(request.GET, queryset=Order.objects.prefetch_related("items").all().order_by("id"))

    count = filterset.qs.count()

    # Apply pagination
    res_per_page = 2
    paginator = PageNumberPagination()
    paginator.page_size = res_per_page

    queryset = paginator.paginate_queryset(filterset.qs, request)

    # orders = Order.objects.prefetch_related("items").all()
    serrializer = OrderSerializer(queryset, many=True)

    return Response({
        "count": count,
        "res_per_page": res_per_page,
        "orders": serrializer.data
        })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order_details(request, id):
    try:
        order = Order.objects.prefetch_related("items").get(id=id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status.HTTP_404_NOT_FOUND)
    serrializer = OrderSerializer(order)

    return Response({"order": serrializer.data})


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_order(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.user != request.user:
        return Response({"error": "You cannot update this order"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    order.city = data["city"]
    order.street = data["street"]
    order.state = data["state"]
    order.zip = data["zip"]
    order.phone_number = data["phone_number"]
    order.country = data["country"]

    order.save()

    serializer = OrderSerializer(order)
    return Response({"order": serializer.data}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_order(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not user.is_superuser:
        return Response({"error": "Only admin users can process an order"}, status=status.HTTP_403_FORBIDDEN)

    order.delete()

    return Response({"success": "Order deleted successfully"}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdminUser])
def process_order(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not user.is_superuser:
        return Response({"error": "Only admin users can process an order"}, status=status.HTTP_403_FORBIDDEN)
    order.order_status = request.data["status"]
    order.save()

    return Response({"success": "order has been processed"})