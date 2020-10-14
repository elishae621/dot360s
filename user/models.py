from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.shortcuts import reverse


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

        return self._create_user(email, firstname, lastname, password, **other_fields)

    def create_superuser(self, email, firstname, lastname, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

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
