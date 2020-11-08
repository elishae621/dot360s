from django import forms
from user.models import Driver, User, Vehicle


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'password', 'password2', 'phone')


class DriverProfileUpdateForm(forms.ModelForm):
    location = forms.ChoiceField(choices=Driver.City.choices, widget=forms.RadioSelect())
    status = forms.ChoiceField(choices=Driver.Driver_status.choices, widget=forms.RadioSelect())
    journey_type = forms.MultipleChoiceField(choices=Driver.Journey_type.choices, widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Driver
        fields = ['image', 'location',
                  'status', 'journey_type']
        
class VehicleUpdateForm(forms.ModelForm):
    vehicle_type = forms.ChoiceField(choices=Vehicle.Vehicle_type.choices, widget=forms.RadioSelect())

    class Meta:
        model = Vehicle
        fields = ['name', 'plate_number', 'capacity', 'color', 'vehicle_type']


