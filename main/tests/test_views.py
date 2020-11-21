from django.test import Client, RequestFactory, TestCase
from main import views
from faker import Faker
from user.models import User, Driver, Vehicle
from main.models import Request, Ride, Order, Withdrawal
from django.urls import reverse
from unittest.mock import Mock, patch
from main.signals import order_accepted

fake = Faker()


class TestIndexView(TestCase):
    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = Driver.objects.filter(user=self.driver_user).first()
        self.passenger = User.objects.create(email=fake.email(), 
            firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'), password=fake.password())
        self.http_request = RequestFactory().get(reverse('home'))

    def test_redirect_for_drivers(self):
        self.http_request.user = self.driver_user
        response = views.Index.as_view()(self.http_request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('order_list'))

    def test_redirect_for_passengers(self):
        self.http_request.user = self.passenger
        response = views.Index.as_view()(self.http_request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('request_list'))


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
            'time': fake.date_time(), 
            'payment_method': "cash"
        }
        self.driver.location = self.data.get('city')
        self.driver.status = 'AV'
        self.driver.completed = True
        self.driver.save()
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
            from_address=self.data.get('from_address')).first()    
        self.order = Order.objects.filter(request=self.request_created).first()
        order_accepted.send(sender=Order, Order=self.order, Driver=self.driver)

    def test_passenger_is_the_right_passenger(self):
        self.assertEqual(self.request_created.passenger, self.passenger)

    def test_request_is_created(self):
        self.assertTrue(self.request_created)

    def test_only_one_request_is_created(self):
        request_created = Request.objects.filter(
            from_address=self.data.get('from_address')).filter(
            to_address=self.data.get('to_address')).filter(
            intercity=self.data.get('intercity')).filter(
            city=self.data.get('city')).filter(
            request_vehicle_type=self.data.get('request_vehicle_type')).filter(
            no_of_passengers=self.data.get('no_of_passengers')).filter(
            load=self.data.get('load')).filter(
            time=self.data.get('time'))

        self.assertEqual(len(request_created), 1)
        
    def test_driver_can_create_request(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        passenger_driver = Driver.objects.get(user=user)
        request = RequestFactory().post(reverse('create_request'), data=self.data)
        request.user = user
        response = views.RequestCreate.as_view()(request)
        response.client = Client()
        request_created = Request.objects.filter(
            from_address=self.data.get('from_address')).first()    
        order = Order.objects.filter(request=request_created).first()
        order_accepted.send(sender=Order, Order=self.order, Driver=self.driver)

        self.assertTrue(request_created)

    def test_driver_is_the_passenger_of_request(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        passenger_driver = Driver.objects.get(user=user)
        request = RequestFactory().post(reverse('create_request'), data=self.data)
        request.user = user
        response = views.RequestCreate.as_view()(request)
        response.client = Client()
        request_created = Request.objects.filter(
            from_address=self.data.get('from_address')).filter(to_address=self.data.get('to_address')).last()    
        order = Order.objects.filter(request=request_created).first()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)
       
        self.assertEqual(request_created.passenger, user)

    @patch('main.views.messages.add_message')
    def test_message_if_insufficient_balance(self, message_mock):
        message_mock.return_value = Mock()
        self.data = {
            'from_address': fake.address(),
            'to_address': fake.address(),
            'intercity': fake.random_element(elements=[False, True]), 
            'city': fake.random_element(elements=Driver.City.values),
            'request_vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type.values), 
            'no_of_passengers': fake.random_int(min=1, max=20), 
            'load': fake.random_element(elements=[False, True]), 
            'time': fake.date_time(), 
            'payment_method': "card"
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
        self.http_request = RequestFactory().post(reverse('create_request'), data=self.data)
        self.http_request.user = self.passenger
        self.response = views.RequestCreate.as_view()(self.http_request)
        self.response.client = Client()
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, "Insufficient Balance. Your ride costs 100.0 naira.")


    @patch('main.views.messages.add_message')
    def test_redirect_if_insufficient_balance(self, message_mock):
        message_mock.return_value = Mock()
        self.data = {
            'from_address': fake.address(),
            'to_address': fake.address(),
            'intercity': fake.random_element(elements=[False, True]), 
            'city': fake.random_element(elements=Driver.City.values),
            'request_vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type.values), 
            'no_of_passengers': fake.random_int(min=1, max=20), 
            'load': fake.random_element(elements=[False, True]), 
            'time': fake.date_time(), 
            'payment_method': "card"
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
        self.http_request = RequestFactory().post(reverse('create_request'), data=self.data)
        self.http_request.user = self.passenger
        self.response = views.RequestCreate.as_view()(self.http_request)
        self.response.client = Client()
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('fund_account'))

    def test_passenger_of_request_is_logged_in_user(self):
        self.assertEqual(self.request_created.passenger, self.passenger)

    
    def test_redirect_if_no_driver_is_avaliable(self):
        self.data = {
            'from_address': fake.address(),
            'to_address': fake.address(),
            'intercity': fake.random_element(elements=[False, True]), 
            'city': fake.random_element(elements=Driver.City.values),
            'request_vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type.values), 
            'no_of_passengers': fake.random_int(min=1, max=20), 
            'load': fake.random_element(elements=[False, True]), 
            'time': fake.date_time(),
            'payment_method': "cash"
        }
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
        
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('no_avaliable_driver', kwargs={'slug': self.request_created.order_of_request.slug}))
    
    def test_redirect_if_no_driver_is_marked_completed(self):
        self.data = {
            'from_address': fake.address(),
            'to_address': fake.address(),
            'intercity': fake.random_element(elements=[False, True]), 
            'city': fake.random_element(elements=Driver.City.values),
            'request_vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type.values), 
            'no_of_passengers': fake.random_int(min=1, max=20), 
            'load': fake.random_element(elements=[False, True]), 
            'time': fake.date_time(),
            'payment_method': "cash"
        }
        # driver is in city but not avaliable
        self.driver.location = self.data.get('city')
        self.driver.status = 'AV'
        if self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = self.data.get('request_vehicle_type')
        self.driver.completed = False
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
        
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('no_avaliable_driver', kwargs={'slug': self.request_created.order_of_request.slug}))
    
    def test_redirect_for_no_avaliable_driver_if_marked_not_active(self):
        self.data = {
            'from_address': fake.address(),
            'to_address': fake.address(),
            'intercity': fake.random_element(elements=[False, True]), 
            'city': fake.random_element(elements=Driver.City.values),
            'request_vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type.values), 
            'no_of_passengers': fake.random_int(min=1, max=20), 
            'load': fake.random_element(elements=[False, True]), 
            'time': fake.date_time(),
            'payment_method': "cash"
        }
        # driver is in city but not avaliable
        self.driver.location = self.data.get('city')
        self.driver.status = 'AV'
        if self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = self.data.get('request_vehicle_type')
        self.driver.completed = True
        self.driver.user.is_active = False
        self.driver.save()
        self.driver.user.save()
        self.driver.vehicle.save()
        http_request = RequestFactory().post(reverse('create_request'), data=self.data)
        http_request.user = self.passenger
        self.response = views.RequestCreate.as_view()(http_request)
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
        
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('no_avaliable_driver', kwargs={'slug': self.request_created.order_of_request.slug}))
    
    def test_redirect_for_no_avaliable_driver_if_driver_is_user(self):
        self.data = {
            'from_address': fake.address(),
            'to_address': fake.address(),
            'intercity': fake.random_element(elements=[False, True]), 
            'city': fake.random_element(elements=Driver.City.values),
            'request_vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type.values), 
            'no_of_passengers': fake.random_int(min=1, max=20), 
            'load': fake.random_element(elements=[False, True]), 
            'time': fake.date_time(),
            'payment_method': "cash"
        }
        # driver is in city but not avaliable
        self.driver.location = self.data.get('city')
        self.driver.status = 'AV'
        if self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = self.data.get('request_vehicle_type')
        self.driver.completed = True
        self.driver.user.is_active =True
        self.driver.save()
        self.driver.user.save()
        self.driver.vehicle.save()
        self.request = RequestFactory().post(reverse('create_request'), data=self.data)
        self.request.user = self.driver.user
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
        
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('no_avaliable_driver', kwargs={'slug': self.request_created.order_of_request.slug}))
    
    def test_order_created_with_the_right_request(self):
        self.assertTrue(Order.objects.filter(request=self.request_created).first())

    def test_driver_is_added_to_request(self):
        self.assertTrue(Order.objects.filter(driver__user=self.driver.user))

    def test_redirect_if_valid_drivers_exist(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('unaccepted_request'))


class TestCancelRequest(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        self.ride = Ride.objects.get(request=self.request)
        self.order = Order.objects.get(request=self.request)
        kwargs = {'slug': self.order.slug}
        self.http_request = RequestFactory().post(reverse('cancel_request', kwargs=kwargs))
        self.http_request.user = self.passenger
        self.response = views.CancelRequest.as_view()(self.http_request, **kwargs)
        self.response.client = Client()
        
    def test_ride_is_cancelled(self):
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status , "cancelled")

    def test_success_url_redirect(self):
        self.assertEqual(self.response.status_code, 302)

    
    def test_driver_status_is_now_avaliable(self):
        self.request.driver = self.driver
        self.request.save()
        kwargs = {'slug': self.order.slug}
        self.response = views.CancelRequest.as_view()(self.http_request, **kwargs)

        self.request.driver.refresh_from_db()
        self.assertEqual(self.request.driver.status, 'AV')

    def test_request_has_no_driver_is_ignored_for_change_of_status(self):
        kwargs = {'slug': self.order.slug}
        self.response = views.CancelRequest.as_view()(self.http_request, **kwargs)

        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status , "cancelled")
        self.assertEqual(self.response.status_code, 302)

    @patch('main.views.messages.add_message')
    def test_another_user_cannot_cancel_the_request_of_another(self, message_mock):
        message_mock.return_value = Mock()
        request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        ride = Ride.objects.get(request=request)
        kwargs = {'slug': request.order_of_request.slug}
        self.http_request = RequestFactory().post(reverse('cancel_request', kwargs=kwargs))
        self.http_request.user = self.driver.user
        self.response = views.CancelRequest.as_view()(self.http_request, **kwargs)
        self.response.client = Client()
        ride.refresh_from_db()
        self.assertNotEqual(ride.status , "cancelled")

    @patch('main.views.messages.add_message')
    def test_message_another_user_cannot_cancel_the_request_of_another(self, message_mock):
        message_mock.return_value = Mock()
        request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        ride = Ride.objects.get(request=request)
        kwargs = {'slug': request.order_of_request.slug}
        self.http_request = RequestFactory().post(reverse('cancel_request', kwargs=kwargs))
        self.http_request.user = self.driver.user
        self.response = views.CancelRequest.as_view()(self.http_request, **kwargs)
        self.response.client = Client()
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, "Error! You are not the creator of this request")

    @patch('main.views.messages.add_message')
    def test_redirect_for_another_user_cannot_cancel_the_request_of_another(self, message_mock):
        message_mock.return_value = Mock()
        request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        ride = Ride.objects.get(request=request)
        kwargs = {'slug': request.order_of_request.slug}
        self.http_request = RequestFactory().post(reverse('cancel_request', kwargs=kwargs))
        self.http_request.user = self.driver.user
        self.response = views.CancelRequest.as_view()(self.http_request, **kwargs)
        self.response.client = Client()
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('home'))

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

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
    def test_referral_paid_if_balance_above_200(self, message_mock, verify_mock):
        self.user1 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.user2 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), referral=self.user1.email)
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                'amount': 20000, # in kobo
            }
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        http_request.user = self.user2 
        response = views.VerifyTransaction.as_view()(http_request)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.account_balance, 50)

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
    def test_referral_status_changes_to_paid_if_paid(self, message_mock, verify_mock):
        self.user1 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.user2 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), referral=self.user1.email)
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                'amount': 20000, # in kobo
            }
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        http_request.user = self.user2 
        response = views.VerifyTransaction.as_view()(http_request)
        self.user1.refresh_from_db()
        self.assertEqual(self.user2.referral_status, "paid")

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
    def test_referral_not_paid_if_balance_below_200(self, message_mock, verify_mock):
        self.user1 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.user2 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), referral=self.user1.email)
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                'amount': 19900, # in kobo
            }
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        http_request.user = self.user2 
        response = views.VerifyTransaction.as_view()(http_request)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.account_balance, 0)

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
    def test_referral_not_paid_twice(self, message_mock, verify_mock):
        self.user1 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.user2 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), referral=self.user1.email, referral_status="paid")
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                'amount': 20000, # in kobo
            }
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        http_request.user = self.user2 
        response = views.VerifyTransaction.as_view()(http_request)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.account_balance, 0)

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
    def test_incorrect_referral_email_is_ignored(self, message_mock, verify_mock):
        self.user1 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.user2 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), referral=fake.email())
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                'amount': 30000, # in kobo
            }
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        http_request.user = self.user2 
        response = views.VerifyTransaction.as_view()(http_request)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.account_balance, 0)

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
    def test_no_referral_email_is_ignored(self, message_mock, verify_mock):
        self.user2 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                'amount': 30000, # in kobo
            }
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        http_request.user = self.user2 
        response = views.VerifyTransaction.as_view()(http_request)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
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
        order = self.ride.request.order_of_request
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        message = message_mock.call_args_list[0][0][2]

        self.assertEqual(message, "Verification successful")

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
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
        order = self.ride.request.order_of_request
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        response.client = Client()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
    def test_message_if_status_is_false(self, message_mock, verify_mock):
        verify_json = {
            "status": False,
            "message": "Transaction reference not recognized",
            "data": {}
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443")
        order = self.ride.request.order_of_request
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        message = message_mock.call_args_list[0][0][2]

        self.assertEqual(message, "Transaction reference not recognized")

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
    def test_redirect_if_status_is_false(self, message_mock, verify_mock):
        verify_json = {
            "status": False,
            "message": "Transaction reference not recognized",
            "data": {}
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/?reference=kshfhso3443", follow=False)
        order = self.ride.request.order_of_request
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        response.client = Client()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('fund_account'))

    
    @patch('main.views.messages.add_message')
    def test_message_if_reference_not_in_request_GET(self, message_mock):
        message_mock.return_value = Mock()
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/")
        order = self.ride.request.order_of_request
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        message = message_mock.call_args_list[0][0][2]

        self.assertEqual(message, "Improperly configured. No reference in verify. Please try again. If this continues, contact Dot360s")

    @patch('main.paystack_api.requests.get')
    @patch('main.views.messages.add_message')
    def test_redirect_if_reference_not_in_request_GET(self, message_mock, verify_mock):
        verify_json = {
            "status": False,
            "message": "Transaction reference not recognized",
            "data": {}
        }
        message_mock.return_value = Mock()
        verify_mock.return_value.json.return_value = verify_json
        http_request = RequestFactory().get("http://localhost:8080/verify-transaction/", follow=False)
        order = self.ride.request.order_of_request
        order.accepted = True
        order.save()
        order_accepted.send(sender=Order, Order=order, Driver=self.driver)

        http_request.user = self.passenger 
        response = views.VerifyTransaction.as_view()(http_request)
        response.client = Client()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('fund_account'))


class TestRequestListView(TestCase):
    def setUp(self):
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.http_request = RequestFactory().get(reverse('order_list'))     
        self.http_request.user = self.passenger
        self.response = views.RequestListView.as_view()(self.http_request)

    def test_get_queryset(self):
        request_queryset = Request.objects.filter(passenger=self.http_request.user).order_by('-time')
        self.assertIsInstance(self.response.context_data, dict)
        self.assertEqual(
            list(self.response.context_data['requests']), list(request_queryset))

    def test_only_three_request_is_shown(self):
        for x in range(10):
            Request.objects.create(passenger=self.passenger, 
            from_address=fake.address(), to_address=fake.address(),
            request_vehicle_type='T', intercity=True,
            city = 1, no_of_passengers=3,
            load=True)
        response = views.RequestListView.as_view()(self.http_request)
        self.assertEqual(len(response.context_data['requests']), 5)


class TestOrderListView(TestCase):
    def setUp(self):
        driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = driver_user.driver
        driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = driver_user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        for self.request in range(2):
            self.request = Request.objects.create(driver=self.driver,passenger=self.passenger, 
            from_address=fake.address(), to_address=fake.address(),
            request_vehicle_type='T', intercity=True,
            city = 1, no_of_passengers=3,
            load=True)
            order = Order.objects.get(request=self.request)
            order.driver.add(self.driver) 
            order.save()
            order.accepted = True
            order.save()
            order_accepted.send(sender=Order, Order=order, Driver=self.driver)
            
        self.http_request = RequestFactory().get(reverse('order_list'))     
        self.http_request.user = driver_user        
        self.response = views.OrderListView.as_view()(self.http_request)

    def test_context_data_contains_the_orders(self):
        orders = []
        for order in list(Order.objects.all()):
            orders.insert(0, order)
        
        views.OrderListView.request = self.http_request
        self.assertEqual(list(views.OrderListView.get_queryset(views.OrderListView)), orders)

    def test_get_queryset(self):
        driver_order_queryset = Order.objects.filter(driver=self.driver).exclude(request__ride__status="cancelled").order_by('-time_posted')
        self.assertIsInstance(self.response.context_data, dict)
        self.assertEqual(
            list(self.response.context_data['orders']), list(driver_order_queryset))

    def test_current_order_is_correct_order(self):
        self.driver.status = 'BU'
        self.driver.save()
        current_order = Order.objects.filter(request__driver=self.http_request.user.driver).last()
        last_order = Order.objects.get(request=self.request)
        self.assertEqual(current_order, last_order)

    def test_current_order_in_context_data(self):
        self.driver.status = 'BU'
        self.driver.save()
        current_order = Order.objects.filter(request__driver=self.http_request.user.driver).last()
        self.assertIn(current_order, self.response.context_data.get('orders'))

    def test_current_order_in_context_data(self):
        self.driver.status = 'BU'
        self.driver.save()
        current_order = Order.objects.filter(request__driver=self.http_request.user.driver).last()
        self.assertIn(current_order, self.response.context_data.get('orders'))

    def test_current_order_not_in_context_data_for_not_busy_driver(self):
        self.driver.status = 'BU'
        self.driver.save()
        self.http_request.user = self.driver.user
        for order in Order.objects.all():
            order.request.driver = None 
            order.request.save()        
        self.response = views.OrderListView.as_view()(self.http_request)
        self.assertFalse(self.response.context_data.get('current_order'))

    def test_your_orders_in_context_data(self):
        orders = []
        for order in list(Order.objects.all()):
            orders.insert(0, order)
        print([ order for order in orders if order.accepted == True ])
        self.assertEqual(list(self.response.context_data.get('your_orders')), [ order for order in orders if order.accepted == True])

    # test that the number of the objects are what you expect and are not empty
    def test_new_orders_in_context_data(self):
        request = Request.objects.create(driver=self.driver,passenger=self.passenger, 
            from_address=fake.address(), to_address=fake.address(),
            request_vehicle_type='T', intercity=True,
            city = 1, no_of_passengers=3,
            load=True)
        orders = []
        for order in list(Order.objects.all()):
            orders.insert(0, order)
        response = views.OrderListView.as_view()(self.http_request)
        self.assertIn('new_orders', response.context_data)
        # self.assertEqual(list(response.context_data.get('new_orders')), [ order for order in orders if order.accepted == False ])


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
        order = self.request.order_of_request
        kwargs = {'slug': order.slug}
        self.http_request = RequestFactory().get(reverse('take_order', kwargs=kwargs))
        self.http_request.user = self.driver_user
        self.response = views.TakeOrder.as_view()(self.http_request, **kwargs)
        order.refresh_from_db()
        self.assertTrue(order.accepted)

    def test_fetches_correct_order(self):
        request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        order = request.order_of_request
        kwargs={'slug': order.slug}
        http_request = RequestFactory().get(reverse('take_order', kwargs=kwargs))
        http_request.user = self.driver_user
        response = views.TakeOrder.as_view()(http_request, **kwargs)

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
        
    @patch('main.paystack_api.requests.get')
    @patch('main.paystack_api.requests.post')    
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
        http_request = RequestFactory().post(reverse('fund_account'), data={'amount': 27000})
        http_request.user = self.passenger
        response = views.FundAccount.as_view()(http_request)
        self.passenger.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, auth_json['data'].get('authorization_url'))

    @patch("main.views.messages.add_message")
    def test_error_message_was_printed_out(self, message_mock):
        message_mock.return_value = Mock()
        http_request = RequestFactory().post(reverse('fund_account'), data={'amount': 27000})
        http_request.user = self.passenger
        response = views.FundAccount.as_view()(http_request)
        
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, "An Error Occured, Paystack cannot be reached at this time")

    @patch("main.views.messages.add_message")
    def test_form_is_rendered_to_response_if_auth_response_is_none(self, message_mock):
        message_mock.return_value = Mock()
        http_request = RequestFactory().post(reverse('fund_account'), data={'amount': 27000})
        http_request.user = self.passenger
        response = views.FundAccount.as_view()(http_request)
        
        self.assertEqual(response.context_data['form'].changed_data, ['amount'])
 

class TestOngoingOrderViewPaid(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), account_balance=300.00)
        self.old_balance = self.passenger.account_balance
        self.request = Request.objects.create(driver=self.driver,passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.ride = Ride.objects.get(request=self.request)
        self.ride.status = "waiting"
        self.ride.payment_status = "card"
        self.ride.save()
        self.order = Order.objects.filter(request=self.request).first()
        kwargs = {'slug': self.order.slug}
        http_request = RequestFactory().get(reverse('ongoing_order', kwargs=kwargs))
        http_request.user = self.driver.user
        self.response = views.OngoingOrder.as_view()(http_request, **kwargs)

    def test_account_not_charged_if_ride_is_paid(self):
        self.passenger.refresh_from_db()
        self.assertEqual(self.passenger.account_balance, self.old_balance)

class TestOngoingOrderViewUnpaid(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), account_balance=300.00)
        self.old_balance = self.passenger.account_balance
        self.request = Request.objects.create(driver=self.driver,passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.ride = Ride.objects.get(request=self.request)
        self.ride.status = 2
        self.order = Order.objects.filter(request=self.request).first()
        kwargs = {'slug': self.order.slug}
        http_request = RequestFactory().get(reverse('ongoing_order', kwargs=kwargs))
        http_request.user = self.driver.user
        self.response = views.OngoingOrder.as_view()(http_request, **kwargs)

    def test_ride_status_has_been_changed(self):
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, "ongoing")

    def test_ride_payment_status_is_changed_to_paid(self):
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.payment_status, "paid")

    def test_ride_price_has_been_removed_from_balance(self):
        self.passenger.refresh_from_db()
        self.assertEqual(self.passenger.account_balance, self.old_balance -  self.ride.price)

class TestVerifyCompletedView(TestCase):
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
        http_request = RequestFactory().get(reverse('verify_completed', kwargs=kwargs))
        http_request.user = self.driver.user
        self.response = views.VerifyCompleted.as_view()(http_request, **kwargs)

    def test_ride_status_has_been_changed_to_completed(self):
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, "completed")

    def test_driver_is_now_set_as_avaliable(self):
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.status, 'AV')

class TestRequestAnotherDriver(TestCase):
    def setUp(self):
        user1 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver1 = user1.driver
        user2 = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver2 = user2.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(driver=self.driver1,passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.order = Order.objects.filter(request=self.request).first()
        self.order.accepted=True
        self.order.save()
        self.order.driver.add(self.driver1)
        self.order.driver.add(self.driver2)
        self.order.accepted = True
        self.order.request.driver = self.driver1
        kwargs = {'slug': self.order.slug}
        http_request = RequestFactory().get(reverse('another_driver', kwargs=kwargs))
        http_request.user = self.passenger
        self.response = views.AnotherDriver.as_view()(http_request, **kwargs)
        self.order.refresh_from_db()    

    def test_not_accepted_for_order_after_another_driver_view(self):
        self.assertFalse(self.order.accepted)
    
    def test_no_driver_for_order_after_another_driver_view(self):
        self.assertFalse(self.order.request.driver)
    
    def test_driver1_is_removed_from_drivers(self):
        self.request.refresh_from_db()
        self.assertFalse(Order.objects.filter(driver=self.driver1).first())

    def test_driver2_remains_in_drivers(self):
        self.request.refresh_from_db()
        self.assertTrue(Order.objects.filter(driver=self.driver2).first())
    
    def test_redirect(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('unaccepted_request'))


class TestChangeDriverStatus(TestCase):
    def setUp(self):
        self.user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = self.user.driver
        
    def test_status_changes_from_AV_to_NA(self):
        self.driver.status = 'AV'
        http_request = RequestFactory().get(reverse('change_status'), data={'next': reverse('home')})
        
        http_request.user = self.user
        self.response = views.ChangeDriverStatus.as_view()(http_request)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.status, 'NA')

    def test_status_changes_from_NA_to_AV(self):
        self.driver.status = 'NA'
        http_request = RequestFactory().get(reverse('change_status'), data={'next': reverse('home')})
        http_request.user = self.user
        self.response = views.ChangeDriverStatus.as_view()(http_request)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.status, 'AV')

    @patch('main.views.messages.add_message')
    def test_status_message_for_BU(self, message_mock):
        message_mock.return_value = Mock()
        self.driver.status = 'BU'
        http_request = RequestFactory().get(reverse('change_status'), data={'next': reverse('home')})
        http_request.user = self.user
        self.response = views.ChangeDriverStatus.as_view()(http_request)
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, "you are busy now, complete your current ride to change your status")


class TestWithdrawalListView(TestCase):
    def setUp(self):
        self.user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.http_request = RequestFactory().get(reverse('withdrawal_list'))     
        self.http_request.user = self.user        
        self.response = views.WithdrawalList.as_view()(self.http_request)

    def test_get_queryset(self):
        queryset = Withdrawal.objects.filter(user=self.user)
        self.assertIsInstance(self.response.context_data, dict)
        self.assertEqual(
            list(self.response.context_data['withdrawals']), list(queryset))



class TestHistoryListView(TestCase):
    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = self.driver_user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())
        self.http_request = RequestFactory().get(reverse('history'))     
        
    def test_get_queryset_if_driver(self):
        self.http_request.user = self.driver_user        
        self.response = views.HistoryListView.as_view()(self.http_request)
        queryset = Request.objects.filter(driver__user=self.http_request.user) 
        self.assertIsInstance(self.response.context_data, dict)
        self.assertEqual(
            list(self.response.context_data['requests']), list(queryset))

    def test_get_queryset_if_passenger(self):
        self.http_request.user = self.passenger        
        self.response = views.HistoryListView.as_view()(self.http_request)
        queryset = Request.objects.filter(passenger=self.http_request.user) 
        self.assertIsInstance(self.response.context_data, dict)
        self.assertEqual(
            list(self.response.context_data['requests']), list(queryset))


class TestWithdrawalCreateView(TestCase):
    def setUp(self): 
        self.user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), account_balance=3000)
        self.data = {
            'name': fake.name(),
            'amount': 2000,
            'account_no': 23243434343,
            'bank': 'GT Bank', 
            'reason': fake.text()
        }
        self.http_request = RequestFactory().post('create_withdrawal', data=self.data)
        self.http_request.user = self.user 
        response = views.WithdrawalCreateView.as_view()(self.http_request)
        self.withdrawal = Withdrawal.objects.filter(reason=self.data.get('reason')).first()

    def test_withdrawal_request_is_created(self):
        self.assertTrue(self.withdrawal)

    def test_name_is_in_initial(self):
        views.WithdrawalCreateView.request = self.http_request
        self.assertEqual(views.WithdrawalCreateView.get_initial(views.WithdrawalCreateView).get('name', ''), self.user.get_full_name())

    def test_bank_is_in_initial(self):
        Withdrawal.objects.create(user=self.user, amount=2000, account_no=3324323333, bank="GT Bank", reason=fake.text())
        views.WithdrawalCreateView.request = self.http_request
        self.assertEqual(views.WithdrawalCreateView.get_initial(views.WithdrawalCreateView).get('bank', ''), "GT Bank")

    def test_bank_is_not_in_initial_if_first_withdrawal(self):
        Withdrawal.objects.all().delete()
        views.WithdrawalCreateView.request = self.http_request
        self.assertFalse(views.WithdrawalCreateView.get_initial(views.WithdrawalCreateView).get('bank'))

    def test_account_no_is_in_initial(self):
        Withdrawal.objects.create(user=self.user, amount=2000, account_no=3324323333, bank="GT Bank", reason=fake.text())
        views.WithdrawalCreateView.request = self.http_request
        self.assertEqual(views.WithdrawalCreateView.get_initial(views.WithdrawalCreateView).get('account_no', ''), 3324323333)    

    def test_account_no_is_not_in_initial_if_first_withdrawal(self):
        Withdrawal.objects.all().delete()
        views.WithdrawalCreateView.request = self.http_request
        self.assertFalse(views.WithdrawalCreateView.get_initial(views.WithdrawalCreateView).get('account_no'))

    def test_user_is_saved_in_withdrawal(self):
        self.assertEqual(self.withdrawal.user, self.user)

    @patch('main.views.messages.add_message')
    def test_message_for_invalid_amount(self, message_mock):
        message_mock.return_value = Mock()
        self.user.account_balance = 1000
        self.user.save()
        self.data = {
            'name': fake.name(),
            'amount': 2000,
            'account_no': 23243434343,
            'bank': 'GT Bank', 
            'reason': fake.text()
        }
        self.http_request = RequestFactory().post('create_withdrawal', data=self.data)
        self.http_request.user = self.user 
        response = views.WithdrawalCreateView.as_view()(self.http_request)
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, f"Insufficient Balance. Your account balance is {self.user.account_balance} NGN")

    @patch('main.views.messages.add_message')
    def test_invalid_form_returns_with_false_data(self, message_mock):
        message_mock.return_value = Mock()
        self.user.account_balance = 1000
        self.user.save()
        self.data = {
            'name': fake.name(),
            'amount': 2000,
            'account_no': 23243434343,
            'bank': 'GT Bank', 
            'reason': fake.text()
        }
        self.http_request = RequestFactory().post('create_withdrawal', data=self.data)
        self.http_request.user = self.user 
        response = views.WithdrawalCreateView.as_view()(self.http_request)
        self.assertEqual(response.context_data.get('form').cleaned_data, self.data)

    @patch('main.views.messages.add_message')
    def test_redirect_if_form_valid(self, message_mock):
        message_mock.return_value = Mock()
        self.data = {
            'name': fake.name(),
            'amount': 2000,
            'account_no': 23243434343,
            'bank': 'GT Bank', 
            'reason': fake.text()
        }
        self.http_request = RequestFactory().post('create_withdrawal', data=self.data)
        self.http_request.user = self.user 
        response = views.WithdrawalCreateView.as_view()(self.http_request)
        self.withdrawal = Withdrawal.objects.filter(reason=self.data.get('reason')).first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('withdrawal_detail', kwargs={'pk': self.withdrawal.pk}))
