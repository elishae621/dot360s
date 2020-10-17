from django import forms
from user.models import Driver, User, Vehicle
# from allauth.account.forms import SignupForm
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.forms import UserCreationForm


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    firstname = forms.CharField(required=True)
    lastname = forms.CharField(required=False)
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['firstname'].widget.attrs['placeholder'] = 'firstname'
        self.fields['lastname'].widget.attrs['placeholder'] = 'lastname'
        self.fields['phone'].widget.attrs['placeholder'] = 'Phone Number'


class DriverProfileUpdateForm(forms.ModelForm):
    location = forms.ChoiceField(choices=Driver.CITIES)
    status = forms.ChoiceField(choices=Driver.STATUS_CHOICES)
    journey_type = forms.MultipleChoiceField(choices=Driver.JOURNEY_CHOICES)

    class Meta:
        model = Driver
        fields = ['image', 'location',
                  'status', 'journey_type']


class VehicleUpdateForm(forms.ModelForm):
    vehicle_type = forms.ChoiceField(choices=Vehicle.VEHICLE_CHOICE)

    class Meta:
        model = Vehicle
        fields = ['name', 'plate_number', 'capacity', 'color', 'vehicle_type']
