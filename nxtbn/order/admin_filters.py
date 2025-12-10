from django.conf import settings
from django_filters import rest_framework as filters
from nxtbn.order import OrderAuthorizationStatus, OrderChargeStatus, OrderStatus
from nxtbn.order.models import Order
from nxtbn.payment import PaymentMethod
from babel.numbers import get_currency_precision

class OrderFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=OrderStatus.choices)
    charge_status = filters.ChoiceFilter(choices=OrderChargeStatus.choices)
    authorize_status = filters.ChoiceFilter(choices=OrderAuthorizationStatus.choices)
    currency = filters.CharFilter(field_name='currency', lookup_expr='iexact')
    payment_method = filters.ChoiceFilter(choices=PaymentMethod.choices, method='filter_by_payment_method')
    # created_at = filters.DateFromToRangeFilter(field_name='created_at') # eg. ?created_at_after=2023-09-01&created_at_before=2023-09-12
    created_at_before = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    created_at_after = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    min_order_value = filters.NumberFilter(field_name='total_price', lookup_expr='gte', method='filter_min_order_value')
    max_order_value = filters.NumberFilter(field_name='total_price', lookup_expr='lte', method='filter_max_order_value')

    class Meta:
        model = Order
        fields = [
            'status',
            'charge_status',
            'authorize_status',
            'currency',
            'payment_method',
            'created_at_before',
            'created_at_after',
            'min_order_value',
            'max_order_value',
        ]

    def filter_by_payment_method(self, queryset, name, value):
        return queryset.filter(payments__payment_method=value).distinct()
    
    def filter_min_order_value(self, queryset, name, value):
        """
        Filter orders with total_price greater than or equal to the specified min_order_value in units.
        """
        if value is not None:
            precision = get_currency_precision(settings.BASE_CURRENCY)
            min_value_in_subunits = int(value * (10 ** precision))
            return queryset.filter(total_price__gte=min_value_in_subunits)
        return queryset

    def filter_max_order_value(self, queryset, name, value):
        """
        Filter orders with total_price less than or equal to the specified max_order_value in units.
        """
        if value is not None:
            precision = get_currency_precision(settings.BASE_CURRENCY)
            max_value_in_subunits = int(value * (10 ** precision))
            return queryset.filter(total_price__lte=max_value_in_subunits)
        return queryset
