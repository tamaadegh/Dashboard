import graphene
from nxtbn.order.proccesor.storefront_type import OrderEstimateInput
import graphene
from graphene.types.generic import GenericScalar
from graphql import GraphQLError
from nxtbn.discount.models import PromoCode
from nxtbn.order.proccesor.views import OrderCalculation
from nxtbn.product.models import Product
from nxtbn.core.signal_initiators import order_created
from nxtbn.users import UserRole

class OrderProcessMutation(graphene.Mutation):
    class Arguments:
        input = OrderEstimateInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    order_id = graphene.String()
    order_alias = graphene.String()
    response = GenericScalar()  # To return additional data like estimated costs

    def mutate(self, info, input):
        request = info.context
        user = request.user

        # Validate staff-specific fields
        if input.get('custom_shipping_amount') and not user.is_staff:
            raise GraphQLError("Only staff can set custom shipping amount.")
        if input.get('custom_discount_amount') and not user.is_staff:
            raise GraphQLError("Only staff can set custom discount amount.")
        
        if input.get('customer_id') and not user.is_staff:
            raise GraphQLError("Only staff can set customer for the order.")
        
        # Perform Order Estimation/Creation
        try:
            order_calculation = OrderCalculation(
                input,
                order_source="store", 
                create_order=input.get('create_order', False),    # Change to True for order creation
                collect_user_agent=False,
                request=request
            )
            response = order_calculation.get_response()

            # If `create_order` is True, create the order
            if input.get('create_order', False):
                order = order_calculation.create_order_instance()
                response['order_id'] = str(order.id)
                response['order_alias'] = order.alias

                # Broadcast order created event
                order_created.send(sender=self.__class__, order=order, request=request)

            return OrderProcessMutation(
                success=True,
                message="Order processed successfully.",
                order_id=response.get('order_id'),
                order_alias=response.get('order_alias'),
                response=response
            )
        except Exception as e:
            raise GraphQLError(str(e))
        except ValueError as e:
            raise GraphQLError(str(e))
