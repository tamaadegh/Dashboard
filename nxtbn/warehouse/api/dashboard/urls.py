from rest_framework.routers import DefaultRouter
from django.urls import path
from nxtbn.warehouse.api.dashboard import views as warehouse_views

router = DefaultRouter()
router.register(r'warehouses', warehouse_views.WarehouseViewSet)
router.register(r'stocks', warehouse_views.StockViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('warehouse-wise-variant-stock/<int:variant_id>/', warehouse_views.WarehouseStockByVariantAPIView.as_view(), name='warehouse-wise-variant-stock'),
    path('upate-stock-warehosue-wise/<int:variant_id>/', warehouse_views.UpdateStockWarehouseWise.as_view(), name='update-stock-wirehouse-wise-variant-stock'),
    path('stock-reservation-list/', warehouse_views.StockReservationListAPIView.as_view(), name='update-stock-warehouse-wise-variant-stock'),
    path('stock-reservation-transfer/<int:pk>/', warehouse_views.MergeStockReservationAPIView.as_view(), name='stock-reservation-detail'),
    path('retry-stock-reservation/<uuid:alias>/', warehouse_views.RetryReservationAPIView.as_view(), name='retry-stock-reservation'),
    path('stock-transfer-list/', warehouse_views.StockTransferListCreateAPIView.as_view(), name='stock-transfer-list'),
    path('stock-transfer-detail/<int:id>/', warehouse_views.StockTransferRetrieveUpdateAPIView.as_view(), name='stock-transfer-detail'),
    path('stock-transfer-mark-as-in-transit/<int:pk>/', warehouse_views.StockTransferMarkAsInTransitAPIView.as_view(), name='stock-transfer-mark-as-in-transit'),
    path('stock-transfer-receive/<int:pk>/', warehouse_views.StockTransferReceivingAPI.as_view(), name='stock-transfer-receive'),
    path('stock-transfer-mark-completed/<int:pk>/', warehouse_views.StockTransferMarkedAsCompletedAPIView.as_view(), name='stock-transfer-mark-completed'),
]
