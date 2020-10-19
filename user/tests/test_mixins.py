from django.test import TestCase, RequestFactory, Client
from user.mixins import Update_view
from user.tests.factories import UserFactory
from user import views
from faker import Faker
import factory
from django.urls import reverse
from user.models import User
import pytest
from user.forms import  DriverProfileUpdateForm, VehicleUpdateForm


fake = Faker()


class TestUpdateViewMixin(TestCase):

    def setUp(self):
        self.view = views.update_profile()
        self.user = UserFactory()
        self.data = {
            'firstname': self.fake.first_name(),
            'lastname': self.fake.last_name(),
            'image': factory.django.ImageField(from_path=r"C:\Users\Elisha\Pictures\Screenshots\Screenshot (16).png", filename=r"\profile_pics\newimage", format="png")

        }
        self.request = RequestFactory().post(
            reverse('driver_profile_update'), self.data)
        self.request.user = self.user
        self.response = views.update_profile.as_view()(self.request)
        self.user.refresh_from_db()

    def test_success_url_redirect(self):

        self.assertEqual(self.response.status_code, 302)
        self.assertRedirects(self.response, reverse(
            'user_profile_detail'), fetch_redirect_response=False)

    def test_user_updated_if_valid(self):
        self.assertEqual(self.user.firstname, self.data.get('firstname'))
        self.assertEqual(self.user.lastname, self.data.get('lastname'))


class TestUpdateFormInvalid(TestCase):

    def setUp(self):
        self.fake = Faker()
        self.view = views.update_profile()
        self.user = UserFactory()
        self.invalid_data = {
            'email': 'invalid_email'
        }
        self.request = RequestFactory().post(
            reverse('driver_profile_update'), self.invalid_data)
        self.request.user = self.user
        self.response = views.update_profile.as_view()(self.request)
        self.user.refresh_from_db()

    # def test_uForm_invalid(self):
    #     self.assertFalse(self.response.context_data['pForm'].is_valid())

    def test_pForm_invalid(self):
        self.assertFalse(self.response.context_data['Form'].is_valid())


class TestGet(TestCase):

    def setUp(self):
        self.fake = Faker()
        self.view = views.update_profile()
        self.user = UserFactory()
        self.request = RequestFactory().get(
            reverse('driver_profile_update'))
        self.request.user = self.user
        self.response = views.update_profile.as_view()(self.request)
        self.user.refresh_from_db()

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_uForm_is_in_context(self):
        self.assertIn('uForm', self.response.context_data)

    def test_pForm_is_in_context(self):
        self.assertIn('pForm', self.response.context_data)
