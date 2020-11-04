from django.test import TestCase
from user.models import User, Driver, Vehicle, Request, Ride, Order
from faker import Faker
from user.signals import order_accepted

fake = Faker()

class TestCreateDriver(TestCase):
    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())

    def test_driver_if_is_driver_true(self):
        self.assertTrue(Driver.objects.filter(user=self.driver_user).first())

    def test_driver_is_created_once(self):
        self.assertTrue(len(Driver.objects.filter(user=self.driver_user)), 1)


class TestVechicleCreated(TestCase):
    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.driver = Driver.objects.filter(user=self.driver_user).first()

    def test_vehicle_is_created(self):
        self.assertTrue(Vehicle.objects.filter(owner=self.driver).first())

    def test_only_one_vehicle_is_created(self):
        self.assertEqual(len(Vehicle.objects.filter(owner=self.driver)), 1)


class TestCreateRide(TestCase):
    def setUp(self):
        self.user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'))
        self.user.set_password(fake.password())

        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.driver = Driver.objects.filter(user=self.driver_user).first()

        self.request = Request.objects.create(driver=self.driver, passenger=self.user, from_address=fake.text(), to_address=fake.text(), 
        city=fake.random_element(elements=Driver.City.values), no_of_passengers=fake.random_int(min=1, max=20), load=fake.random_element(elements=[False, True]), time=fake.date_time())

    def test_ride_is_created(self):
        self.assertTrue(Ride.objects.filter(request=self.request).first())

    def test_only_one_ride_is_created(self):
        self.assertEqual(len(Ride.objects.filter(request=self.request)), 1)
    


class TestCreateOrder(TestCase):
    def setUp(self):
        self.user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'))
        self.user.set_password(fake.password())

        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.driver = Driver.objects.filter(user=self.driver_user).first()

        self.request = Request.objects.create(driver=self.driver, passenger=self.user, from_address=fake.text(), to_address=fake.text(), 
        city=fake.random_element(elements=Driver.City.values), no_of_passengers=fake.random_int(min=1, max=20), load=fake.random_element(elements=[False, True]), time=fake.date_time())

    def test_order_is_created(self):
        self.assertTrue(Order.objects.filter(request=self.request).first())

    def test_only_one_order_is_created(self):
        self.assertEqual(len(Order.objects.filter(request=self.request)), 1)
    

class TestOrderAccepted(TestCase):
    def setUp(self):
        self.user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'))
        self.user.set_password(fake.password())

        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.driver = Driver.objects.filter(user=self.driver_user).first()

        self.request = Request.objects.create(passenger=self.user, from_address=fake.text(), to_address=fake.text(), 
        city=fake.random_element(elements=Driver.City.values), no_of_passengers=fake.random_int(min=1, max=20), load=fake.random_element(elements=[False, True]), time=fake.date_time())

        self.order = Order.objects.filter(request=self.request).first()

        self.order.accepted = True
        order_accepted.send(sender=Order, Order=self.order, Driver=self.driver)

    def test_that_driver_has_been_set_on_request(self):
        self.request.refresh_from_db()
        self.assertEqual(self.request.driver, self.driver)

    def test_that_ride_status_is_now_unpaid_and_confirmed(self):
        self.assertEqual(self.order.request.ride.status, "waiting")