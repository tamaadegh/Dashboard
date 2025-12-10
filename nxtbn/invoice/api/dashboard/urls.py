from django.urls import path
from nxtbn.invoice.api.dashboard import views

urlpatterns = [
    path('api/invoice/<uuid:alias>/', views.OrderInvoiceAPIView.as_view(), name='invoice-api'),
]
