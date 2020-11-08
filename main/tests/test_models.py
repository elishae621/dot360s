from django.test import TestCase
from user.models import User, Vehicle
from main.models import Request, Ride, Order
from faker import Faker
from django.urls import reverse
from django.template.defaultfilters import slugify
from math import floor
from time import time


fake = Faker()


class TestRequest(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(driver=self.driver,passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(), request_vehicle_type=fake.random_element(
        elements=Vehicle.Vehicle_type.values), intercity=fake.random_element(elements=[True, False]))

    def test_str_function(self):
        self.assertEqual(str(self.request),
            f"Request: {self.driver}, {self.passenger}")

    def test_get_absolute_url(self):
        self.assertEqual(self.request.get_absolute_url(), reverse('order_detail', kwargs={'slug': self.request.request_order.slug}))


class TestRide(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.request = Request.objects.create(driver=self.driver,
        passenger=self.passenger, from_address=fake.address(), to_address=fake.address())
        self.ride = Ride.objects.filter(request=self.request).first()

    def test_str_function(self):
        self.assertEqual(str(self.ride),
            f"Ride => Request: {self.driver}, {self.passenger}")

    def test_get_absolute_url(self):
        self.assertEqual(self.ride.get_absolute_url(), reverse('order_detail', kwargs={'slug': self.request.request_order.slug}))


class TestOrder(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(), 
        lastname=fake.last_name(), phone=fake.numerify(text='080########'), password=fake.password())
        self.request = Request.objects.create(driver=self.driver,
        passenger=self.passenger, from_address=fake.address(), to_address=fake.address())
        self.order = Order.objects.filter(request=self.request).first()
        self.order.driver.add(self.driver)
        order = self.order
        order.save()

    def test_str_function(self):
        self.assertEqual(str(self.order),
            f"{self.request.passenger.firstname}'s order")

    def test_get_absolute_url(self):
        self.assertEqual(self.order.get_absolute_url(), reverse('order_detail', kwargs={'slug': self.order.slug}))

    def test_slug_is_put_in_save(self):
        print(self.order.slug)
        self.assertEqual(self.order.slug, f"{str(slugify(floor(time()*10)))}-{str(slugify(self.request.from_address))}")