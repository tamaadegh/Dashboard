from django.urls import path
from .views import InitiatePaymentAPIView, hubtel_callback, PaymentStatusAPIView

urlpatterns = [
    path('initiate/', InitiatePaymentAPIView.as_view(), name='hubtel_initiate'),
    path('callback/', hubtel_callback, name='hubtel_callback'),
    path('status/<str:client_reference>/', PaymentStatusAPIView.as_view(), name='hubtel_status'),
]
