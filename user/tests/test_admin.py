from django.test import TestCase, RequestFactory
from user.admin import (
    UserAdmin, DriverInline, VehicleInline,
    DriverAdmin, VehicleAdmin,
)
from user.models import User, Vehicle, Driver
from main.models import Request
from unittest.mock import patch, Mock
from faker import Faker
fake = Faker()


class TestUserAdmin(TestCase):
    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = self.driver_user.driver
        self.passenger = User.objects.create(email=fake.email(), 
            firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'), password=fake.password())
        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        self.http_request = RequestFactory().get(f'/admin/user/user/')

    @patch('user.admin.admin.ModelAdmin.get_inline_instances')
    def test_get_inline_instances_returns_for_obj(self, get_inline_instances):
        get_inline_instances.return_value = (DriverInline,)
        
        self.assertTrue(UserAdmin.get_inline_instances(
            UserAdmin, request=self.request, obj=self.passenger))

    def test_get_inline_instances_returns_none_for_no_obj(self):
        self.assertFalse(UserAdmin.get_inline_instances(UserAdmin, request=self.request, obj=None))

    def test_driver_function_for_passenger(self):
        self.assertFalse(UserAdmin.driver(UserAdmin, self.passenger))

    def test_driver_function_for_driver(self):
        self.assertTrue(UserAdmin.driver(UserAdmin, self.driver_user))
        
    @patch("user.admin.messages")
    def test_make_driver_updates_queryset(self, message_mock):
        message_mock.return_value = Mock()
        UserAdmin.make_driver(UserAdmin, self.http_request, queryset=User.objects.filter(pk=self.passenger.pk))
        self.passenger.refresh_from_db()
        self.assertTrue(self.passenger.is_driver)

    @patch("user.admin.messages")
    def test_make_driver_message_works(self, message_mock):
        message_mock.return_value = Mock()
        UserAdmin.make_driver(UserAdmin, self.http_request, queryset=User.objects.filter(pk=self.passenger.pk))
        message = message_mock.success.mock_calls[0].args[1]
        self.assertEqual(message, "Selected User(s) Marked as drivers Successfully !!")

    @patch("user.admin.messages")
    def test_make_driver_error_message_works(self, message_mock):
        self.http_request = RequestFactory().get(f'/admin/user/driver/')
        message_mock.return_value = Mock()
        UserAdmin.make_driver(DriverAdmin, self.http_request, queryset=Driver.objects.filter(pk=self.driver.pk))
        message = message_mock.error.mock_calls[0].args[1]
        self.assertEqual(message, "This can only be done from the user model")


    @patch("user.admin.messages")
    def test_make_not_driver_updates_queryset(self, message_mock):
        message_mock.return_value = Mock()
        UserAdmin.make_not_driver(UserAdmin, self.http_request, queryset=User.objects.filter(pk=self.driver_user.pk))
        self.driver_user.refresh_from_db()
        self.assertFalse(self.driver_user.is_driver)

    @patch("user.admin.messages")
    def test_make_not_driver_message_works(self, message_mock):
        message_mock.return_value = Mock()
        UserAdmin.make_not_driver(UserAdmin, self.http_request, queryset=User.objects.filter(pk=self.driver_user.pk))
        message = message_mock.success.mock_calls[0].args[1]
        self.assertEqual(message, "Selected user(s) Marked as non drivers Successfully !!")

    @patch("user.admin.messages")
    def test_make_not_driver_error_message_works(self, message_mock):
        self.http_request = RequestFactory().get(f'/admin/user/driver/')
        message_mock.return_value = Mock()
        UserAdmin.make_not_driver(DriverAdmin, self.http_request, queryset=Driver.objects.filter(pk=self.driver.pk))
        message = message_mock.error.mock_calls[0].args[1]
        self.assertEqual(message, "This can only be done from the user model")

    def test_no_add_permissions(self):
        self.assertFalse(UserAdmin.has_add_permission(UserAdmin, self.http_request))


class TestDriverAdmin(TestCase):
    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = self.driver_user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.request = Request.objects.create(driver=self.driver, passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        self.http_request = RequestFactory().get(f'/admin/user/driver/{self.driver.pk}/change/')

    @patch('user.admin.admin.ModelAdmin.get_inline_instances')
    def test_get_inline_instances_returns_for_obj(self, get_inline_instances):
        get_inline_instances.return_value = (VehicleInline,)
        self.assertTrue(DriverAdmin.get_inline_instances(
            DriverAdmin, request=self.http_request, obj=self.driver))

    def test_get_inline_instances_returns_none_for_no_obj(self):
        self.assertFalse(DriverAdmin.get_inline_instances(DriverAdmin, request=self.http_request, obj=None))

    def test_no_add_permissions(self):
        self.assertFalse(DriverAdmin.has_add_permission(DriverAdmin, self.http_request))


class TestVehicleAdmin(TestCase):
    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = self.driver_user.driver
        self.vehicle = Vehicle.objects.filter(owner=self.driver).first()
        self.http_request = RequestFactory().get(f'/admin/user/driver/{self.vehicle.pk}/change/')
            
    def test_no_add_permissions(self):
        self.assertFalse(VehicleAdmin.has_add_permission(VehicleAdmin, self.http_request))