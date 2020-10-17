from django.test import TestCase, RequestFactory
from user.forms import (
    UserRegistrationForm,
    DriverProfileUpdateForm,
    VehicleUpdateForm)
from faker import Faker
import factory
from django.urls import reverse
from user.models import User
from django.http import HttpRequest
from django.conf import settings
from importlib import import_module
import pytest
from user.providers import CustomPhoneProvider
from faker import Faker


fakeUser = Faker()
fakeUser.add_provider(CustomPhoneProvider)


class TestUserRegistrationForm(TestCase):

    def setUp(self):
        self.data = {
            'email': fakeUser.email(),
            'firstname': fakeUser.first_name(),
            'lastname': fakeUser.last_name(),
            'password1': 'secretdeadlypassword',
            'password2': 'secretdeadlypassword',
            'phone': fakeUser.phone_number(),
            'image': factory.django.ImageField(from_path=r"C:\Users\Elisha\Pictures\Screenshots\Screenshot (16).png", filename=r"\newimage", format="png")
        }
        self.form = UserRegistrationForm(data=self.data)
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.request.FILES['image'] = self.data['image']
        self.request.POST = self.data
        self.form.is_valid()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        self.request.session = engine.SessionStore(session_key)
        self.request.META['SERVER_NAME'] = 'testserver'
        self.request.META['REQUEST_METHOD'] = 'POST'
        self.user = self.form.save(self.request)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())

    def test_form_saved_data(self):
        self.assertTrue(self.user)

    def test_firstname_saved(self):
        self.assertEqual(self.user.firstname, self.form.data['firstname'])

    def test_lastname_saved(self):
        self.assertEqual(self.user.lastname, self.form.data['lastname'])


class TestProfileUpdateForm(TestCase):

    def setUp(self):
        self.data = {
            'image': factory.django.ImageField(filename="uploadedImage.jpg")
        }
        self.form = ProfileUpdateForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())


class TestDriverUpdateForm(TestCase):

    def setUp(self):
        self.data = {
            'firstname': fakeUser.first_name(),
            'lastname': fakeUser.last_name(),
            'location': fakeUser.address(),
            'status': fakeUser.random_element(elements=
                ('Not Avaliable', 'Busy', 'Avaliable')),
            'journey_type': ['Within the city']
            # 'journey_type': fakeUser.random_elements(elements=
                # ('IN', 'OUT'), unique=True)
        }
        self.form = DriverUpdateForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())


class TestVehicleUpdateForm(TestCase):

    def setUp(self):
        self.data = {
            'name': fakeUser.text(max_nb_chars=20),
            'plate_number': fakeUser.bothify("???-###-???"),
            'capacity': fakeUser.random_int(min=1, max=18),
            'color': fakeUser.color_name(),
            'vehicle_type': fakeUser.random_element(elements=('Tricycle', 'Bus', 'Car'))
        }
        self.form = DriverUpdateForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())
