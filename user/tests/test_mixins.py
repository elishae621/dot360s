from django.test import TestCase, RequestFactory
from user import views
from faker import Faker
from django.urls import reverse
from user.models import Driver, User, Vehicle
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
        self.driver.location= fake.random_element(elements=Driver.City.values)
        self.driver.status = fake.random_element(elements=Driver.Driver_status.values)
        self.driver.journey_type = fake.random_elements(elements=Driver.Journey_type.values, unique=True)

    
    def test_accessible_for_driver(self):
        request = RequestFactory().get(reverse('user:driver_update'))
        request.user = self.driver_user
        response = views.driver_update_profile.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_redirect_for_not_driver(self):
        request = RequestFactory().get(reverse('user:driver_update'))
        request.user = self.user
        response = views.driver_update_profile.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


class TestUpdateViewMixin(TestCase):

    def setUp(self):
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.driver = Driver.objects.filter(user=self.driver_user).first()
        self.driver.location = fake.random_element(elements=Driver.City.values)
        self.driver.status = fake.random_element(elements=Driver.Driver_status.values)
        self.driver.journey_type = fake.random_elements(elements=Driver.Journey_type.values, unique=True)
        self.driver.vehicle.name = "old name"
        self.driver.vehicle.plate_number = "old plate number"
        self.driver.vehicle.color = "old color"
        self.driver.vehicle.capacity = fake.random_int(min=1, max=20)
        self.driver.vehicle.vehicle_type = fake.random_element(elements=Vehicle.Vehicle_type.values)
        self.driver.save()
        self.driver.vehicle.save()
        self.data = {
            'location': fake.random_element(elements=Driver.City.values),
            'status': fake.random_element(elements=Driver.Driver_status.values),
            'journey_type': fake.random_elements(elements=Driver.Journey_type.values, unique=True),
            'name': 'new name',
            'plate number': 'new plate number',
            'color': 'new color',
            'capacity': fake.random_int(min=1, max=20),
            'vehicle_type': fake.random_element(elements=Vehicle.Vehicle_type.values)
        }
        self.request = RequestFactory().post(
            reverse('user:driver_update'), self.data)
        self.request.user = self.driver_user
        self.response = views.driver_update_profile.as_view()(self.request)
        self.driver.refresh_from_db()

    def test_location_updated(self):
        self.assertEqual(self.driver.location, self.data.get('location'))

    def test_status_updated(self):
        self.assertEqual(self.driver.status, self.data.get('status'))

    def test_journey_type_updated(self):
        self.assertEqual(self.driver.journey_type[0], str(self.data.get('journey_type')[0]))
        if len(self.driver.journey_type) == 2:
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

    def test_driver_completed_set_to_true(self):
        self.assertTrue(self.driver.completed)

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
            reverse('user:driver_update'), self.data)
        self.request.user = self.driver_user
        self.response = views.driver_update_profile.as_view()(self.request)
        self.driver.refresh_from_db()

    def test_uForm_invalid(self):
        self.assertFalse(self.response.context_data['dForm'].is_valid())

    def test_pForm_invalid(self):
        self.assertFalse(self.response.context_data['vForm'].is_valid())

    def test_no_of_errors_for_dForm(self):
        self.assertEqual(len(self.response.context_data['dForm'].errors), 3)

    def test_no_of_errors_for_vForm(self):
        self.assertEqual(len(self.response.context_data['vForm'].errors), 2)


class TestGetUpdateForm(TestCase):

    def setUp(self):
        self.fake = Faker()
        self.driver_user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'), 
        is_driver=True)
        self.driver_user.set_password(fake.password())
        self.request = RequestFactory().get(reverse('user:driver_update'))
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
        request = RequestFactory().get(reverse('user:driver_detail', kwargs={'pk': driver_user.pk}))
        request.user = driver_user
        response = views.profile_detail_view.as_view()(request)
        self.assertEqual(
            views.profile_detail_view.get_queryset(views.profile_detail_view)[0], Driver.objects.filter(user=driver_user).first())

    def test_driver_not_found(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(), lastname=fake.last_name(),
        phone=fake.numerify(text='080########'))
        user.set_password(fake.password())
        request = RequestFactory().get(reverse('user:driver_detail', kwargs={'pk': user.pk}))
        request.user = user
        with self.assertRaises(Http404):
            response = views.profile_detail_view.as_view()(request)