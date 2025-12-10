import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay

from nxtbn.purchase.models import PurchaseOrder, PurchaseOrderItem




class PurchaseType(DjangoObjectType):
    db_id = graphene.Int(source="id")
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

        interfaces = (relay.Node,)
        filter_fields = {
            'supplier__id': ['exact'],
            'destination__id': ['exact'],
            'status': ['exact'],
            'expected_delivery_date': ['exact', 'lte', 'gte'],
            'created_by__id': ['exact'],
        }


class PurchaseOrderItemType(DjangoObjectType):
    db_id = graphene.Int(source="id")
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'purchase_order__id': ['exact'],
            'variant__id': ['exact'],
            'ordered_quantity': ['exact', 'lte', 'gte'],
            'received_quantity': ['exact', 'lte', 'gte'],
            'rejected_quantity': ['exact', 'lte', 'gte'],
            'unit_cost': ['exact', 'lte', 'gte'],
        }