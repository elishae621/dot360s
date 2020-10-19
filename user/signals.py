from django.dispatch import receiver
from django.db.models.signals import post_save
from user.models import User, Driver, Vehicle


@receiver(post_save, sender=User)
def create_driver(sender, instance, created, **kwargs):
    if created:
        if instance.is_driver == True:
            driver = Driver.objects.create(user=instance)
            Vehicle.objects.create(owner=driver)
