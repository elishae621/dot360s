from django.dispatch import receiver
from django.db.models.signals import post_save
from user.models import User, Driver, Vehicle


# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         if instance.user_type is 1:
#             Driver.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.driver_profile.save()


@receiver(post_save, sender=Driver)
def create_vehicle(sender, instance, created, **kwargs):
    if created:
        Vehicle.objects.create(owner=instance)


@receiver(post_save, sender=Driver)
def save_vehicle(sender, instance, **kwargs):
    instance.vehicle.save()
