from django.test import TestCase, RequestFactory
from user.forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from faker import Faker
import factory
from django.urls import reverse
from user.models import User
from django.http import HttpRequest
from django.conf import settings
from importlib import import_module
import pytest



class TestUserRegistrationForm(TestCase):

    def setUp(self):
        self.fakeUser = Faker()
        self.data = {
            'email': self.fakeUser.email(),
            'firstname': self.fakeUser.first_name(),
            'lastname': self.fakeUser.last_name(),
            'password1': 'secretdeadlypassword',
            'password2': 'secretdeadlypassword',
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
        pass

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
        self.fakeProfile = Faker()
        self.data = {
            'image': factory.django.ImageField(filename="uploadedImage.jpg")
        }
        self.form = ProfileUpdateForm(data=self.data)

    def test_form_is_valid(self):
        assert self.form.is_valid()


class TestUserUpdateForm(TestCase):

    def setUp(self):
        self.fakeUser = Faker()
        self.data = {
            'firstname': self.fakeUser.first_name(),
            'lastname': self.fakeUser.last_name()
        }
        self.form = UserUpdateForm(data=self.data)

    def test_form_is_valid(self):
        assert self.form.is_valid()
