from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.get_products, name="get_products"),
    path("products/<str:id>/", views.get_product_details, name="get_products_details"),
]
