from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
import factory
from faker import Faker
from .factories import UserFactory
from user import views
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase, Client
from user.models import User, Driver
from django.http import Http404
from user.forms import UserRegistrationForm
import pytest


class TestUserProfileDetailView(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        url = reverse('user_profile_detail')
        self.request = self.factory.get(url)

    def test_user_profile_detail_view(self):
        """test that user Driver detail
        gets the correct user's Driver"""

        user = UserFactory()
        self.request.user = user
        response = views.user_profile_detail_view.as_view()(self.request)
        self.assertEqual(
            views.user_profile_detail_view.get_queryset(views.user_profile_detail_view)[0], Driver.objects.filter(user=user).first())

    def test_user_with_no_profile(self):
        user = UserFactory(Driver=None)
        self.request.user = user
        with self.assertRaises(Http404):
            response = views.user_profile_detail_view.as_view()(self.request)
