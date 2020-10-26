from django import forms
from user.models import Driver, User, Vehicle, Request
from django.core.exceptions import ValidationError


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

class RequestForm(forms.ModelForm):
    request_vehicle_type = forms.ChoiceField(choices=Vehicle.Vehicle_type.choices, widget=forms.RadioSelect(), label="Vehicle Type")
    city = forms.ChoiceField(choices=Driver.City.choices, widget=forms.RadioSelect())
    time = forms.DateTimeField(widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Request
        fields = ['from_address', 'to_address', 'city', 'intercity', 'request_vehicle_type', 'no_of_passengers', 'load', 'time']
        
    def clean_city(self):
        data = self.cleaned_data.get('city')
        list_of_drivers = Driver.objects.filter(location=data)
        if not list_of_drivers:
            raise ValidationError("We are coming to your city soon. We appologize for any inconviences")
        return data

    def clean_intercity(self):
        data = self.cleaned_data.get('intercity')
        list_of_out_drivers = []
        list_of_in_drivers = []
        valid_drivers = Driver.objects.filter(location=self.cleaned_data.get('city'))
        if valid_drivers:
            for driver in list(valid_drivers):
                if 'OUT' in driver.journey_type:
                    list_of_out_drivers.append(driver)
                if 'IN' in driver.journey_type:
                    list_of_in_drivers.append(driver)
        if data:
            list_of_drivers = list_of_out_drivers
        else:
            list_of_drivers = list_of_in_drivers
        if not list_of_drivers:
            raise ValidationError("No driver offers this journey type in your city")
        return data

    def clean_request_vehicle_type(self):
        data = self.cleaned_data.get('request_vehicle_type')
        list_of_drivers = Driver.objects.filter(location=self.cleaned_data.get('city'))
        list_of_drivers_with_vehicle = []
        if list_of_drivers:
            for driver in list(list_of_drivers):
                if driver.vehicle.vehicle_type == data:
                    list_of_drivers_with_vehicle.append(driver)
        if list_of_drivers_with_vehicle == []:
            raise ValidationError("None of our Drivers with this vehicle type in your city are avaliable at this time. Please try again at another time")
        return data

    # other methods only checks if drivers exist for the
    # the request data. this method gets the final list
    # of valid data with the cleaned data
    def clean(self):
        cleaned_data = super(RequestForm, self).clean()
        valid_drivers = list(Driver.objects.filter(location=self.cleaned_data.get('city')))
        list_of_out_drivers = []
        list_of_in_drivers = []
        for driver in valid_drivers:
            if 'OUT' in driver.journey_type:
                list_of_out_drivers.append(driver)
            if 'IN' in driver.journey_type:
                list_of_in_drivers.append(driver)
        if self.cleaned_data.get('intercity'):
            valid_drivers = list_of_out_drivers
        else:
            valid_drivers = list_of_in_drivers
        list_of_drivers_with_vehicle = []
        for driver in valid_drivers:
            if driver.vehicle.vehicle_type == self.cleaned_data.get('request_vehicle_type'):
                list_of_drivers_with_vehicle.append(driver)
        valid_drivers = list_of_drivers_with_vehicle
        cleaned_data['valid_drivers'] = valid_drivers
        return cleaned_data

    