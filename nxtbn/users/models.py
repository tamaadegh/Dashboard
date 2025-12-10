from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from nxtbn.core.enum_perms import PermissionsEnum
from nxtbn.order import OrderStatus
from nxtbn.users import UserRole

from babel.numbers import get_currency_precision, format_currency


class User(AbstractUser):
    role = models.CharField(max_length=255, default='Store Admin')

    # To learn more about permissions hierarchy, check this files: nxtbn/core/admin_permissions.py
    is_store_admin = models.BooleanField(default=False)
    is_store_staff = models.BooleanField(default=False)


    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        permissions = [
            (PermissionsEnum.CAN_READ_CUSTOMER, 'Can read customer'),
            (PermissionsEnum.CAN_UPDATE_CUSTOMER, 'Can update customer'),
        ]

    def __str__(self):
        parts = [self.get_full_name(), self.username, self.email]
        return " - ".join(part for part in parts if part)

    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def total_spent(self):
        precision = get_currency_precision(settings.BASE_CURRENCY)
        total_spent_in_subunit =  self.payments.aggregate(models.Sum('payment_amount'))['payment_amount__sum'] or 0
        total_spent_in_unit = total_spent_in_subunit / (10 ** precision)
        total_spent = format_currency(total_spent_in_unit, settings.BASE_CURRENCY, locale='en_US')
        return total_spent

    
    def total_order_count(self):
        return self.orders.count()
    
    def total_cancelled_order_count(self):
        return self.orders.filter(status=OrderStatus.CANCELLED).count()
    
    def total_pending_order_count(self):
        return self.orders.filter(status=OrderStatus.PENDING).count()
    
    def total_refunded_order_count(self):
        return self.orders.filter(status=OrderStatus.REFUNDED).count()
    