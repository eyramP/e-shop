from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Product, ProductImages, Review
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
@permission_classes([IsAuthenticated,])
def new_product(request):
    data = request.data
    if Product.objects.filter(name=data["name"]).exists():
        return Response({"error": "Product with the given name already exists"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        product = Product.objects.create(**data,  user=request.user)
        res_serializer = ProductSerializer(product)

        return Response({"Product": res_serializer.data})

    return Response(serializer.errors)


@api_view(["PUT"])
@permission_classes([IsAuthenticated,])
def update_product(request, id):
    product = get_object_or_404(Product, id=id)
    data = request.data

    # Check if produdct belong to user
    if not product.user == request.user:
        return Response({"error": "You cannot update this product."}, status=status.HTTP_403_FORBIDDEN)
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
@permission_classes([IsAuthenticated,])
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    # Check if produdct belong to user
    if not product.user == request.user:
        return Response({"error": "You are not allowed to delete this product."}, status=status.HTTP_403_FORBIDDEN)

    images = ProductImages.objects.filter(product=product)
    for image in images:
        image.delete()

    product.delete()

    return Response({"success": "Product deleted successfully"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request, id):
    user = request.user
    product = get_object_or_404(Product, id=id)
    data = request.data

    review = product.reviews.filter(user=user)

    if (data["rating"] <= 0 or data["rating"] > 5):
        return Response({"error": "Rating must be between 1 to 5"}, status=status.HTTP_400_BAD_REQUEST)

    elif review.exists():
        new_review = {"rating": data["rating"], "comment": data["comment"]}
        review.update(**new_review)

        rating = product.reviews.aggregate(
            avg_ratings=Avg("rating")
        )
        product.ratings = rating["avg_ratings"]
        product.save()

        return Response({"success": "Review updated."}, status=status.HTTP_200_OK)

    else:
        Review.objects.create(
           user=user,
           product=product,
           comment=data["comment"],
           rating=data["rating"]
        )

        rating = product.reviews.aggregate(
            avg_ratings=Avg("rating")
        )
        product.ratings = rating["avg_ratings"]
        product.save()

        return Response({"success": "Review posted."}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_review(request, id):
    user = request.user
    product = get_object_or_404(Product, id=id)

    review = product.reviews.filter(user=user)
    if review.exists():
        review.delete()

        rating = product.reviews.aggregate(
            avg_ratings=Avg("rating")
        )

        if rating["avg_ratings"] is None:
            rating["avg_ratings"] = 0

        product.ratings = rating["avg_ratings"]
        product.save()

        return Response({"success": "Review deleted."})

    else:
        return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)