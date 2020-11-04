from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.shortcuts import reverse
from django.utils import timezone
from django.urls import reverse_lazy
from multiselectfield import MultiSelectField
from django.template.defaultfilters import slugify
from math import floor
from time import time


class CustomAccountManager(BaseUserManager):

    def _create_user(self, email, firstname, lastname, phone, password, **other_fields):
        """create and saves the user with the given info"""

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, firstname=firstname, lastname=lastname,
                          phone=phone, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, firstname, lastname, phone, password=None, **other_fields):
        other_fields.setdefault('is_superuser', False)
        other_fields.setdefault('is_staff', False)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_driver', False)

        return self._create_user(email, firstname, lastname, phone, password, **other_fields)

    def create_superuser(self, email, firstname, lastname, phone, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_driver', False)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self._create_user(email, firstname, lastname, phone, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email Address'), unique=True)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_driver = models.BooleanField(default=False)
    phone = models.CharField(max_length=14, null=True, blank=False, unique=True,
        validators=[RegexValidator(regex="(?:^[+]{1}[0-9]*$)|(?:^0{1}[0-9]{10}$)",
        message="Enter a valid phone number without spaces or hyphens")])
    account_balance = models.FloatField(default=0) # in kobo

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'phone']

    def __str__(self):
        return f"{self.firstname}"

    def get_absolute_url(self):
        return reverse_lazy('home')

    def get_full_name(self):
        return f"{self.firstname} {self.lastname}"

class Driver(models.Model):

    class City(models.TextChoices):
        Aba = "aba"
        Umuahia = "umuahia"
        Port_Harcourt = "port harcourt"
        Owerri = "owerri"

    class Journey_type(models.TextChoices):
        within_the_city = 'IN'
        outside_your_current_city = 'OUT'
    
    class Driver_status(models.TextChoices):
        Not_Avaliable = 'NA'
        Busy = 'BU'
        Avaliable = 'AV'

    user = models.OneToOneField(User, on_delete=models.CASCADE,
        limit_choices_to={'is_driver': True})
    image = models.ImageField(_('Profile Picture'), default="default.jpg", upload_to="profile_pics/")
    location = models.CharField(_('Present City'),
        max_length=20, choices=City.choices, null=True, blank=True)
    status = models.CharField(_('Status'),
        choices=Driver_status.choices, default=Driver_status.Not_Avaliable,
        max_length=2)
    journey_type = MultiSelectField(_('Journey'),
        choices=Journey_type.choices, default=Journey_type.within_the_city, null=True, blank=True)

    def __str__(self):
        return f"Driver => {self.user.firstname}"

    def get_absolute_url(self):
        return reverse_lazy('driver_profile_detail', kwargs={'pk':self.user.driver.pk})


class Vehicle(models.Model):

    class Vehicle_type(models.TextChoices):
        Tricycle = 'T'
        Bus = 'B'
        Car = 'C'

    owner = models.OneToOneField(Driver, on_delete=models.CASCADE, related_name='vehicle')
    name = models.CharField(max_length=20, null=True, blank=True)
    plate_number = models.CharField(max_length=15, null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    capacity = models.PositiveSmallIntegerField(null=True, blank=True)
    vehicle_type = models.CharField(choices=Vehicle_type.choices, null=True, blank=True,
    max_length=1)

    def __str__(self):
        return f"{self.owner}'s vehicle"

    def get_absolute_url(self):
        return reverse("driver_profile_detail", kwargs={'pk': self.owner.pk})
    

class Request(models.Model):
    driver = models.ForeignKey(Driver, related_name='driver',
        on_delete=models.SET_NULL, null=True )
    passenger = models.ForeignKey(User, related_name='passenger',
        on_delete=models.SET_NULL, null=True)
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


class Order(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name='request_order')
    driver = models.ManyToManyField(Driver, related_name='request_driver')
    time_posted = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return f"{self.request.passenger.firstname}'s order"

    def get_absolute_url(self):
        return reverse("take_order", kwargs={"slug": self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(slugify(floor(time()*10))) + "-" + str(slugify(self.request.from_address))
        return super().save(*args, **kwargs)
