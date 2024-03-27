import os
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from product.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer
from .filters import OrderFilter

from utils.helpers import get_current_host
import stripe


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


stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    YOUR_DOMAIN = get_current_host(request)

    user = request.user
    data = request.data

    order_items = data["order_items"]

    shipping_details = {
        "street": data["street"],
        "city": data["city"],
        "state": data["state"],
        "zip_code": data["zip"],
        "phone_number": data["phone_number"],
        "country": data["country"],
        "user": user.id
    }

    checkout_order_items = []
    for item in order_items:
        product = Product.objects.get(id=item["product"])
        checkout_order_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": product.name,
                    "images": [product.images],
                    "metadata": {"product_id": product.id}
                },
                "unit_amount": int(product.price * 100)
            },
            "quantity": item["quantity"],
        })

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        metadata=shipping_details,
        line_items=checkout_order_items,
        customer_email=user.email,
        mode="payment",
        success_url=YOUR_DOMAIN,
        cancel_url=YOUR_DOMAIN,
    )

    return Response({"session": session})


@api_view(["POST"])
def stripe_webhook(request):
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            webhook_secret
        )

    except ValueError as e:
        return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # line_items are order items
        line_items = stripe.checkout.Session.list_line_items(session["id"])
        price = session["amount_total"] / 100

        order = Order.objects.create(
            user=User(session.metadata.user),
            street=session.metadata.street,
            city=session.metadata.city,
            state=session.metadata.state,
            zip=session.metadata.zip_code,
            phone_number=session.metadata.phone_number,
            country=session.metadata.country,
            total_amount=price,
            payment_mode="Card",
            payment_status="Paid"
        )

        for item in line_items["data"]:

            print("item", item)

            line_product = stripe.Product.retrieve(item.price.product)
            product_id = line_product.metadata.product_id

            product = Product.objects.get(id=product_id)

            item = OrderItem.objects.create(
                product=product,
                order=order,
                product_name=product.name,
                quantity=item.quantity,
                price=item.price.unit_amount / 100,
                image=line_product.images[0]
            )

            product.stock -= item.quantity
            product.save()

        return Response({"success": "Payment successful"}, status=status.HTTP_200_OK)

