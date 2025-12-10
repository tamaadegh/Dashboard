import graphene
from graphene_django.types import DjangoObjectType
from nxtbn.users.models import User


class AdminUserType(DjangoObjectType):
    full_name = graphene.String()
    db_id = graphene.ID(source='id')
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'role',
            'email',
            'phone_number',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'is_superuser',
            'is_store_admin',
            'is_store_staff',
            'date_joined',
        )
        interfaces = (graphene.relay.Node, )
        filter_fields = {
            'id': ['exact'],
            'is_staff': ['exact'],
            'is_active': ['exact'],
            'is_superuser': ['exact'],
            'is_store_admin': ['exact'],
            'is_store_staff': ['exact'],
        }


    def resolve_full_name(self, info):
        if not self.first_name and not self.last_name:
            return self.username
        return f"{self.first_name} {self.last_name}"




class PermissionType(graphene.ObjectType):
    codename = graphene.String()
    name = graphene.String()
    has_assigned = graphene.Boolean()