"""
Dashboard User Permission Hierarchy:

- `is_superuser`:  
    Grants unrestricted access to all dashboard functionalities without any limitations.  
    Inherits all permissions of `is_store_admin` by default.  

- `is_staff`:  
    Required for all users to access the dashboard.  

- `is_store_admin`:  
    Has extensive permissions and authority within the dashboard.  
    Can perform almost all operations except a few critical ones restricted to the superuser.  
    Inherits all permissions assigned to other users by default.  

- `is_store_staff`:  
    Has limited access to the dashboard.  
    Their permissions can be extended granularly by assigning specific permissions, which are managed by the store admin.  

**Additional Notes:**  
- All users have read permissions by default, except for certain critical data that require explicit authorization.  
- The superuser automatically inherits all permissions of a store admin.  
- A store admin inherits all permissions granted to other users by default.  
"""



from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

from nxtbn.users import UserRole


import functools
from graphql import GraphQLError


class IsStoreAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_staff:
            return False
        
        if request.user.is_superuser:
            return True

        return request.user.is_store_admin
    
class IsStoreStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_staff:
            return False
        
        if request.user.is_superuser:
            return True
        
        if request.user.is_store_admin:
            return True

        return request.user.is_store_staff

class GranularPermission(BasePermission):
    def get_permission_name(self, model_name, action):
       
        return f"{model_name}.{action}"

    def has_permission(self, request, view):
        if not request.user.is_staff:
            return False
        
        if request.user.is_superuser:
            return True
        
        if request.user.is_store_admin:
            return True
        
        if request.method in SAFE_METHODS and request.user.is_staff: # Every staff can view
            return True
      
        model_cls = None
        if hasattr(view, 'get_queryset'): # Warning, Never use  hasattr(view, 'queryset') as DRF cache  this which may lead to unexpected behavior
            model_cls = view.get_queryset().model
        elif hasattr(view, 'model'):
            model_cls = view.model

        if model_cls is None:
            return False

        model_name = model_cls.__name__.lower()
        action = view.required_perm

        permission_name = self.get_permission_name(model_name, action)

        # Check if the user has the generated permission
        return request.user.has_perm(permission_name)
    

class CommonPermissions(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_staff:
            return False
        
        if request.user.is_superuser:
            return True
        
        if request.user.is_store_admin:
            return True
        
        if request.method in SAFE_METHODS and request.user.is_staff: # Every staff can view
            return True



        model_cls = None
        if hasattr(view, 'get_queryset'): # Warning, Never use  hasattr(view, 'queryset') as DRF cache  this which may lead to unexpected behavior
            model_cls = view.get_queryset().model
        elif hasattr(view, 'model'):
            model_cls = view.model
            
        if model_cls is None:
            return False

        model_meta = model_cls.model._meta

        method_permissions_map = {
            'GET': f'{model_meta.app_label}.view_{model_meta.model_name}',
            'OPTIONS': f'{model_meta.app_label}.view_{model_meta.model_name}',
            'HEAD': f'{model_meta.app_label}.view_{model_meta.model_name}',
            'POST': f'{model_meta.app_label}.add_{model_meta.model_name}',
            'PUT': f'{model_meta.app_label}.change_{model_meta.model_name}',
            'PATCH': f'{model_meta.app_label}.change_{model_meta.model_name}',
            'DELETE': f'{model_meta.app_label}.delete_{model_meta.model_name}',
        }

        required_permission = method_permissions_map.get(request.method)

        if required_permission is None:
            return False

        return request.user.has_perm(required_permission)


def has_required_perm(user, code: str, model_cls=None):
    if not user.is_staff:
        return False

    if user.is_superuser:
        return True
    
    if user.is_store_admin:
        return True

    perm_code  = model_cls._meta.app_label + '.' + code
    return user.has_perm(perm_code)


def gql_required_perm(model, code: str):  # model argument will be the model class
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, info, *args, **kwargs):
            operation = info.operation.operation
            user = info.context.user

            if user.is_anonymous:
                raise GraphQLError("Authentication required")
            
            if not user.is_staff:
                raise GraphQLError("Permission denied")
            
            if user.is_superuser:
                return func(self, info, *args, **kwargs)
            
            if user.is_store_admin:
                return func(self, info, *args, **kwargs)
            
            if operation == "query":
                return func(self, info, *args, **kwargs)
            
            # Check if the user has permission for the model
            perm_code = f"{model._meta.app_label}.{code}"  # Constructing the permission name
            if not user.has_perm(perm_code):  # Check if the user has the required permission for the model
                raise GraphQLError("Permission denied")  # Block unauthorized access

            return func(self, info, *args, **kwargs)  # Call the actual resolver
        
        return wrapper
    
    return decorator



def gql_store_admin_required(func): # Used in graphql only
    @functools.wraps(func)
    def wrapper(self, info, *args, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError("Authentication required")
        
        if not user.is_staff:
            raise GraphQLError("Permission denied")
        
        if user.is_superuser:
            return func(self, info, *args, **kwargs)

        if user.is_store_admin:
            return func(self, info, *args, **kwargs)

        return func(self, info, *args, **kwargs)  # Call the actual resolver

    return wrapper


def gql_store_staff_required(func): # Used in graphql only
    @functools.wraps(func)
    def wrapper(self, info, *args, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError("Authentication required")
        
        if not user.is_staff:
            raise GraphQLError("Permission denied")
        
        if user.is_superuser:
            return func(self, info, *args, **kwargs)
        
        if user.is_store_admin:
            return func(self, info, *args, **kwargs)

        if user.is_store_staff:
            return func(self, info, *args, **kwargs)
        else:
            raise GraphQLError("Permission denied")

    
    return wrapper