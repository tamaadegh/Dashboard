from nxtbn.users.utils.jwt_utils import JWTManager
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model


from graphql import GraphQLError
from graphql.language.ast import FieldNode, FragmentSpreadNode, InlineFragmentNode


class MaxQueryDepthMiddleware:
    def __init__(self, max_depth=6, max_top_level_fields=2):
        self.max_depth = max_depth
        self.max_top_level_fields = max_top_level_fields

    def resolve(self, next, root, info, **kwargs):
        operation = info.operation

        # Bypass validation for introspection queries
        if self._is_introspection_query(operation):
            return next(root, info, **kwargs)

        # Validate max depth
        query_depth = self._calculate_depth(operation.selection_set, info)
        if query_depth > self.max_depth:
            raise GraphQLError(f"Query depth exceeds the maximum limit of {self.max_depth}. Current depth: {query_depth}.")

        # Validate max top-level fields
        top_level_fields_count = len(operation.selection_set.selections)
        if top_level_fields_count > self.max_top_level_fields:
            raise GraphQLError(f"Query exceeds the maximum of {self.max_top_level_fields} top-level fields. Current count: {top_level_fields_count}.")

        # Continue to the next middleware or resolver
        return next(root, info, **kwargs)

    def _is_introspection_query(self, operation):
        # Check if the operation contains any introspection fields
        if operation.selection_set:
            for selection in operation.selection_set.selections:
                if isinstance(selection, FieldNode) and selection.name.value.startswith("__"):
                    return True
        return False

    def _calculate_depth(self, selection_set, info, depth=0):
        if not selection_set or not hasattr(selection_set, "selections"):
            return depth

        depths = []
        for selection in selection_set.selections:
            if isinstance(selection, (FieldNode, InlineFragmentNode)):
                depths.append(self._calculate_depth(selection.selection_set, info, depth + 1))
            elif isinstance(selection, FragmentSpreadNode):
                fragment = info.fragments.get(selection.name.value)
                if fragment:
                    depths.append(self._calculate_depth(fragment.selection_set, info, depth + 1))
        return max(depths, default=depth)



class NXTBNGraphQLAuthenticationMiddleware:
    def __init__(self):
        self.jwt_manager = JWTManager()

    def resolve(self, next, root, info, **args):
        request = info.context

        # First check JWT token
        user = self.get_user_from_jwt(request)
        
        # If no JWT token, fall back to session-based authentication
        if not user.is_authenticated:
            user = self.get_user_from_session(request)

        # If no valid user from either method, set as AnonymousUser
        if not user.is_authenticated:
            user = AnonymousUser()

        info.context.user = user

        # Continue processing the query
        return next(root, info, **args)

    def get_user_from_jwt(self, request):
        token = self.get_token_from_request(request)
        if token:
            return self.jwt_manager.verify_jwt_token(token) or AnonymousUser()
        return AnonymousUser()

    def get_user_from_session(self, request):
        return request.user if request.user.is_authenticated else AnonymousUser()

    def get_token_from_request(self, request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]

        return request.COOKIES.get("access_token")
