from django.test import TestCase, RequestFactory
from user.forms import (
    UserRegistrationForm,
    DriverProfileUpdateForm,
    VehicleUpdateForm)
from faker import Faker
import factory
from django.urls import reverse
from user.models import User, Driver
from django.http import HttpRequest
from django.conf import settings
from importlib import import_module
import pytest
from user.providers import CustomPhoneProvider
from faker import Faker
from phonenumber_field.phonenumber import PhoneNumber

fake = Faker()
fake.add_provider(CustomPhoneProvider)


class TestUserRegistrationForm(TestCase):

    def setUp(self):
        self.data = {
            'email': fake.email(),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'password1': 'secretdeadlypassword',
            'password2': 'secretdeadlypassword',
            'phone':PhoneNumber.from_string(phone_number=fake.phone_number(), region='NG').as_e164,
        }
        self.form = UserRegistrationForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())

class TestDriverProfileUpdateForm(TestCase):
    def setUp(self):
        self.data = {
            'image': factory.django.ImageField(from_path=r"C:\Users\Elisha\Pictures\Screenshots\Screenshot (16).png", filename=r"\newimage", format="png"),
            'location': ['Umuahia',],
            'status': ['Not Avaliable',],
            'journey_type': [1,]
        }
        self.form = DriverProfileUpdateForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())


class TestDriverUpdateForm(TestCase):

    def setUp(self):
        self.data = {
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'location': fake.address(),
            'status': fake.random_element(elements=
                ('Not Avaliable', 'Busy', 'Avaliable')),
            'journey_type': ['Within the city']
            # 'journey_type': fake.random_elements(elements=
                # ('IN', 'OUT'), unique=True)
        }
        self.form = DriverUpdateForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())


class TestVehicleUpdateForm(TestCase):

    def setUp(self):
        self.data = {
            'name': fake.text(max_nb_chars=20),
            'plate_number': fake.bothify("???-###-???"),
            'capacity': fake.random_int(min=1, max=18),
            'color': fake.color_name(),
            'vehicle_type': fake.random_element(elements=('Tricycle', 'Bus', 'Car'))
        }
        self.form = DriverUpdateForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())
