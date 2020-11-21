from django.db import models
from django.template.defaultfilters import slugify
from math import floor
from time import time
from django.utils import timezone
from user.models import Driver, User, Vehicle
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.shortcuts import reverse


class Request(models.Model):
    driver = models.ForeignKey(Driver, related_name='driver',
        on_delete=models.CASCADE, null=True)
    passenger = models.ForeignKey(User, related_name='passenger',
        on_delete=models.CASCADE, null=True)
    from_address = models.CharField(_('From'), max_length=70, null=True)
    to_address = models.CharField(_('To'), max_length=70, null=True)
    city = models.CharField(choices=Driver.City.choices,
        max_length=20, null=True, blank=True)
    no_of_passengers = models.IntegerField(default=1)
    intercity = models.BooleanField(default=False)
    load = models.BooleanField(default=False)
    time = models.DateTimeField(default=timezone.now)
    request_vehicle_type = models.CharField(choices=Vehicle.Vehicle_type.choices, null=True, blank=True,
    max_length=1)

    def __str__(self):
        return f'Request: {self.driver}, {self.passenger}'

    def get_absolute_url(self):
        return reverse("order_detail", kwargs={"slug": self.order_of_request.slug})


class Ride(models.Model):

    class Ride_status(models.TextChoices):
        unconfirmed = "unconfirmed"  # a driver has not taking this ride
        waiting = "waiting"  # has a driver, but waiting for the ride to start
        ongoing = "ongoing"  # the ride has started but has not been marked as completed
        completed = "completed"  # the ride has been marked as completed
        cancelled = "cancelled" # the ride is deleted at any stage

    class Payment_method(models.TextChoices):
        cash = "cash"
        card = "card"

    class Payment_status(models.TextChoices):
        unpaid = "unpaid"
        paid = "paid"

    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name='ride')
    status = models.CharField(max_length=11, choices=Ride_status.choices,
        default=Ride_status.unconfirmed)
    price = models.FloatField(default=100.00)
    payment_status = models.CharField(max_length=6, choices=Payment_status.choices, default=Payment_status.unpaid)
    payment_method = models.CharField(max_length=6,  choices=Payment_method.choices, 
        default=Payment_method.card)

    def __str__(self):
        return f'Ride => {self.request}'

    def get_absolute_url(self):
        return reverse("order_detail", kwargs={"slug": self.request.order_of_request.slug})


class Order(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name='order_of_request')
    driver = models.ManyToManyField(Driver, related_name='request_driver')
    time_posted = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return f"{self.request.passenger.firstname}'s order"

    def get_absolute_url(self):
        return reverse("order_detail", kwargs={"slug": self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(slugify(floor(time()*10))) + "-" + str(slugify(self.request.from_address))
        return super().save(*args, **kwargs)


class Withdrawal(models.Model):

    class Status(models.TextChoices):
        unattended = "unattended"
        pending = "pending"
        completed = "completed"
        cancelled = "cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawal", null=True)
    name = models.CharField(max_length=40, null=True, blank=True)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=500)
    account_no = models.IntegerField()
    bank = models.CharField(max_length=50)
    status = models.CharField(choices=Status.choices, default=Status.unattended, max_length=10)

    def __str__(self):
        return f"{self.user.get_full_name()} {self.amount} on {self.date}"

    def get_absolute_url(self):
        return reverse('withdrawal_detail', kwargs={'pk': self.pk})