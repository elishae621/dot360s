from django.test import TestCase, RequestFactory
from user.forms import (
    UserRegistrationForm,
    DriverProfileUpdateForm,
    VehicleUpdateForm)
from faker import Faker
import factory
from django.urls import reverse
from user.models import User, Driver, Vehicle
from django.http import HttpRequest
from django.conf import settings
from importlib import import_module
import pytest
from faker import Faker
from phonenumber_field.phonenumber import PhoneNumber

fake = Faker()
password = fake.password()

class TestUserRegistrationForm(TestCase):

    def setUp(self):
        self.data = {
            'email': fake.email(),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'password': password,
            'password2': password,
            'phone': fake.numerify(text='080########'),
        }
        self.form = UserRegistrationForm(data=self.data)

    def test_form_is_valid(self):
        print(self.form.errors)
        self.assertTrue(self.form.is_valid())

    

class TestDriverProfileUpdateForm(TestCase):
    def setUp(self):
        self.data = {
            'image': factory.django.ImageField(from_path=r"C:\Users\Elisha\Pictures\Screenshots\Screenshot (16).png", filename=r"\newimage", format="png"),
            'location': fake.random_int(min=1, max=len(Driver.CITIES)),
            'status': fake.random_int(min=1, max=len(Driver.STATUS_CHOICES)),
            'journey_type': [1,2]
        }
        self.form = DriverProfileUpdateForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())


class TestVehicleUpdateForm(TestCase):

    def setUp(self):
        self.data = {
            'name': fake.text(max_nb_chars=20),
            'plate_number': fake.bothify("???-###-???"),
            'capacity': fake.random_int(min=1, max=18),
            'color': fake.color_name(),
            'vehicle_type': fake.random_int(min=1, max=len(Vehicle.VEHICLE_CHOICE))
        }
        self.form = VehicleUpdateForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())
