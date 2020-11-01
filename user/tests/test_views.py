import time
from django.contrib.messages.api import get_messages
from django.http.response import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls.base import reverse_lazy 
from user import views
from faker import Faker
from user.models import User, Driver, Vehicle, Request, Ride, Order
from django.urls import reverse
import pytz
from random import randint
from unittest.mock import Mock, patch
import pytest
from user.signals import order_accepted
from django.template.loader import render_to_string
from user.paystack_api import authorize, verify
from user.forms import FundAccountForm

fake = Faker()


class TestCreateRequest(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = Driver.objects.filter(user=user).first()
        self.passenger = User.objects.create(email=fake.email(), 
            firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'), password=fake.password())
        self.data = {
            'from_address': fake.address(),
            'to_address': fake.address(),
            'intercity': fake.random_element(elements=[False, True]), 
            'city': fake.random_element(elements=Driver.City.values),
            'request_vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type.values), 
            'no_of_passengers': fake.random_int(min=1, max=20), 
            'load': fake.random_element(elements=[False, True]), 
            'time': fake.date_time()
        }
        self.driver.location = self.data.get('city')
        self.driver.status = 'AV'
        if self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = self.data.get('request_vehicle_type')
        self.driver.save()
        self.driver.vehicle.save()
        self.request = RequestFactory().post(reverse('create_request'), data=self.data)
        self.request.user = self.passenger
        self.response = views.RequestCreate.as_view()(self.request)
        self.response.client = Client()
        self.request_created = Request.objects.filter(
            from_address=self.data.get('from_address')).filter(
            to_address=self.data.get('to_address')).filter(
            intercity=self.data.get('intercity')).filter(
            city=self.data.get('city')).filter(
            request_vehicle_type=self.data.get('request_vehicle_type')).filter(
            no_of_passengers=self.data.get('no_of_passengers')).filter(
            load=self.data.get('load')).filter(
            time=self.data.get('time')).first()    
        self.order = Order.objects.filter(request=self.request_created).first()
        self.order.driver.add(self.driver)
        self.order.save()

    def test_request_is_created(self):
        self.driver.location = self.data.get('city')
        self.driver.status = 'AV'
        if self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = self.data.get('request_vehicle_type')
        self.driver.save()
        self.driver.vehicle.save()
        self.request = RequestFactory().post(reverse('create_request'), data=self.data)
        self.request.user = self.passenger
        self.response = views.RequestCreate.as_view()(self.request)
        self.request_created = Request.objects.filter(
            from_address=self.data.get('from_address')).filter(
            to_address=self.data.get('to_address')).filter(
            intercity=self.data.get('intercity')).filter(
            city=self.data.get('city')).filter(
            request_vehicle_type=self.data.get('request_vehicle_type')).filter(
            no_of_passengers=self.data.get('no_of_passengers')).filter(
            load=self.data.get('load')).filter(
            time=self.data.get('time')).first()
        
        self.assertTrue(self.request_created)

    def test_passenger_of_request_is_logged_in_user(self):
        self.driver.location = self.data.get('city')
        self.driver.status = 'AV'
        if self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = self.data.get('request_vehicle_type')
        self.driver.save()
        self.driver.vehicle.save()
        self.request = RequestFactory().post(reverse('create_request'), data=self.data)
        self.request.user = self.passenger
        self.response = views.RequestCreate.as_view()(self.request)
        self.request_created = Request.objects.filter(
            from_address=self.data.get('from_address')).filter(
            to_address=self.data.get('to_address')).filter(
            intercity=self.data.get('intercity')).filter(
            city=self.data.get('city')).filter(
            request_vehicle_type=self.data.get('request_vehicle_type')).filter(
            no_of_passengers=self.data.get('no_of_passengers')).filter(
            load=self.data.get('load')).filter(
            time=self.data.get('time')).first()
        self.request_created.passenger = self.request.user

        self.assertEqual(self.request_created.passenger, self.passenger)

    
    def test_redirect_if_no_driver_is_avaliable(self):
        # driver is in city but not avaliable
        self.driver.location = self.data.get('city')
        self.driver.status = fake.random_element(elements=['NA', 'BU'])
        if self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = self.data.get('request_vehicle_type')
        self.driver.save()
        self.driver.vehicle.save()
        self.request = RequestFactory().post(reverse('create_request'), data=self.data)
        self.request.user = self.passenger
        self.response = views.RequestCreate.as_view()(self.request)
        self.response.client = Client()
        self.request_created = Request.objects.filter(
            from_address=self.data.get('from_address')).filter(
            to_address=self.data.get('to_address')).filter(
            intercity=self.data.get('intercity')).filter(
            city=self.data.get('city')).filter(
            request_vehicle_type=self.data.get('request_vehicle_type')).filter(
            no_of_passengers=self.data.get('no_of_passengers')).filter(
            load=self.data.get('load')).filter(
            time=self.data.get('time')).first()
        
        self.assertRedirects(self.response, reverse('no_avaliable_driver'))
    
    def test_order_created_with_the_right_request(self):
        self.assertTrue(Order.objects.filter(request=self.request_created).first())

    def test_order_of_request_is_created_with_qualified_driver(self):
        self.assertTrue(Order.objects.filter(driver__user=self.driver.user))


class TestDeleteRequest(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(driver=self.driver,passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        self.ride = Ride.objects.get(request=self.request)
        self.http_request = RequestFactory().post(reverse('delete_request'))
        self.http_request.user = self.passenger
        self.response = views.RequestDelete.as_view()(self.http_request)
        self.response.client = Client()
        
    def test_request_is_deleted(self):
        self.assertFalse(Request.objects.filter(passenger=self.passenger))

    def test_ride_is_deleted(self):
        self.assertFalse(Ride.objects.filter(request__isnull=True))

    def test_success_url_redirect(self):
        self.assertEqual(self.response.status_code, 302)


class TestVerifyTransaction(TestCase):
    def setUp(self):
        driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = driver_user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(driver=self.driver,passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        self.ride = Ride.objects.get(request=self.request)
        self.ride.refresh_from_db()
        self.client = Client()
    
    @patch('user.paystack_api.requests.get')
    @patch('user.mixins.messages.add_message')
    def test_message_if_status_is_true(self, message_mock, verify_mock):
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                "amount": 27000,
                "currency": "NGN",
                "transaction_date": "2020-10-01T11:03:09.000Z",
                "status": "success",
                "reference": "DG4uishudoq9OLD",
                "domain": "test",
                "metadata": 0,
                "gateway_response": "Successful",
                "message": None,
                "channel": "card"
            }
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        order = self.ride.request.request_order
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        message = message_mock.call_args_list[0][0][2]

        self.assertEqual(message, "Verification successful")

    @patch('user.paystack_api.requests.get')
    @patch('user.mixins.messages.add_message')
    def test_redirect_if_status_is_true(self, message_mock, verify_mock):
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                "amount": 27000,
                "currency": "NGN",
                "transaction_date": "2020-10-01T11:03:09.000Z",
                "status": "success",
                "reference": "DG4uishudoq9OLD",
                "domain": "test",
                "metadata": 0,
                "gateway_response": "Successful",
                "message": None,
                "channel": "card"
            }
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        order = self.ride.request.request_order
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        response.client = Client()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse_lazy('passenger_home'))

    @patch('user.paystack_api.requests.get')
    @patch('user.mixins.messages.add_message')
    def test_message_if_status_is_false(self, message_mock, verify_mock):
        verify_json = {
            "status": False,
            "message": "Transaction reference not recognized",
            "data": {}
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        order = self.ride.request.request_order
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        message = message_mock.call_args_list[0][0][2]

        self.assertEqual(message, "Transaction reference not recognized")

    @patch('user.paystack_api.requests.get')
    @patch('user.mixins.messages.add_message')
    def test_redirect_if_status_is_false(self, message_mock, verify_mock):
        verify_json = {
            "status": False,
            "message": "Transaction reference not recognized",
            "data": {}
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443", follow=False)
        order = self.ride.request.request_order
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        response.client = Client()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse_lazy('fund_account'))

    
    @patch('user.mixins.messages.add_message')
    def test_message_if_reference_not_in_request_GET(self, message_mock):
        message_mock.return_value = Mock()
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/")
        order = self.ride.request.request_order
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        message = message_mock.call_args_list[0][0][2]

        self.assertEqual(message, "Improperly configured. No reference in verify. Please try again. If this continues, contact Dot360s")

    @patch('user.paystack_api.requests.get')
    @patch('user.mixins.messages.add_message')
    def test_redirect_if_reference_not_in_request_GET(self, message_mock, verify_mock):
        verify_json = {
            "status": False,
            "message": "Transaction reference not recognized",
            "data": {}
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/", follow=False)
        order = self.ride.request.request_order
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        response.client = Client()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse_lazy('fund_account'))


class TestOrderListView(TestCase):
    def setUp(self):
        driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = driver_user.driver
        self.http_request = RequestFactory().get(reverse_lazy('driver_orders'))     
        self.http_request.user = driver_user        
        self.response = views.OrderListView.as_view()(self.http_request)

    def test_get_queryset(self):
        driver_order_queryset = Order.objects.filter(driver=self.driver).order_by('-time_posted')
        self.assertIsInstance(self.response.context_data, dict)
        self.assertEqual(
            list(self.response.context_data['orders']), list(driver_order_queryset))


class TestTakeOrderView(TestCase):
    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = self.driver_user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

    def test_order_accepted_is_true(self):
        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        order = self.request.request_order
        kwargs = {'slug': order.slug}
        self.http_request = RequestFactory().get(reverse('take_order', kwargs=kwargs))
        self.http_request.user = self.driver_user
        self.response = views.TakeOrder.as_view()(self.http_request, kwargs.get('slug'))

        self.assertTrue(order.accepted)

    def test_fetches_correct_order(self):
        request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        order = request.request_order
        http_request = RequestFactory().get(reverse('take_order', kwargs={'slug': order.slug}))
        http_request.user = self.driver_user
        response = views.TakeOrder.as_view()(http_request)

        self.assertEqual(
            views.TakeOrder.get_queryset(views.TakeOrder)[0], order)


class TestFundAccountView(TestCase):
    def setUp(self):
        driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = driver_user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), account_balance=fake.random_int(min=100, max=5000))
        self.old_balance = self.passenger.account_balance
        
    @patch('user.paystack_api.requests.get')
    @patch('user.paystack_api.requests.post')    
    def test_amount_funded_is_added_to_balance_if_successful(self, auth_mock, verify_mock):
        auth_json = {
            'status': True, 
            'message': 'Authorization URL created', 
            'data': {
                'authorization_url': 'https://checkout.paystack.com/9mzlnrn30akanzp', 
                'access_code': '9mzlnrn30akanzp', 
                'reference': 'yzlei4h480'
            }
        }
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                "amount": 27000
            }
        }
        auth_mock.return_value.json.return_value = auth_json
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().post(reverse_lazy('fund_account'), data={'amount': 27000})
        http_request.user = self.passenger
        response = views.FundAccount.as_view()(http_request)
        self.passenger.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, auth_json['data'].get('authorization_url'))

    @patch("user.views.messages.add_message")
    def test_error_message_was_printed_out(self, message_mock):
        message_mock.return_value = Mock()
        http_request = RequestFactory().post(reverse_lazy('fund_account'), data={'amount': 27000})
        http_request.user = self.passenger
        response = views.FundAccount.as_view()(http_request)
        
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, "An Error Occured, Paystack cannot be reached at this time")

    @patch("user.views.messages.add_message")
    def test_form_is_rendered_to_response_if_auth_response_is_none(self, message_mock):
        message_mock.return_value = Mock()
        http_request = RequestFactory().post(reverse_lazy('fund_account'), data={'amount': 27000})
        http_request.user = self.passenger
        response = views.FundAccount.as_view()(http_request)
        
        self.assertEqual(response.context_data['form'].changed_data, ['amount'])
 

class TestOngoingOrderView(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(driver=self.driver,passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.ride = Ride.objects.get(request=self.request)
        self.ride.status = 3
        self.order = Order.objects.filter(request=self.request).first()
        kwargs = {'slug': self.order.slug}
        http_request = RequestFactory().get(reverse_lazy('ongoing_order', kwargs=kwargs))
        self.response = views.OngoingOrder.as_view()(http_request, kwargs)

    def test_ride_status_has_been_changed_to_ongoing(self):
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, 4)