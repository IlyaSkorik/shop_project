from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        if not instance.groups.exists() and not instance.is_superuser:
            group, _ = Group.objects.get_or_create(name='Покупатель')
            instance.groups.add(group)
