from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.shortcuts import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


class CustomAccountManager(BaseUserManager):

    def _create_user(self, email, firstname, lastname, password, **other_fields):
        """create and saves the user with the given info"""

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, firstname=firstname, lastname=lastname, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, firstname, lastname, password=None, **other_fields):
        other_fields.setdefault('is_superuser', False)
        other_fields.setdefault('is_staff', False)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_driver', False)

        return self._create_user(email, firstname, lastname, password, **other_fields)

    def create_superuser(self, email, firstname, lastname, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_driver', False)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self._create_user(email, firstname, lastname, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email address'), unique=True)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_driver = models.BooleanField(default=False)
    phone = PhoneNumberField(null=True, blank=False, unique=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname']

    def __str__(self):
        return self.firstname

    def get_absolute_url(self):
        return f'/user/{self.pk}/'


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics/")

    def __str__(self):
        return f"{self.user}'s profile"

    def get_absolute_url(self):
        return f'/user/{self.pk}/'


location = [
    ('UMUAHIA', 'Umuahia'),
    ('ABA', 'Aba')
]

journey_choice = [
    ('IN', 'Within the city'),
    ('OUT', 'InterCity travel')
]

vehicle_choice = [
    ('T', 'Tricycle'),
    ('B', 'Bus'), 
    ('C', 'Car'),
]


class Driver(User):
    polar_choices = [
        ('not_avaliable', 'Not Avaliable'),
        ('busy', 'Busy'),
        ('avaliable', 'Avaliable'),
    ]
    username = models.CharField(max_length=10)
    location = models.CharField(max_length=15, choices=location,
        null=True, blank=True)
    about = models.TextField(default="No about yet for this driver")
    status = models.CharField(max_length=13, choices=polar_choices, default='not_avaliable')
    journey_type = models.CharField(max_length=3, choices=journey_choice,
        default='IN')

    def __str__(self):
        return f'Driver: {self.username}'


class Vehicle(models.Model):
    name = models.CharField(max_length=20)
    plate_number = models.CharField(max_length=15)
    capacity = models.IntegerField()
    vehicle_type = models.CharField(max_length=1, choices=vehicle_choice, 
        null=True, blank=True)
    owner = models.ForeignKey(Driver, on_delete=models.CASCADE)


class Passenger(User):
    """same as the base user for now"""

    def __str__(self):
        return f'Passenger: {self.email}'
    


class Request(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.SET_NULL, null=True)
    from_address = models.CharField(max_length=70)
    to_address = models.CharField(max_length=70)
    city = models.CharField(max_length=15, choices=location,
        null=True, blank=True)
    no_of_passengers = models.IntegerField(default=1)
    load = models.BooleanField(default=False)
    time = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f'Request: {self.driver}, {self.passenger}'


ride_status = [
    ('WC', 'Waiting for confirmation'),
    ('WD', 'Waiting for driver'),
    ('ON', 'Ongoing'),
    ('CO', 'Completed'),
]

class Ride(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=ride_status, 
        null=True, blank=True)
    price = models.FloatField(default=100.00)

    def __str__(self):
        return f'Ride => {self.request}'
    