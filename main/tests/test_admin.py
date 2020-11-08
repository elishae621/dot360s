from django.test import TestCase, RequestFactory
from main.admin import RequestAdmin, RideAdmin, OrderAdmin
from user.models import User
from main.models import Request, Ride, Order
from faker import Faker
fake = Faker()


class TestRequestAdmin(TestCase):
    def setUp(self):
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.http_request = RequestFactory().get(f'/admin/user/request/{self.request.pk}/change/')
    
    def test_no_add_permissions(self):
        self.assertFalse(RequestAdmin.has_add_permission(RequestAdmin, self.http_request))

class TestRideAdmin(TestCase):
    def setUp(self):
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.ride = Ride.objects.filter(request=self.request).first()
        self.http_request = RequestFactory().get(f'/admin/user/ride/{self.ride.pk}/change/')
    
    def test_no_add_permissions(self):
        self.assertFalse(RideAdmin.has_add_permission(RideAdmin, self.http_request))


class TestOrderAdmin(TestCase):
    def setUp(self):
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.order = Order.objects.filter(request=self.request).first()
        self.http_request = RequestFactory().get(f'/admin/user/order/{self.order.pk}/change/')
    
    def test_no_add_permissions(self):
        self.assertFalse(OrderAdmin.has_add_permission(OrderAdmin, self.http_request))