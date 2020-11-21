from django.core.exceptions import ValidationError
from user.models import User, Driver, Vehicle

from main.models import Request, Ride, Order, Withdrawal

from rest_framework import serializers
from rest_framework import fields 

from multiselectfield import MultiSelectField

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'email', 'firstname', 'lastname', 'phone', 'account_balance', 'date_of_birth', 'referral', 'referral_status', 'is_staff', 'is_active', 'is_driver',]


class DriverSerializer(serializers.ModelSerializer):

    class Meta:
        model = Driver
        fields = ['pk', 'user', 'image', 'location', 'status', 'journey_type', 'completed',]


class DriverUpdateSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=False, read_only=True)
    user = serializers.IntegerField(required=False, read_only=True)
    image = serializers.ImageField(required=False)
    location = serializers.ChoiceField(choices=Driver.City.choices)
    status = serializers.ChoiceField(choices=Driver.Driver_status.choices)
    journey_type = serializers.MultipleChoiceField(choices=Driver.Journey_type.choices)
    completed = serializers.BooleanField(default=False, required=False, read_only=True)

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image) 
        instance.location = validated_data.get('location', instance.location)
        instance.status = validated_data.get('status', instance.status)
        instance.journey_type = validated_data.get('journey_type', instance.journey_type)
        instance.save()
        return instance


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['pk', 'owner', 'name', 'plate_number', 'color', 'capacity', 'vehicle_type',]


class VehicleUpdateSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=False, read_only=True)
    owner = serializers.IntegerField(required=False, read_only=True)
    name = serializers.CharField(max_length=20)
    plate_number = serializers.CharField(max_length=20)
    color = serializers.CharField(max_length=15)
    capacity = serializers.IntegerField()
    vehicle_type = serializers.ChoiceField(choices=Vehicle.Vehicle_type.choices)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.plate_number = validated_data.get('plate_number', instance.plate_number)
        instance.color = validated_data.get('color', instance.color)
        instance.capacity = validated_data.get('capacity', instance.capacity)
        instance.vehicle_type = validated_data.get('vehicle_type', instance.vehicle_type)
        instance.save()
        # the fields are required so I must not test for all of them
        if instance.owner.location and instance.color:
            instance.owner.completed = True
            instance.owner.save()
        return instance


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    date_of_birth = serializers.DateField(required=True)
    phone = serializers.RegexField(regex="(?:^[+]{1}[0-9]*$)|(?:^0{1}[0-9]{10}$)", min_length=11, required=True)

    class Meta:
        model = User 
        fields = ['email', 'firstname', 'lastname', 'password', 'password2', 'date_of_birth', 'phone', 'referral', ]


    def save(self):
        user = User(email=self.validated_data['email'], firstname=self.validated_data['firstname'], lastname=self.validated_data['lastname'], date_of_birth=self.validated_data['date_of_birth'], phone=self.validated_data['phone'], referral=self.validated_data['referral'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        user.set_password(password)
        user.save()
        return user 