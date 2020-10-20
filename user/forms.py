from django import forms
from user.models import Driver, User, Vehicle, Request, Ride
# from allauth.account.forms import SignupForm
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget


class UserRegistrationForm(forms.ModelForm):
    phone = forms.CharField(widget=PhoneNumberInternationalFallbackWidget(region='NG'))
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())


    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'password', 'password2', 'phone')


class DriverProfileUpdateForm(forms.ModelForm):
    location = forms.ChoiceField(choices=Driver.CITIES, widget=forms.RadioSelect())
    status = forms.ChoiceField(choices=Driver.STATUS_CHOICES, widget=forms.RadioSelect())
    journey_type = forms.MultipleChoiceField(choices=Driver.JOURNEY_CHOICES, widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Driver
        fields = ['image', 'location',
                  'status', 'journey_type']
        
class VehicleUpdateForm(forms.ModelForm):
    vehicle_type = forms.ChoiceField(choices=Vehicle.VEHICLE_CHOICE, widget=forms.RadioSelect())

    class Meta:
        model = Vehicle
        fields = ['name', 'plate_number', 'capacity', 'color', 'vehicle_type']

class RequestForm(forms.ModelForm):
    city = forms.ChoiceField(choices=Vehicle.VEHICLE_CHOICE, widget=forms.RadioSelect())
    time = forms.DateTimeField(widget=forms.SplitDateTimeWidget)

    class Meta:
        model = Request
        fields = ['from_address', 'to_address', 'city', 'no_of_passengers', 'load', 'time']