from user.models import User, Driver, Vehicle
from main.models import Request, Ride, Order, Withdrawal
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'email', 'firstname', 'lastname', 'phone', 'account_balance', 'date_of_birth', 'referral', 'referral_status', 'is_staff', 'is_active', 'is_driver',]


class DriverSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Driver
        fields = ['url', 'user', 'image', 'location', 'status', 'journey_type', 'completed', ]


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


class WithdrawalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['url', 'name', 'amount', 'date', 'reason', 'account_no', 'bank', 'status', ]


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User 
        fields = ['email', 'firstname', 'lastname', 'password', 'password2', 'date_of_birth', 'phone', 'referral', 'referral_status', ]

    def save(self):
        user = User(email=self.validated_data['email'], firstname=self.validated_data['firstname'], lastname=self.validated_data['lastname'], date_of_birth=self.validated_data['date_of_birth'], phone=self.validated_data['phone'], referral=self.validated_data['referral'], referral_status=self.validated_data['referral_status'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match'})
            user.set_password(password)
            user.save()
            return user 