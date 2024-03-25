from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from .models import Product, ProductImages
from .serializers import ProductSerializer, ProductImageSerializer
from .filters import ProductFilter


@api_view(["GET"])
def get_products(request):
    filterset = ProductFilter(request.GET, queryset=Product.objects.all().order_by("id"))
    count = filterset.qs.count()

    #pagination
    resPerPage = 5
    paginator = PageNumberPagination()
    paginator.page_size = resPerPage

    queryset = paginator.paginate_queryset(filterset.qs, request)

    serializer = ProductSerializer(queryset, many=True)
    return Response(
        {
            "count": count,
            "restPerPage": resPerPage,
            "products": serializer.data
         }
        )


@api_view(["GET"])
def get_product_details(request, id):
    product = get_object_or_404(Product, id=id)

    serializer = ProductSerializer(product)

    return Response({"product": serializer.data})


@api_view(["POST"])
def upload_product_images(request):
    data = request.data
    files = request.FILES.getlist("images")

    images = []
    for f in files:
        image = ProductImages.objects.create(
            product=Product(data["product"]),
            image=f
        )
        images.append(image)

    serializer = ProductImageSerializer(images, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def new_product(request):
    data = request.data
    if Product.objects.filter(name=data["name"]).exists():
        return Response({"error": "Product with the given name already exists"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        product = Product.objects.create(**data)
        res_serializer = ProductSerializer(product)

        return Response({"Product": res_serializer.data})

    return Response(serializer.errors)


@api_view(["PUT"])
def update_product(request, id):
    product = get_object_or_404(Product, id=id)
    data = request.data

    # Check if produdct belong to user
    if not product.user == request.user:
        return Response({"error": "This product does not belong to you."}, status=status.HTTP_400_BAD_REQUEST)
    product.name = data["name"]
    product.description = data["description"]
    product.price = data["price"]
    product.brand = data["brand"]
    product.stock = data["stock"]
    product.ratings = data["ratings"]
    product.category = data["category"]
    product.save()

    serializer = ProductSerializer(product)

    return Response({"Prodict": serializer.data}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    # Check if produdct belong to user
    if not product.user == request.user:
        return Response({"error": "You are not allowed to delete this product."}, status=status.HTTP_400_BAD_REQUEST)

    images = ProductImages.objects.filter(product=product)
    for image in images:
        image.delete()

    product.delete()

    return Response({"success": "Product deleted successfully"}, status=status.HTTP_200_OK)