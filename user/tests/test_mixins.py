from django.test import TestCase, RequestFactory, Client
from user.mixins import Update_view
from user import views
from faker import Faker
import factory
from django.urls import reverse
from user.models import User, Driver, Vehicle
import pytest
from user.forms import  DriverProfileUpdateForm, VehicleUpdateForm
from phonenumber_field.phonenumber import PhoneNumber
from django.core.exceptions import PermissionDenied
from django.http import Http404



fake = Faker()
class TestMustBeDriverValidMixin(TestCase):
    def setUp(self):
        self.user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'))
        self.user.set_password(fake.password())

        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.driver = Driver.objects.filter(user=self.driver_user).first()
        self.driver.location= fake.random_int(min=1, max=len(Driver.CITIES))
        self.driver.status = fake.random_int(min=1, max=len(Driver.STATUS_CHOICES))
        self.driver.journey_type = fake.random_elements(elements=Driver.JOURNEY_CHOICES, unique=True)

    
    def test_accessible_for_driver(self):
        request = RequestFactory().get(reverse('driver_profile_update'))
        request.user = self.driver_user
        response = views.driver_update_profile.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_forbidden_for_not_driver(self):
        request = RequestFactory().get(reverse('driver_profile_update'))
        request.user = self.user

        with self.assertRaises(PermissionDenied):
            response = views.driver_update_profile.as_view()(request)


class TestUpdateViewMixin(TestCase):

    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.driver = Driver.objects.filter(user=self.driver_user).first()
        self.driver.location= 1
        self.driver.status = 1
        self.driver.journey_type = [1,]
        self.driver.vehicle.name = "old name"
        self.driver.vehicle.plate_number = "old plate number"
        self.driver.vehicle.color = "old color"
        self.driver.vehicle.capacity = 1
        self.driver.vehicle.vehicle_type = 1
        self.data = {
            'location': 2,
            'status': 2,
            'journey_type': [1,2],
            'name': 'new name',
            'plate number': 'new plate number',
            'color': 'new color',
            'capacity': 2,
            'vehicle_type': 2
        }
        self.request = RequestFactory().post(
            reverse('driver_profile_update'), self.data)
        self.request.user = self.driver_user
        self.response = views.driver_update_profile.as_view()(self.request)
        self.driver.refresh_from_db()

    def test_success_url_redirect(self):

        self.assertEqual(self.response.status_code, 302)
        self.assertRedirects(self.response, reverse(
            'driver_profile_update'), fetch_redirect_response=False)

    def test_location_updated(self):
        self.assertEqual(self.driver.location, self.data.get('location'))

    def test_status_updated(self):
        self.assertEqual(self.driver.status, self.data.get('status'))

    def test_journey_type_updated(self):
        self.assertEqual(self.driver.journey_type[0], str(self.data.get('journey_type')[0]))
        self.assertEqual(self.driver.journey_type[1], str(self.data.get('journey_type')[1]))


    def test_vehicle_name_updated(self):
        self.assertEqual(self.driver.vehicle.name, self.data.get('name'))
    
    def test_vehicle_plate_number_updated(self):
        self.assertEqual(self.driver.vehicle.plate_number, self.data.get('plate_number'))

    def test_vehicle_color_updated(self):
        self.assertEqual(self.driver.vehicle.color, self.data.get('color'))

    def test_vehicle_capacity_updated(self):
        self.assertEqual(self.driver.vehicle.capacity, self.data.get('capacity'))

    def test_vehicle_vehicle_type(self):
        self.assertEqual(self.driver.vehicle.vehicle_type, self.data.get('vehicle_type'))

class TestUpdateFormInvalid(TestCase):

    def setUp(self):
        self.fake = Faker()
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.driver = Driver.objects.filter(user=self.driver_user).first()
        self.driver.location= 1
        self.driver.status = 1
        self.driver.journey_type = [1,]
        self.driver.vehicle.name = "old name"
        self.driver.vehicle.plate_number = "old plate number"
        self.driver.vehicle.color = "old color"
        self.driver.vehicle.capacity = 1
        self.driver.vehicle.vehicle_type = 1
        self.data = {
            'location': 'invalid location',
            'status': 'invalid status',
            'journey_type': 'invalid',
            'name': 23,
            'plate number': 23,
            'color': 23,
            'capacity': 'invalid capacity',
            'vehicle_type': 'invalid type'
        }
        self.request = RequestFactory().post(
            reverse('driver_profile_update'), self.data)
        self.request.user = self.driver_user
        self.response = views.driver_update_profile.as_view()(self.request)
        self.driver.refresh_from_db()

    def test_uForm_invalid(self):
        self.assertFalse(self.response.context_data['dForm'].is_valid())

    def test_pForm_invalid(self):
        self.assertFalse(self.response.context_data['vForm'].is_valid())


class TestGetUpdateForm(TestCase):

    def setUp(self):
        self.fake = Faker()
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.request = RequestFactory().get(reverse('driver_profile_update'))
        self.request.user = self.driver_user
        self.response = views.driver_update_profile.as_view()(self.request)
        self.driver_user.refresh_from_db()

    def test_dForm_is_in_context(self):
        self.assertIn('dForm', self.response.context_data)

    def test_vForm_is_in_context(self):
        self.assertIn('vForm', self.response.context_data)


class TestGetLoginedUserMixin(TestCase):
    def setUp(self):
        pass
        
    def test_get_correct_driver(self):
        driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        driver_user.set_password(fake.password())
        request = RequestFactory().get(reverse('driver_profile_detail', kwargs={'pk': driver_user.pk}))
        request.user = driver_user
        response = views.profile_detail_view.as_view()(request)
        self.assertEqual(
            views.profile_detail_view.get_queryset(views.profile_detail_view)[0], Driver.objects.filter(user=driver_user).first())

    def test_driver_not_found(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'))
        user.set_password(fake.password())
        request = RequestFactory().get(reverse('driver_profile_detail', kwargs={'pk': user.pk}))
        request.user = user
        with self.assertRaises(Http404):
            response = views.profile_detail_view.as_view()(request)
