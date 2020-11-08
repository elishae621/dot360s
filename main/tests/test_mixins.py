from django.test import TestCase, RequestFactory
from main import views
from faker import Faker
from django.urls import reverse
from user.models import User
from main.models import Request, Ride, Order
from django.http import Http404
from main.signals import order_accepted

fake = Faker()


class TestGetLoggedInUserRideMixin(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
  
    
    def test_ride_exist(self):
        request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        self.ride = Ride.objects.get(request=request)
        http_request = RequestFactory().get(reverse('unaccepted_request'))
        http_request.user = self.passenger
        response = views.UnacceptedRequest.as_view()(http_request)
        self.assertEqual(
            views.UnacceptedRequest.get_queryset(views.UnacceptedRequest)[0], self.ride)
        
    def test_ride_not_found(self):
        http_request = RequestFactory().get(reverse('unaccepted_request'))
        http_request.user = self.passenger
        with self.assertRaises(Http404):
            response = views.UnacceptedRequest.as_view()(http_request)

    
class TestOrderNotAcceptedMixin(TestCase):
    def setUp(self):
        driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = driver_user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
    def test_order_not_accepted_works(self):
        order = Order.objects.get(request=self.request)
        order.accepted = True  
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)
        self.http_request = RequestFactory().get('unaccepted_request')
        self.http_request.user = self.passenger
        self.response = views.UnacceptedRequest.as_view()(self.http_request)
        
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('order_detail', kwargs={'slug': order.slug}))