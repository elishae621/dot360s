from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.shortcuts import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.urls import reverse_lazy


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
    phone = PhoneNumberField(
        _('Phone Number'), null=True, blank=False, unique=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'phone']

    def __str__(self):
        return f"Passenger => {self.firstname}"

    def get_absolute_url(self):
        return reverse_lazy('home')


class Driver(models.Model):
    CITIES = (
        (1, 'Umuahia'),
        (2, 'Aba')
    )

    JOURNEY_CHOICES = (
        (1, 'Within the city'),
        (2, 'InterCity travel')
    )

    STATUS_CHOICES = (
        (1, 'Not Avaliable'),
        (2, 'Busy'),
        (3, 'Avaliable'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE,
        limit_choices_to={'user_type': '1'})
    image = models.ImageField(default="default.jpg", upload_to="profile_pics/")
    location = models.PositiveIntegerField(
        choices=CITIES, null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=1)
    journey_type = models.PositiveSmallIntegerField(
        choices=JOURNEY_CHOICES, default=1)

    def __str__(self):
        return f"Driver => {self.user.firstname}"

    def get_absolute_url(self):
        return reverse_lazy('driver_profile_detail')


class Vehicle(models.Model):
    VEHICLE_CHOICE = (
        (1, 'Tricycle'),
        (2, 'Bus'),
        (3, 'Car'),
    )

    owner = models.ForeignKey(Driver, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, null=True)
    plate_number = models.CharField(max_length=15, null=True)
    color = models.CharField(max_length=15, null=True)
    capacity = models.IntegerField(null=True)
    vehicle_type = models.PositiveSmallIntegerField(choices=VEHICLE_CHOICE, null=True)


class Request(models.Model):
    driver = models.ForeignKey(Driver, related_name='driver',
        on_delete=models.SET_NULL, null=True )
    passenger = models.ForeignKey(User, related_name='passenger',
        on_delete=models.SET_NULL, null=True)
    from_address = models.CharField(max_length=70, null=True)
    to_address = models.CharField(max_length=70, null=True)
    city = models.CharField(max_length=15, choices=Driver.CITIES,
        null=True, blank=True)
    no_of_passengers = models.IntegerField(default=1)
    load = models.BooleanField(default=False)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Request: {self.driver}, {self.passenger}'


class Ride(models.Model):
    RIDE_STATUS = (
        (1, 'Waiting for confirmation'),
        (2, 'Waiting for driver'),
        (3, 'Ongoing'),
        (4, 'Completed'),
    )

    request = models.OneToOneField(Request, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=RIDE_STATUS,
                                              null=True, blank=True)
    price = models.FloatField(default=100.00)

    def __str__(self):
        return f'Ride => {self.request}'
