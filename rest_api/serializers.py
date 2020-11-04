from user.models import User, Driver, Vehicle, Request, Ride, Order
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'email', 'firstname', 'lastname', 'phone', 'account_balance', 'is_staff', 'is_active', 'is_driver',]


class DriverSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Driver
        fields = ['url', 'user', 'image', 'location', 'status', 'journey_type',]


class VehicleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['url', 'owner', 'name', 'plate_number', 'color', 'capacity', 'vehicle_type',]


class RequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Request
        fields = ['url', 'driver', 'passenger', 'from_address', 'to_address', 'city', 'no_of_passengers', 'intercity', 'load', 'time', 'request_vehicle_type', ]


class RideSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ride 
        fields = ['url', 'request', 'status', 'price', 'payment_status', 'payment_method', ]


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ['url', 'request', 'driver', 'time_posted', 'accepted', 'slug', ]