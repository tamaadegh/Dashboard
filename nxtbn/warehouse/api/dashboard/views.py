
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import generics, status
from nxtbn.core.admin_permissions import CommonPermissions, GranularPermission
from nxtbn.core.enum_perms import PermissionsEnum
from nxtbn.order.models import Order
from nxtbn.product.models import ProductVariant
from nxtbn.warehouse import StockMovementStatus
from nxtbn.warehouse.models import StockReservation, StockTransfer, StockTransferItem, Warehouse, Stock
from nxtbn.warehouse.api.dashboard.serializers import StockReservationSerializer, StockTransferReceivingSerializer, StockTransferSerializer, StockUpdateSerializer, MergeStockReservationSerializer, WarehouseSerializer, StockSerializer, StockDetailViewSerializer
from nxtbn.core.paginator import NxtbnPagination


from rest_framework import filters as drf_filters
from rest_framework.views import APIView
import django_filters
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.db.models.functions import Coalesce
from django.db.models import F, Sum, Q
from django.db import transaction
from rest_framework.exceptions import ValidationError

from nxtbn.warehouse.utils import reserve_stock
from rest_framework.exceptions import APIException



class WarehouseViewSet(viewsets.ModelViewSet):
    permission_classes = (CommonPermissions, )
    model = Warehouse
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    pagination_class = None


class StockFilter(filters.FilterSet):
    warehouse = filters.CharFilter(field_name='warehouse__name', lookup_expr='iexact')
    created_at = filters.DateTimeFromToRangeFilter(field_name='created_at')

    class Meta:
        model = Stock
        fields = [
            'warehouse',
            'created_at'
        ]
  
class StockFilterMixin:
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter
    ] 
    search_fields = [
        'warehouse__name',
        'product_variant__name'
    ]
    ordering_fields = [
        'created_at',
    ]
    filterset_class = StockFilter


class StockViewSet(StockFilterMixin, viewsets.ModelViewSet):
    permission_classes = (CommonPermissions, )
    model = Stock
    queryset = Stock.objects.select_related('warehouse', 'product_variant').all()
    pagination_class = NxtbnPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StockDetailViewSerializer
        return StockSerializer



class WarehouseStockByVariantAPIView(APIView):
    permission_classes = (CommonPermissions, )
    model = ProductVariant
    def get(self, request, variant_id):
        try:
            # Fetch the product variant
            product_variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response({"error": "Variant not found."}, status=status.HTTP_404_NOT_FOUND)

        # Query all warehouses and annotate stock data for the given variant
        warehouses = Warehouse.objects.annotate(
            total_quantity=Coalesce(
                Sum('stocks__quantity', filter=Q(stocks__product_variant=product_variant)), 
                0
            ),
            reserved_quantity=Coalesce(
                Sum('stocks__reserved', filter=Q(stocks__product_variant=product_variant)), 
                0
            )
        )

        # Prepare the response data
        data = []
        for warehouse in warehouses:
            available_quantity = warehouse.total_quantity - warehouse.reserved_quantity
            data.append({
                "warehouse_id": warehouse.id,
                "warehouse_name": warehouse.name,
                "quantity": warehouse.total_quantity,
                "reserved_quantity": warehouse.reserved_quantity,
                "available_quantity": available_quantity,
            })

        return Response(data, status=status.HTTP_200_OK)
    



class UpdateStockWarehouseWise(generics.UpdateAPIView):
    permission_classes = (CommonPermissions, )
    model = Stock
    serializer_class = StockUpdateSerializer

    def update(self, request, *args, **kwargs):
        variant_id = kwargs.get('variant_id')
        payload = request.data 

        product_variant = get_object_or_404(ProductVariant, id=variant_id)

        for item in payload:
            warehouse_id = item.get("warehouse")
            quantity = int(item.get("quantity"))

            if quantity is None or quantity <= 0:
                # Skip if quantity is not provided or is <= 0
                continue

            warehouse = get_object_or_404(Warehouse, id=warehouse_id)

            try:
                # Check if the stock already exists
                stock = Stock.objects.get(warehouse=warehouse, product_variant=product_variant)
                stock.quantity = quantity  # Update the stock quantity
                stock.save()
            except Stock.DoesNotExist:
                # Create a new stock only if quantity > 0
                Stock.objects.create(warehouse=warehouse, product_variant=product_variant, quantity=quantity)

        return Response({"detail": "Stock updated successfully."}, status=status.HTTP_200_OK)
    

class StockReservationFilter(filters.FilterSet):
    warehouse = filters.CharFilter(field_name='stock__warehouse', lookup_expr='iexact')
    variant = filters.CharFilter(field_name='stock__product_variant', lookup_expr='exact')
    class Meta:
        model = StockReservation
        fields = [
            'id',
            'stock',
            'purpose',
            'warehouse',
            'variant',
        ]



class StockReservationFilterMixin:
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter
    ] 
    search_fields = [
        'id',
        'stock__product_variant__name',

    ]
    ordering_fields = [
        'quantity',
    ]
    filterset_class = StockReservationFilter

    def get_queryset(self):
        return StockReservation.objects.all()
    
class StockReservationListAPIView(StockReservationFilterMixin, generics.ListCreateAPIView):
    permission_classes = (CommonPermissions, )
    model = StockReservation
    serializer_class = StockReservationSerializer
    queryset = StockReservation.objects.all()
    pagination_class = NxtbnPagination



class MergeStockReservationAPIView(generics.UpdateAPIView):
    permission_classes = (CommonPermissions, )
    model = StockReservation
    """
    API to transfer stock reservation from one warehouse to another.
    """
    queryset = StockReservation.objects.all()
    serializer_class = MergeStockReservationSerializer

    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        serializer = self.get_serializer(reservation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        destination_stock = serializer.validated_data['destination_stock']
        destination_reservation = serializer.validated_data.get('destination_reservation')

        # If a reservation already exists at the destination, merge it
        if destination_reservation:
            destination_reservation.quantity += reservation.quantity
            destination_reservation.save()

            # Adjust the reserved quantities of source and destination stocks
            source_stock = reservation.stock
            source_stock.reserved -= reservation.quantity
            source_stock.save()

            destination_stock.reserved += reservation.quantity
            destination_stock.save()

            # Delete the source reservation
            reservation.delete()
        else:
            # Update source stock reserved quantity
            source_stock = reservation.stock
            source_stock.reserved -= reservation.quantity
            source_stock.save()

            # Update destination stock reserved quantity
            destination_stock.reserved += reservation.quantity
            destination_stock.save()

            # Update reservation to point to destination stock
            reservation.stock = destination_stock
            reservation.save()

        return Response({"detail": "Stock reservation successfully transferred."}, status=status.HTTP_200_OK)


class RetryReservationAPIView(APIView):
    permission_classes = (CommonPermissions, )
    model = StockReservation
    def post(self, request, alias):
        order = get_object_or_404(Order, alias=alias)
        reserve_stock(order)
        return Response({"detail": "Stock reservation retried successfully."}, status=status.HTTP_200_OK)
    


class StockTransferListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = (CommonPermissions, )
    model = StockTransfer
    queryset = StockTransfer.objects.prefetch_related('items').all()
    serializer_class = StockTransferSerializer


class StockTransferRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (CommonPermissions, )
    model = StockTransfer
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer
    lookup_field = 'id'

class StockTransferMarkAsInTransitAPIView(APIView):
    permission_classes = (CommonPermissions, )
    model = StockTransfer
    def put(self, request, pk):
        with transaction.atomic():
            transfer = get_object_or_404(StockTransfer, id=pk)
            transfer.status = StockMovementStatus.IN_TRANSIT
            transfer.save()

            # increase incomming stock for destination warehouse
            for item in transfer.items.all():
                try:
                    stock = Stock.objects.get(warehouse=transfer.to_warehouse, product_variant=item.variant)
                    stock.incoming += item.quantity
                except Stock.DoesNotExist:
                    stock = Stock.objects.create(
                        warehouse=transfer.to_warehouse,
                        product_variant=item.variant,
                        incoming=item.quantity
                    )
                stock.save()

           
            # decrease outgoing stock for source warehouse
            for item in transfer.items.all():
                stock = Stock.objects.get(warehouse=transfer.from_warehouse, product_variant=item.variant)
                stock.quantity -= item.quantity
                stock.save()


        return Response({"detail": "Stock transfer marked as in-transit."}, status=status.HTTP_200_OK)
    


class StockTransferReceivingAPI(generics.UpdateAPIView):
    permission_classes = (GranularPermission, )
    model = StockTransfer
    required_perm = PermissionsEnum.CAN_RECEIVE_TRANSFERRED_STOCK
    serializer_class = StockTransferReceivingSerializer
    lookup_field = 'pk'
    queryset = StockTransfer.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status != StockMovementStatus.IN_TRANSIT:
            return Response(
                {"error": "Only stock transfer with status 'IN_TRANSIT' can be received."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data, context={'instance': instance})
        serializer.is_valid(raise_exception=True)

        items_data = serializer.validated_data['items']


        with transaction.atomic():
            for item_data in items_data:
                item_id = item_data['id']
                received_quantity = item_data['received_quantity']
                rejected_quantity = item_data['rejected_quantity']

                try:
                    order_item = instance.items.get(id=item_id)
                    order_item.received_quantity = received_quantity
                    order_item.rejected_quantity = rejected_quantity
                    order_item.save()
                except StockTransferItem.DoesNotExist:
                    raise ValidationError(f"Item with id {item_id} does not exist in the stock transfer.")
                except Stock.DoesNotExist:
                    raise ValidationError(f"Stock entry not found for item id {item_id}.")

        return Response({"message": "Stock receiving updated successfully."}, status=status.HTTP_200_OK)
    

class StockTransferMarkedAsCompletedAPIView(APIView):
    permission_classes = (GranularPermission, )
    model = StockTransfer
    required_perm = PermissionsEnum.CAN_MARK_STOCK_TRANSFER_AS_COMPLETED
    def put(self, request, pk):
        transfer = get_object_or_404(StockTransfer, id=pk)

        if transfer.status != StockMovementStatus.IN_TRANSIT:
            raise ValidationError("Only stock transfer with status 'IN_TRANSIT' can be marked as completed.")
        
        # validate if all item received and rejected sum is equal to quantity
        for item in transfer.items.all():
            if item.quantity != item.received_quantity + item.rejected_quantity:
                raise ValidationError(f"Received quantity + Rejected quantity should be equal to {item.quantity} for item {item.variant.name}")
        
        
        with transaction.atomic():
            transfer.status = StockMovementStatus.COMPLETED
            transfer.save()

            # Update the stock quantities
            for item in transfer.items.all():
                destination_stock = Stock.objects.get(warehouse=transfer.to_warehouse, product_variant=item.variant)
                destination_stock.quantity += item.received_quantity
                destination_stock.incoming -= item.quantity
                destination_stock.save()

        return Response({"detail": "Stock transfer marked as completed."}, status=status.HTTP_200_OK)