from django_filters import rest_framework as filters

from order.models import Order

class OrderFilter(filters.FilterSet):
    class Meta:
        model = Order
        fields = [
            "id", 
            "payment_mode",
            "payment_status"
        ]
