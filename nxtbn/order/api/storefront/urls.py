from django.urls import path
from nxtbn.order.api.storefront import views as order_views

urlpatterns = [
    path('orders/', order_views.OrderListView.as_view(), name='order-list'),
    path('eastimate/', order_views.OrderEastimateAPIView.as_view(), name='order_estimate'),
    path('create/', order_views.OrderCreateAPIView.as_view(), name='order_create'),
    path('orders/return-request/', order_views.OrderReturnRequestAPIView.as_view(), name='return-request'),
]
