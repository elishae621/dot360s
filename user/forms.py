from django import forms
from user.models import Driver, User, Vehicle
# from allauth.account.forms import SignupForm
from phonenumber_field.modelfields import PhoneNumberField


class UserRegistrationForm(forms.ModelForm):
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'password', 'phone')


class DriverProfileUpdateForm(forms.ModelForm):
    location = forms.ChoiceField(choices=Driver.CITIES)
    status = forms.ChoiceField(choices=Driver.STATUS_CHOICES)
    journey_type = forms.MultipleChoiceField(choices=Driver.JOURNEY_CHOICES)

    class Meta:
        model = Driver
        fields = ['image', 'location',
                  'status', 'journey_type']

    def save(self, form):
        super(DriverProfileUpdateForm, self).save(form)
        pass

class VehicleUpdateForm(forms.ModelForm):
    vehicle_type = forms.ChoiceField(choices=Vehicle.VEHICLE_CHOICE)

    class Meta:
        model = Vehicle
        fields = ['name', 'plate_number', 'capacity', 'color', 'vehicle_type']
