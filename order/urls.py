from django.urls import path
from . import views

urlpatterns = [
    path("order/new/", views.new_order, name="new_order"),
    path("orders/", views.get_orders, name="all_orders"),
    path("orders/<str:id>/", views.get_order_details, name="order_details"),
    path("orders/<str:id>/update/", views.update_order, name="update_order"),
    path("orders/<str:id>/delete/", views.delete_order, name="delete_order"),
    path("orders/<str:id>/process/", views.process_order, name="process_order"),
]