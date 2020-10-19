from django import forms
from user.models import Driver, User, Vehicle
# from allauth.account.forms import SignupForm
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError


class UserRegistrationForm(forms.ModelForm):
    phone = PhoneNumberField()
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())


    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'password', 'password2', 'phone')

    def clean_password1(self):
        password = self.cleaned_data['password']
        password1 = self.cleaned_data['password1']
        if password1 is not password:
            raise ValidationError("Your two password do not match")
        return password1


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
