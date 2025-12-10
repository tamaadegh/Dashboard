from celery import shared_task

from nxtbn.order.models import Order
from nxtbn.warehouse.utils import reserve_stock

@shared_task
def handle_stock_reserve(order_id):
    order = Order.objects.get(id=order_id)
    reserve_stock(order)