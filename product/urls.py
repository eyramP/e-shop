from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.get_products, name="get_products"),
    path("products/<str:id>/", views.get_product_details, name="get_products_details"),
    path("upload_images/", views.upload_product_images, name="upload_images"),
    path("new_product/", views.new_product, name="new_product"),
    path("products/<str:id>/update/", views.update_product, name="update_product"),
    path("products/<str:id>/delete/", views.delete_product, name="delete_product"),

    path("products/<str:id>/review/", views.create_review, name="create_review"),
    path("products/<str:id>/delete_review/", views.delete_review, name="delete_review"),
]
