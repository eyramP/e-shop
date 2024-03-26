from django.urls import path
from . import views

urlpatterns = [
    path("order/new/", views.new_order, name="new_order"),
    path("orders/", views.get_orders, name="all_orders"),
    path("orders/<str:id>/", views.get_order_details, name="order_details"),
]