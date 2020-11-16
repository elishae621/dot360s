from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.shortcuts import reverse
from django.urls import reverse_lazy
from multiselectfield import MultiSelectField



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
    
    class Referral_status(models.TextChoices):
        unpaid = "unpaid"
        paid = "paid"

    email = models.EmailField(_('Email Address'), unique=True)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_driver = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True)
    phone = models.CharField(max_length=14, null=True, blank=False, unique=True,
        validators=[RegexValidator(regex="(?:^[+]{1}[0-9]*$)|(?:^0{1}[0-9]{10}$)",
        message="Enter a valid phone number without spaces or hyphens")])
    account_balance = models.FloatField(default=0) # in kobo
    referral = models.EmailField(_('Who referred you'), null=True, blank=True)
    referral_status = models.CharField(choices=Referral_status.choices, default="unpaid", max_length=6)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'phone']

    def __str__(self):
        return f"{self.firstname}"

    def get_absolute_url(self):
        return reverse('home')

    def get_full_name(self):
        return f"{self.firstname} {self.lastname}"


class Driver(models.Model):

    class City(models.TextChoices):
        none = "none"
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
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Driver => {self.user.firstname}"

    def get_absolute_url(self):
        return reverse('driver_profile_detail', kwargs={'pk':self.user.driver.pk})


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
    

