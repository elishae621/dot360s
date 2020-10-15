from django.test import TestCase
from user.models import User, Profile, Driver, Vehicle, Passenger, Request, Ride
from dot360s.settings import INSTALLED_APPS, AUTH_USER_MODEL
from django.db import transaction
from django.shortcuts import reverse
from faker import Faker


class TestSettings(TestCase):
    def test_account_configuration(self):
        assert 'user.apps.UserConfig' in INSTALLED_APPS
        assert 'user.User' == AUTH_USER_MODEL


class TestCreateSuperuser(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.superuser = User.objects.create_superuser(email=self.faker.email(),
            firstname=self.faker.first_name(), lastname=self.faker.last_name(),
            password=self.faker.password())

    def test_default_is_staff(self):
        self.assertTrue(self.superuser.is_staff)

    def test_default_is_superuser(self):
        self.assertTrue(self.superuser.is_superuser)

    def test_default_is_active(self):
        self.assertTrue(self.superuser.is_active)

    def test_not_is_staff(self):
        with self.assertRaises(ValueError, msg="Superuser must be assigned to is_staff=True."):
            superuser = User.objects.create_superuser(email=self.faker.email(),
                firstname=self.faker.first_name(), lastname=self.faker.last_name(),
                password=self.faker.password(), is_staff=False)

    def test_not_is_superuser(self):
        with self.assertRaises(ValueError, msg="Superuser must be assigned to is_superuser=True."):
            superuser = User.objects.create_superuser(email=self.faker.email(),
                firstname=self.faker.first_name(), lastname=self.faker.last_name(),
                password=self.faker.password(), is_superuser=False)


class TestCreateUser(TestCase):
    def setUp(self):
        self.faker = Faker()

    def test_not_email(self):
        with self.assertRaises(ValueError, msg="You must provide an email address"):
            user = User.objects.create_user(
                email="", firstname=self.faker.first_name(), lastname=self.faker.last_name(), password=self.faker.password()
            )


class TestUserModel(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.user = User.objects.create(
            email=self.faker.email(), firstname=self.faker.first_name(), lastname=self.faker.last_name()
        )

    def test_str_function(self):
        self.assertEqual(str(self.user), self.user.firstname)

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), reverse(
            'profile_detail', kwargs={'pk': self.user.pk}))


class TestProfileModel(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.user = User.objects.create(email=self.faker.email(),
            firstname=self.faker.first_name(), lastname=self.faker.last_name())

    def test_str_function(self):
        self.assertEqual(str(self.user.profile),
                         f"{self.user.firstname}'s profile")

    def test_get_absolute_url(self):
        self.assertEqual(self.user.profile.get_absolute_url(), reverse(
            'profile_detail', kwargs={'pk': self.user.pk}))


class TestDriver(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.driver = Driver.objects.create(email=self.faker.email(),
            firstname=self.faker.first_name(), lastname=self.faker.last_name(),
            username=self.faker.user_name(), is_driver=True)
        
    def test_str_function(self):
        self.assertEqual(str(self.driver), f"Driver: {self.driver.username}")


class TestPassenger(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.passenger = Passenger.objects.create(email=self.faker.email(),
            firstname=self.faker.first_name(), lastname=self.faker.last_name())

    def test_str_function(self):
        self.assertEqual(str(self.passenger), f"Passenger: {self.passenger.email}")


class TestRequest(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.driver = Driver.objects.create(email=self.faker.email(),
            firstname=self.faker.first_name(), lastname=self.faker.last_name(),
            username=self.faker.user_name())
        self.passenger = Passenger.objects.create(email=self.faker.email(),
            firstname=self.faker.first_name(), lastname=self.faker.last_name())

        self.request = Request.objects.create(driver=self.driver, 
            passenger=self.passenger, from_address="address", to_address="address")
    
    def test_str_function(self):
        self.assertEqual(str(self.request), 
            f"Request: {self.driver}, {self.passenger}")



class TestRide(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.driver = Driver.objects.create(email=self.faker.email(),
            firstname=self.faker.first_name(), lastname=self.faker.last_name(),
            username=self.faker.user_name())
        self.passenger = Passenger.objects.create(email=self.faker.email(),
            firstname=self.faker.first_name(), lastname=self.faker.last_name())
        self.request = Request.objects.create(driver=self.driver, 
            passenger=self.passenger, from_address="address", to_address="address")
        self.ride = Ride.objects.create(request=self.request)

    def test_str_function(self):
        self.assertEqual(str(self.ride), 
            f"Ride => Request: {self.driver}, {self.passenger}")

