from django.urls import path
from nxtbn.purchase.api.dashboard import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'purchase-orders', views.PurchaseViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('inventory-receiving/<int:pk>/', views.InventoryReceivingAPI.as_view(), name='inventory-receiving'),
]
