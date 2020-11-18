from rest_framework.authtoken.models import Token

from django.dispatch import receiver
from django.db.models.signals import post_save

from user.models import User, Driver, Vehicle


@receiver(post_save, sender=User)
def create_token_driver_vehicle(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
    if instance.is_driver == True:
        driver, created = Driver.objects.get_or_create(user=instance)
        vehicle,created = Vehicle.objects.get_or_create(owner=driver)


