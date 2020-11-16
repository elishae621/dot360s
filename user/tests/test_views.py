from django.http.response import Http404
from django.core.exceptions import PermissionDenied, SuspiciousOperation, TooManyFieldsSent 
from django.test import SimpleTestCase, TestCase, override_settings, RequestFactory
from user.models import User, Driver, Vehicle
from django.urls import include, path 
from django.template.loader import render_to_string
from django.urls import reverse 
from user import views
from faker import Faker 
fake = Faker()



def suspicious_operation_view(request):
    raise SuspiciousOperation

def permission_denied_view(request):
    raise PermissionDenied 

def page_not_found_view(request):
    raise Http404

def uncaught_exception_view(request):
    raise TooManyFieldsSent


urlpatterns = [
    path('400/', suspicious_operation_view),
    path('403/', permission_denied_view),
    path('404/', page_not_found_view),
    path('500/', uncaught_exception_view),
    path('accounts/', include('allauth.urls')),
    path('', include('main.urls')),
    path('tellme/', include('tellme.urls')),
]

handler400 = 'user.views.error_400'
handler403 = 'user.views.error_403'
handler404 = 'user.views.error_404'
handler500 = 'user.views.error_500'

@override_settings(ROOT_URLCONF=__name__)
class CustomerErrorHandlerTests(SimpleTestCase):

    def test_template_for_400(self):
        response = self.client.get('/400/')
        with self.assertTemplateUsed(template_name='user/400.html'):
            render_to_string('user/400.html')

    def test_template_for_403(self):
        response = self.client.get('/403/')
        with self.assertTemplateUsed(template_name='user/403.html'):
            render_to_string('user/403.html')
    
    def test_template_for_404(self):
        response = self.client.get('/404/')
        with self.assertTemplateUsed(template_name='user/404.html'):
            render_to_string('user/404.html')
    
    def test_template_for_500(self):
        response = self.client.get('/500/')
        with self.assertTemplateUsed(template_name='user/500.html'):
            render_to_string('user/500.html')
    

class TestDriverProfileUpdateView(TestCase):
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
            reverse('driver_profile_update'), self.data)
        self.request.user = self.driver_user
        self.response = views.driver_update_profile.as_view()(self.request)

    def test_success_url(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse('driver_profile_detail', kwargs={'pk': self.driver_user.id}))