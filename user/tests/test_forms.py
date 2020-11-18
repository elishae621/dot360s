from django.test import TestCase
from user.forms import (
    RegistrationForm,
    DriverProfileUpdateForm,
    VehicleUpdateForm,
)
import factory
from user.models import Driver, Vehicle, User
from faker import Faker

fake = Faker()
password = fake.password()

class TestUserRegistrationForm(TestCase):

    def setUp(self):
        self.data = {
            'email': fake.email(),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'password': password,
            'password2': password,
            'date_of_birth': fake.date_of_birth(),
            'phone': fake.numerify(text='080########'),
            'referral': fake.email(),
        }
        self.form = RegistrationForm(data=self.data)

    def test_form_is_valid(self):
        print(self.form.errors)
        self.assertTrue(self.form.is_valid())

    

class TestDriverProfileUpdateForm(TestCase):
    def setUp(self):
        self.data = {
            'image': factory.django.ImageField(from_path=r"C:\Users\Elisha\Pictures\Screenshots\Screenshot (16).png", filename=r"\newimage", format="png"),
            'location': fake.random_element(elements=Driver.City.values),
            'status': fake.random_element(elements=Driver.Driver_status.values),
            'journey_type': fake.random_elements(elements=Driver.Journey_type.values, unique=True)
        }
        self.form = DriverProfileUpdateForm(data=self.data)

    def test_form_is_valid(self):
        self.assertTrue(self.form.is_valid())


class TestVehicleUpdateForm(TestCase):
    def setUp(self):
        self.data = {
            'name': fake.text(max_nb_chars=20),
            'plate_number': fake.bothify("???-###-???"),
            'capacity': fake.random_int(min=1, max=18),
            'color': fake.color_name(),
            'vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type.values)
        }
        self.form = VehicleUpdateForm(data=self.data)

    def test_form_is_valid(self):
        print(self.form.errors)
        self.assertTrue(self.form.is_valid())
