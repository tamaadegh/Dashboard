from rest_framework import serializers
from nxtbn.warehouse import StockMovementStatus
from nxtbn.warehouse.models import StockReservation, StockTransfer, StockTransferItem, Warehouse, Stock
from nxtbn.product.models import ProductVariant
from nxtbn.product.api.dashboard.serializers import ProductVariantSerializer


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all()) 
    product_variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all())

    warehouse_name = serializers.SerializerMethodField()
    product_variant_name = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            'id',
            'warehouse',
            'product_variant',
            'quantity',
            'warehouse_name',
            'product_variant_name',
            'reserved',
            'available_for_new_order',
        ]

    def get_warehouse_name(self, obj):
        return obj.warehouse.name
    
    def get_product_variant_name(self, obj):
        return obj.product_variant.get_descriptive_name_minimal()



class StockDetailViewSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer(read_only=True)
    product_variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = Stock
        fields = ['id', 'warehouse', 'product_variant', 'quantity', 'reserved', 'available_for_new_order',]


class StockUpdateSerializer(serializers.Serializer):
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all(), required=True)
    quantity = serializers.IntegerField(required=True)


class StockReservationSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    order = serializers.SerializerMethodField()

    class Meta:
        model = StockReservation
        fields = [
            'id',
            'stock',
            'quantity',
            'purpose',
            'order',
        ]

    def get_order(self, obj):
        order_line = obj.order_line
        if order_line:
            return {
                "order_id": order_line.order.id,
                "order_alias": order_line.order.alias,
                "order_line_id": order_line.id,
            }
        return None



class MergeStockReservationSerializer(serializers.ModelSerializer):
    destination = serializers.IntegerField(
        write_only=True, help_text="ID of the destination warehouse"
    )

    class Meta:
        model = StockReservation
        fields = ['id', 'stock', 'quantity', 'purpose', 'order_line', 'destination']
        read_only_fields = ['id', 'stock', 'quantity', 'purpose', 'order_line']

    def validate(self, data):
        """
        Perform validation of the destination warehouse, source stock,
        and ensure the reservation can be transferred.
        """
        reservation = self.instance
        destination_id = data.get('destination')

        # Validate if destionation warehouse and source warehosue are the same
        if reservation.stock.warehouse.id == destination_id:
            raise serializers.ValidationError({
                "destination": "Destination warehouse cannot be the same as the source warehouse."
            })

        # Validate destination warehouse
        try:
            destination_warehouse = Warehouse.objects.get(id=destination_id)
        except Warehouse.DoesNotExist:
            raise serializers.ValidationError({"destination": "Destination warehouse does not exist."})

        # Validate destination stock
        try:
            destination_stock = Stock.objects.get(
                warehouse=destination_warehouse,
                product_variant=reservation.stock.product_variant,
            )
        except Stock.DoesNotExist:
            raise serializers.ValidationError({
                "destination": "Destination stock does not exist."
            })

        # Check if destination has sufficient stock
        if destination_stock.quantity < reservation.quantity:
            raise serializers.ValidationError({
                "detail": (
                    "The destination warehouse does not have enough stock to accommodate the reservation. "
                    "Please transfer or add stock to the destination warehouse first."
                )
            })
        
        # check if destionation stock has enough space for the reservation
        expected_new_reserved = destination_stock.reserved + reservation.quantity
        if expected_new_reserved > destination_stock.quantity:
            raise serializers.ValidationError({
                "detail": (
                    "The destination warehouse does not have enough space to accommodate the reservation. "
                    "Please transfer or add stock to the destination warehouse first."
                )
            })

        # Check if there's an existing reservation for the same order line
        destination_reservation = StockReservation.objects.filter(
            stock=destination_stock, order_line=reservation.order_line
        ).first()

        data['destination_stock'] = destination_stock
        data['destination_reservation'] = destination_reservation

        return data
    



class StockTransferItemSerializer(serializers.ModelSerializer):
    """Serializer for StockTransferItem"""
    class Meta:
        model = StockTransferItem
        fields = ['variant', 'quantity']

class StockTransferSerializer(serializers.ModelSerializer):
    """Serializer for StockTransfer"""
    items = StockTransferItemSerializer(many=True)

    class Meta:
        model = StockTransfer
        fields = ['id', 'from_warehouse', 'to_warehouse', 'status', 'created_by', 'items']
        read_only_fields = ['id', 'status', 'created_by']

    
    def validate(self, attrs):

        # It cant be edited if it is not in pending state
        if self.instance and self.instance.status != StockMovementStatus.PENDING:
            raise serializers.ValidationError({"details": "Only pending stock transfers can be edited."})

        # check if available stock in the source warehouse
        from_warehouse = attrs.get('from_warehouse')
        items = attrs.get('items')

        for item in items:
            variant = item.get('variant')
            quantity = item.get('quantity')

            try:
                stock = Stock.objects.get(warehouse=from_warehouse, product_variant=variant)
            except Stock.DoesNotExist:
                raise serializers.ValidationError({"items": f"Stock for variant {variant.id} does not exist in the source warehouse."})

            if stock.quantity < quantity:
                raise serializers.ValidationError({"items": f"Insufficient stock for variant {variant.id} in the source warehouse."})

        return super().validate(attrs)

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        if not items_data:
            raise serializers.ValidationError({"items": "This field is required."})

        stock_transfer = StockTransfer.objects.create(**validated_data, **{'created_by': self.context['request'].user})
        
        # Create StockTransferItem instances
        for item_data in items_data:
            StockTransferItem.objects.create(stock_transfer=stock_transfer, **item_data)
        
        return stock_transfer
    
    def update(self, instance, validated_data):
        # Extract the new items data
        items_data = validated_data.pop('items', [])

        if items_data is None:
            raise serializers.ValidationError({"items": "This field is required."})

        # Update the StockTransfer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        # Get existing items to compare
        existing_items = {item.variant.id: item for item in instance.items.all()}

        # Add or update the StockTransferItems
        for item_data in items_data:
            variant_id = item_data['variant']
            quantity = item_data['quantity']
            if variant_id in existing_items:
                # Update existing item
                item = existing_items.pop(variant_id)
                item.quantity = quantity
                item.save()
            else:
                # Create new item
                StockTransferItem.objects.create(stock_transfer=instance, **item_data)

        # Delete removed items
        for item in existing_items.values():
            item.delete()

        return instance



class StockTransferItemUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    received_quantity = serializers.IntegerField()
    rejected_quantity = serializers.IntegerField()


class StockTransferReceivingSerializer(serializers.Serializer):
    items = StockTransferItemUpdateSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError({"items": "This field is required."})

        for item in items:
            transfer_item = StockTransferItem.objects.get(id=item.get('id'))
            received_quantity = item.get('received_quantity', 0)
            rejected_quantity = item.get('rejected_quantity', 0)
            if received_quantity + rejected_quantity > transfer_item.quantity:
                raise serializers.ValidationError({
                    "items": "The sum of received and rejected quantities cannot exceed the original quantity."
                })

        return items