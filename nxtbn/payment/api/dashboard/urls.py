from django.urls import path
from nxtbn.payment.api.dashboard import views as payment_views

urlpatterns = [
    path('refund/<uuid:order_alias>/', payment_views.RefundAPIView.as_view(), name='refund'),
    path('create/', payment_views.PaymentCreateAPIView.as_view(), name='create'),
]
