from django.dispatch import receiver, Signal
from django.db.models.signals import post_save
from user.models import User, Driver, Vehicle, Request, Ride, Order


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
    

@receiver(post_save, sender=Request)
def create_order(sender, instance, created, **kwargs):
    if created:
        order, created = Order.objects.get_or_create(request=instance)
        

order_accepted = Signal(providing_args=["order", "Driver"])

@receiver(order_accepted)
def sent_driver_on_accepted_driver(sender, **kwargs):
    order = kwargs.get('Order', '')
    driver = kwargs.get('Driver', '')
    if order.accepted == True:
        order.request.driver = driver
        # a driver has been selected, waiting for payment
        order.request.ride.status = Ride.Ride_status.unpaid
        order.save()
        order.request.save()
        order.request.ride.save()
