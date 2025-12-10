

import graphene

from graphene_django.filter import DjangoFilterConnectionField
from nxtbn.core.admin_permissions import gql_store_admin_required
from nxtbn.purchase.admin_types import PurchaseType
from nxtbn.purchase.models import PurchaseOrder



class PurchaseQuery(graphene.ObjectType):
    purchase = graphene.Field(PurchaseType, id=graphene.ID(required=True))
    purchases = DjangoFilterConnectionField(PurchaseType)


 
    @gql_store_admin_required
    def resolve_purchase(root, info, id):

        try:
            return PurchaseOrder.objects.get(pk=id)
        except PurchaseOrder.DoesNotExist:
            return None
        
   
    @gql_store_admin_required
    def resolve_purchases(root, info, **kwargs):
        return PurchaseOrder.objects.all()