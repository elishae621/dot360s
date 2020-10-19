from django.test import TestCase
from user.models import User, Driver, Vehicle, Request, Ride
from dot360s.settings import INSTALLED_APPS, AUTH_USER_MODEL
from django.db import transaction
from faker import Faker
from user.providers import CustomPhoneProvider
from phonenumber_field.phonenumber import PhoneNumber
from django.urls import reverse_lazy


fake = Faker()
fake.add_provider(CustomPhoneProvider)


class TestSettings(TestCase):
    def test_account_configuration(self):
        self.assertIn('user.apps.UserConfig', INSTALLED_APPS)
        self.assertEqual('user.User', AUTH_USER_MODEL)


class TestCreateSuperuser(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(email=fake.email(),
        firstname=fake.first_name(), lastname=fake.last_name(),
        phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164, password=fake.password())

    def test_default_is_staff(self):
        self.assertTrue(self.superuser.is_staff)

    def test_default_is_superuser(self):
        self.assertTrue(self.superuser.is_superuser)

    def test_default_is_active(self):
        self.assertTrue(self.superuser.is_active)
       
    def test_default_is_driver(self):
        self.assertFalse(self.superuser.is_driver)

    def test_not_is_staff(self):
        with self.assertRaises(ValueError, msg="Superuser must be assigned to is_staff=True."):
            superuser = User.objects.create_superuser(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164, password=fake.password(), is_staff=False)

    def test_not_is_superuser(self):
        with self.assertRaises(ValueError, msg="Superuser must be assigned to is_superuser=True."):
            superuser = User.objects.create_superuser(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164,
            password=fake.password(), is_superuser=False)


class TestCreateUser(TestCase):
    def setUp(self):
        fake = Faker()
        self.user = User.objects.create_user(email=fake.email(),
        firstname=fake.first_name(), lastname=fake.last_name(),
        phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164, password=fake.password())

    def test_not_superuser(self):
        self.assertFalse(self.user.is_superuser)

    def test_not_staff(self):
        self.assertFalse(self.user.is_staff)

    def test_not_active(self):
        self.assertTrue(self.user.is_active)

    def test_not_drvier(self):
        self.assertFalse(self.user.is_driver)

    def test_not_email(self):
        with self.assertRaises(ValueError, msg="You must provide an email address"):
            user = User.objects.create_user(email="", firstname=fake.first_name(), lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164, password=fake.password())


class TestUserModel(TestCase):
    def setUp(self):
        fake = Faker()
        self.user = User.objects.create(
            email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164, password=fake.password())

    def test_str_function(self):
        self.assertEqual(str(self.user), f'{self.user.firstname}')

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), reverse_lazy(
            'home'))


class TestDriverModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164, password=fake.password(), is_driver=True)

    def test_str_function(self):
        self.assertEqual(str(self.user.driver),
            f'Driver => {self.user.firstname}')

    def test_get_absolute_url(self):
        self.assertEqual(self.user.driver.get_absolute_url(), reverse_lazy(
            'driver_profile_detail', kwargs={'pk':self.user.driver.pk}))

class TestVehicleModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164, password=fake.password(), is_driver=True)

    def test_str_function(self):
        self.assertEqual(str(self.user.driver.vehicle),
            f"{self.user.driver}'s vehicle")

    def test_get_absolute_url(self):
        self.assertEqual(self.user.driver.vehicle.get_absolute_url(), reverse_lazy(
            'driver_profile_detail', kwargs={'pk': self.user.driver.pk}))


class TestRequest(TestCase):
    def setUp(self):
        fake = Faker()
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164,
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164,
            password=fake.password())

        self.request = Request.objects.create(driver=self.driver,passenger=self.passenger, from_address=fake.address(), to_address=fake.address())

    def test_str_function(self):
        self.assertEqual(str(self.request),
            f"Request: {self.driver}, {self.passenger}")


class TestRide(TestCase):
    def setUp(self):
        fake = Faker()
        fake = Faker()
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164,
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=PhoneNumber.from_string(phone_number=fake.phone_number(), region='RU').as_e164,
            password=fake.password())
        self.request = Request.objects.create(driver=self.driver,
        passenger=self.passenger, from_address=fake.address(), to_address=fake.address())
        self.ride = Ride.objects.create(request=self.request)

    def test_str_function(self):
        self.assertEqual(str(self.ride),
            f"Ride => Request: {self.driver}, {self.passenger}")
