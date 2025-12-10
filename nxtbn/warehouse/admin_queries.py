

import graphene

from nxtbn.core.admin_permissions import gql_store_admin_required
from nxtbn.warehouse.admin_types import StockReservationType, StockTransferItemType, StockTransferType, StockType, WarehouseType
from nxtbn.warehouse.models import Stock, StockReservation, StockTransfer, StockTransferItem, Warehouse
from graphene_django.filter import DjangoFilterConnectionField



class WarehouseQuery(graphene.ObjectType):
    warehouses = DjangoFilterConnectionField(WarehouseType)
    stocks = DjangoFilterConnectionField(StockType)
    stock_reservations = DjangoFilterConnectionField(StockReservationType)
    stock_transfers = DjangoFilterConnectionField(StockTransferType)
    stock_transfer_items = DjangoFilterConnectionField(StockTransferItemType)
    
    warehouse = graphene.Field(WarehouseType, id=graphene.ID(required=True))
    stock = graphene.Field(StockType, id=graphene.ID(required=True))
    stock_reservation = graphene.Field(StockReservationType, id=graphene.ID(required=True))
    stock_transfer = graphene.Field(StockTransferType, id=graphene.ID(required=True))
    stock_transfer_item = graphene.Field(StockTransferItemType, id=graphene.ID(required=True))

    @gql_store_admin_required
    def resolve_warehouses(root, info, **kwargs):
        return Warehouse.objects.all()

    @gql_store_admin_required
    def resolve_stocks(root, info, **kwargs):
        return Stock.objects.all()

    @gql_store_admin_required
    def resolve_stock_reservations(root, info, **kwargs):
        return StockReservation.objects.all()

    @gql_store_admin_required
    def resolve_stock_transfers(root, info, **kwargs):
        return StockTransfer.objects.all()

    @gql_store_admin_required
    def resolve_stock_transfer_items(root, info, **kwargs):
        return StockTransferItem.objects.all()

    @gql_store_admin_required
    def resolve_warehouse(root, info, id):
        try:
            return Warehouse.objects.get(pk=id)
        except Warehouse.DoesNotExist:
            return None

    @gql_store_admin_required
    def resolve_stock(root, info, id):
        try:
            return Stock.objects.get(pk=id)
        except Stock.DoesNotExist:
            return None

    @gql_store_admin_required
    def resolve_stock_reservation(root, info, id):
        try:
            return StockReservation.objects.get(pk=id)
        except StockReservation.DoesNotExist:
            return None

    @gql_store_admin_required
    def resolve_stock_transfer(root, info, id):
        try:
            return StockTransfer.objects.get(pk=id)
        except StockTransfer.DoesNotExist:
            return None

    @gql_store_admin_required
    def resolve_stock_transfer_item(root, info, id):
        try:
            return StockTransferItem.objects.get(pk=id)
        except StockTransferItem.DoesNotExist:
            return None
