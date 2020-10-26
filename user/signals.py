from django.dispatch import receiver
from django.db.models.signals import post_save
from user.models import User, Driver, Vehicle, Request, Ride


@receiver(post_save, sender=User)
def create_driver(sender, instance, created, **kwargs):
    if created:
        if instance.is_driver == True:
            driver = Driver.objects.create(user=instance)
            Vehicle.objects.create(owner=driver)


@receiver(post_save, sender=Request)
def create_ride(sender, instance, created, **kwargs):
    if created:
        ride, created = Ride.objects.get_or_create(request=instance)
        # price manipulation can be done here
    else:
        old_ride = Ride.objects.filter(request=instance).first()
        if old_ride:
            old_ride.delete()
        ride, created = Ride.objects.get_or_create(request=instance)
        