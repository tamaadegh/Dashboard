from rest_framework import serializers
from nxtbn.purchase import PurchaseStatus
from nxtbn.purchase.models import PurchaseOrder, PurchaseOrderItem
from nxtbn.product.api.dashboard.serializers import SupplierSerializer, ProductVariantSerializer
from nxtbn.users.api.dashboard.serializers import UserSerializer
from nxtbn.warehouse.api.dashboard.serializers import WarehouseSerializer
from nxtbn.product.models import Supplier
from nxtbn.warehouse.models import Warehouse
from django.db import transaction
import datetime
import re

class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.SerializerMethodField()
    destination_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'supplier',
            'supplier_name',
            'destination',
            'destination_name',
            'status',
            'expected_delivery_date',
            'created_by',
            'created_by_name',
            'total_cost'
        ]
    def get_supplier_name(self, obj):
        return obj.supplier.name
    
    def get_destination_name(self, obj):
        return obj.destination.name
    
    def get_created_by_name(self, obj):
        if not obj.created_by:
            return "N/A"
        
        if not obj.created_by.first_name and not obj.created_by.last_name:
            return obj.created_by.username

        return f"{obj.created_by.first_name} {obj.created_by.last_name}"



class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = ['variant', 'ordered_quantity', 'unit_cost']

class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'supplier', 'destination', 'expected_delivery_date', 'items']

    def create(self, validated_data):
        request = self.context.get('request')
              
        items_data = validated_data.pop('items', [])

        if not items_data:
            raise serializers.ValidationError("Items are required")

       
        purchase_order = PurchaseOrder.objects.create(
            created_by=request.user,
            status=PurchaseStatus.DRAFT,
            **validated_data
        )

        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)

        return purchase_order
    
    def validate(self, attrs):
        expected_delivery_date = attrs.get('expected_delivery_date')
        expected_delivery_datetime = datetime.datetime.combine(expected_delivery_date, datetime.time())
        if expected_delivery_datetime <= datetime.datetime.now():
            raise serializers.ValidationError('Invalid Expected delivery date, it is equal or less than current date.')
        
        items = attrs.get('items')
        if len(items) <= 0:
            raise serializers.ValidationError('Items are required')
        
      
        return super().validate(attrs)
    

class PurchaseOrderUpdateSerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), write_only=True)
    destination = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all(), write_only=True)
    items = PurchaseOrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'supplier', 'destination', 'expected_delivery_date', 'items']

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])

        with transaction.atomic():
            # Update the purchase order fields
            instance.supplier = validated_data.get('supplier', instance.supplier)
            instance.destination = validated_data.get('destination', instance.destination)
            instance.expected_delivery_date = validated_data.get('expected_delivery_date', instance.expected_delivery_date)

            # List to keep track of new items to avoid deletion
            new_item_ids = []

            # Process each item in the provided items data
            for item_data in items_data:
                variant = item_data.get('variant')
                item_id = item_data.get('id', None)

                # If the item has an ID, it's an existing item to update
                if item_id:
                    try:
                        item = instance.items.get(id=item_id)
                        item.ordered_quantity = item_data.get('ordered_quantity', item.ordered_quantity)
                        item.unit_cost = item_data.get('unit_cost', item.unit_cost)
                        item.save()
                        new_item_ids.append(item.id)
                    except PurchaseOrderItem.DoesNotExist:
                        pass  
                else:
                    # Check if the variant already exists in the purchase order
                    existing_item = instance.items.filter(variant=variant).first()
                    if existing_item:
                        existing_item.ordered_quantity = item_data['ordered_quantity']
                        existing_item.unit_cost = item_data['unit_cost']
                        existing_item.save()
                        new_item_ids.append(existing_item.id)
                    else:
                        # If there's no ID and no existing item, create a new item
                        new_item = PurchaseOrderItem.objects.create(
                            purchase_order=instance,
                            variant=variant,
                            ordered_quantity=item_data['ordered_quantity'],
                            unit_cost=item_data['unit_cost'],
                        )
                        new_item_ids.append(new_item.id)

            # Remove items that are no longer part of the request
            for item in instance.items.all():
                if item.id not in new_item_ids:
                    item.delete()

        # Return the updated purchase order instance
        instance.save()
        return instance
    

class PurchaseOrderItemDetailSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'variant', 'ordered_quantity', 'received_quantity', 'rejected_quantity', 'unit_cost']


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    destination = WarehouseSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    items = PurchaseOrderItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'supplier',
            'destination',
            'status',
            'expected_delivery_date',
            'created_by',
            'total_cost',
            'items'
        ]


class PurchaseOrderItemUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    received_quantity = serializers.IntegerField()
    rejected_quantity = serializers.IntegerField()

    def validate(self, data):
        item_id = data['id']
        received_quantity = data['received_quantity']
        rejected_quantity = data['rejected_quantity']

    
        instance = self.context.get('instance')

        try:
            order_item = instance.items.get(id=item_id)
        except PurchaseOrderItem.DoesNotExist:
            raise serializers.ValidationError(
                f"Item with id {item_id} does not exist in the purchase order."
            )

        if received_quantity > order_item.ordered_quantity:
            raise serializers.ValidationError(
                f"Received quantity ({received_quantity}) cannot exceed ordered quantity ({order_item.ordered_quantity})."
            )

        if received_quantity < order_item.received_quantity:
            raise serializers.ValidationError(
                f"Received quantity ({received_quantity}) cannot be less than the current received quantity ({order_item.received_quantity})."
            )
        
        if rejected_quantity < order_item.rejected_quantity:
            raise serializers.ValidationError(
                f"Rejected quantity ({rejected_quantity}) cannot be less than the current rejected quantity ({order_item.rejected_quantity})."
            )

        adjusted_quantity = order_item.ordered_quantity - received_quantity
        if rejected_quantity > adjusted_quantity:
            raise serializers.ValidationError(
                f"Rejected quantity ({rejected_quantity}) cannot exceed the adjusted quantity ({adjusted_quantity})."
            )
        

        return data



class InventoryReceivingSerializer(serializers.Serializer):
    items = PurchaseOrderItemUpdateSerializer(many=True)
