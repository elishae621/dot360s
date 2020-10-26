from django.test import Client, RequestFactory, TestCase 
from user import views
from faker import Faker
from user.models import User, Driver, Vehicle, Request, Ride
from django.urls import reverse
import pytz
from random import randint
import math


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
        self.response = views.RequestView.as_view()(self.request)
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

    def test_driver_of_request_is_avaliable(self):
        self.assertEqual(self.request_created.driver.status, 'AV')

    def test_driver_of_request_is_in_same_city(self):
        self.assertEqual(self.request_created.driver.location, self.data.get('city'))

    def test_driver_of_request_uses_same_vehicle_type(self):
        self.assertEqual(self.request_created.driver.vehicle.vehicle_type, self.data.get('request_vehicle_type'))
    
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
        self.response = views.RequestView.as_view()(self.request)
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
        self.response = views.RequestView.as_view()(self.request)
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
        self.response = views.RequestView.as_view()(self.request)
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


class TestUpdateRequest(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.driver.vehicle.vehicle_type = 'B'
        self.driver.intercity = False
        self.driver.location = 2
        self.driver.save()
        self.driver.vehicle.save()
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(driver=self.driver,passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        
        self.old_ride = Ride.objects.filter(request=self.request).first()
        self.old_ride.price = 200.00
        self.old_ride.save()
        self.data = {
            "from_address": fake.address(),
            "to_address": fake.address(),
            "request_vehicle_type": 'B',
            "intercity": False,
            "city": 2,
            "no_of_passengers": 7,
            "load": False,
            "time": fake.date_time(tzinfo=pytz.timezone('Africa/Lagos'))
        }
        self.http_request = RequestFactory().post(reverse('update_request'), data=self.data)
        self.http_request.user = self.passenger
        self.response = views.RequestUpdate.as_view()(self.http_request)
        self.request.refresh_from_db()
        self.new_ride = Ride.objects.filter(request=self.request).first()
        

    def test_old_ride_is_deleted(self):
        old_ride = Ride.objects.filter(request=self.request).first()
        self.assertNotEqual(old_ride.price, 200.00)

    def test_only_one_ride_exit(self):
        self.assertEqual(len(Ride.objects.filter(request=self.request)), 1)

    def test_new_ride_is_created(self):
        self.assertEqual(self.new_ride.price, 100.00)

    def test_new_ride_default_to_waiting_for_confirmation(self):
        # to differentiate the new ride from the old
        self.assertEqual(self.new_ride.price, 100.00)
        self.assertEqual(self.new_ride.status, 'WC')

    def test_from_address_updated(self):
        self.assertEqual(self.request.from_address, self.data.get('from_address'))

    def test_to_address_updated(self):
        self.assertEqual(self.request.to_address, self.data.get('to_address'))

    def test_vehicle_type_updated(self):
        self.assertEqual(self.request.request_vehicle_type, self.data.get('request_vehicle_type'))

    def test_intercity_updated(self):
        self.assertEqual(self.request.intercity, self.data.get('intercity'))

    def test_load_updated(self):
        self.assertEqual(self.request.load, self.data.get('load'))

    def test_time_updated(self):
        self.assertEqual(self.request.time, self.data.get('time'))

    def test_city_updated(self):
        self.assertEqual(self.request.city, self.data.get('city'))

    def test_no_of_passengers_updated(self):
        self.assertEqual(self.request.no_of_passengers, self.data.get('no_of_passengers'))

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
        http_request = RequestFactory().post(reverse('update_request'), data=self.data)
        http_request.user = self.passenger
        response = views.RequestUpdate.as_view()(http_request)
        response.client = Client()

        self.assertRedirects(response, reverse('no_avaliable_driver'))


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
        self.assertRedirects(self.response, reverse('home'))


class TestPriceConfirmation(TestCase):
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
        self.http_request = RequestFactory().get(reverse('price_confirmation'))
        self.http_request.user = self.passenger
        self.response = views.PriceConfirmation.as_view()(self.http_request)

    def test_correct_ride_in_get_context_data(self):
        self.assertEqual(self.response.context_data.get('ride', None), self.ride)


class TestVerifyTransaction(TestCase):
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
        self.random_number_for_ref = randint(0, 9999999999)
        self.http_request = RequestFactory().get(reverse('verify_transaction', 
            kwargs={'reference': self.ride.request.driver.user.firstname + str(self.random_number_for_ref)}))
        self.http_request.user = self.passenger
        self.response = views.VerifyTransaction.as_view()(self.http_request)

    def test_reference_is_saved_if_args_args(self):
        self.assertEqual(self.ride.reference, 
            self.ride.request.driver.user.firstname + str(self.random_number_for_ref))

    def test_refernce_not_changed_if_not_in_args(self):
        self.http_request = RequestFactory().get(reverse('verify_transaction', 
            kwargs={'reference': self.ride.request.driver.user.firstname + str(self.random_number_for_ref)}))
        self.response = views.VerifyTransaction.as_view()(self.http_request)

        self.assertEqual(self.ride.reference, "not yet paid")