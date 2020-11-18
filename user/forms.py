from django import forms
from user.models import Driver, User, Vehicle


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput())
    phone = forms.CharField(label="Phone Number")
    referral = forms.EmailField(help_text="Enter the email of the user that introduced you to dot360s", required=False)
    

    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'password', 'password2', 'date_of_birth', 'phone', 'referral')
        widgets = {
            'date_of_birth': forms.DateInput(format='%d-%m-%Y', attrs={'class': 'datefield'}),
        }

class LoginForm(forms.Form):
    email = forms.EmailField() 
    password = forms.CharField(widget=forms.PasswordInput())


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


