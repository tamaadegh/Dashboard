from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth import get_user_model

from nxtbn.users import UserRole
from nxtbn.users.models import User


@receiver(post_save , sender = User)
def make_superuser_role_as_admin(sender , instance , created , **kwargs):
    if created and instance.is_superuser:
        instance.role = UserRole.ADMIN
        instance.save()