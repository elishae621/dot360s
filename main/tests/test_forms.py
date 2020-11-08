from django.test import TestCase
from main.forms import RequestForm, FundAccountForm
from user.models import User, Driver, Vehicle
from faker import Faker

fake = Faker()


class TestRequestFormErrors(TestCase):
    def setUp(self):
        self.data = {
            'from_address': fake.text(max_nb_chars=70), 
            'to_address': fake.text(max_nb_chars=70), 
            'city': fake.random_element(elements=Driver.City.values),
            'request_vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type),
            'intercity': fake.random_element(elements=[False]), 
            'no_of_passengers': fake.random_int(min=1, max=20), 
            'load': fake.random_element(elements=[False, True]), 
            'time': fake.date_time()
        }
        self.form = RequestForm(data=self.data)
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = Driver.objects.filter(user=user).first()
        self.driver.city = self.data.get('city')

    def test_error_message_if_no_driver_in_city(self):
        # for a city order than which a driver was created for
        city = self.data.get('city')
        while(city == self.data.get('city')):
            city = fake.random_element(elements=Driver.City.values)

        self.driver.location = city
        self.driver.status = 'AV'
        if self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = self.data.get('request_vehicle_type')
        self.driver.save()
        
        print(self.form.errors)
        self.assertEqual(self.form.errors.get('city')[0], "We are coming to your city soon. We appologize for any inconviences")

    def test_error_message_if_no_driver_for_intercity_type(self):
        # no driver in the city runs the intercity type chosen
        self.driver.location = self.data.get('city')
        self.driver.status = 'AV'
        if not self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = self.data.get('request_vehicle_type')
        self.driver.save()
        
        self.assertEqual(self.form.errors.get('intercity')[0], "No driver offers this journey type in your city")

    def test_error_message_if_no_driver_with_vehicle_type(self):
        # driver is in city but not of the vehicle_type
        vehicle_type = self.data.get('request_vehicle_type')
        while(vehicle_type == self.data.get('request_vehicle_type')):
            vehicle_type = fake.random_element(elements=Vehicle.Vehicle_type)
        self.driver.location = self.data.get('city')
        self.driver.status = 'AV'
        if self.data.get('intercity'):
            self.driver.journey_type = ['OUT']
        else:
            self.driver.journey_type = ['IN']
        self.driver.vehicle.vehicle_type = vehicle_type
        self.driver.save()
        
        self.assertEqual(self.form.errors.get('request_vehicle_type')[0], "None of our Drivers with this vehicle type in your city are avaliable at this time. Please try again at another time")


class TestRequestForm(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = Driver.objects.filter(user=user).first()
        self.driver.location = fake.random_element(elements=Driver.City.values)
        self.driver.vehicle.vehicle_type = fake.random_element(elements=Vehicle.Vehicle_type.values)
        self.driver.journey_type = ['IN', 'OUT']
        self.driver.status = 'AV'
        self.driver.save()
        self.driver.vehicle.save()
        self.data = {
            'from_address': fake.text(max_nb_chars=70), 
            'to_address': fake.text(max_nb_chars=70), 
            'city': self.driver.location,
            'request_vehicle_type': self.driver.vehicle.vehicle_type,
            'intercity': fake.random_element(elements=[True, False]), 
            'no_of_passengers': fake.random_int(min=1, max=20), 
            'load': fake.random_element(elements=[False, True]), 
            'time': fake.date_time(),
            'payment_method': fake.random_element(elements=["cash"])
        }
        self.form = RequestForm(data=self.data)
        
    def test_form_is_valid(self):
        print(self.form.errors)
        self.assertTrue(self.form.is_valid())

class TestFundAccountForm(TestCase):
    def setUp(self):
        self.data = {'amount': fake.random_int(min=100, max=3000)}
        self.form = FundAccountForm(data=self.data)

    def test_form_is_valid(self):
        print(self.form.errors)
        self.assertTrue(self.form.is_valid())

    def test_amount_is_changed_to_kobo(self):
        self.form.is_valid()
        self.assertEqual(self.data.get
        ('amount') * 100, self.form.cleaned_data.get('amount'))