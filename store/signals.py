from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Store

@receiver(post_save, sender=Store)
def update_user_vendor_status(sender, instance, **kwargs):
    """Keep UserProfile.is_vendor in sync with Store.is_approved"""
    profile = instance.owner.userprofile
    if instance.is_approved and not profile.is_vendor:
        profile.is_vendor = True
        profile.save()
    elif not instance.is_approved and profile.is_vendor:
        profile.is_vendor = False
        profile.save()
