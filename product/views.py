from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from .models import Product
from .serializers import ProductSerializer
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
