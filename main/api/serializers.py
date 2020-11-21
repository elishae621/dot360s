from user.models import Driver, Vehicle
from rest_framework import serializers

from main.models import Request, Ride, Order, Withdrawal


class FundAccountSerializer(serializers.Serializer):
    account = serializers.IntegerField()


class RequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Request
        fields = ['pk', 'driver', 'passenger', 'from_address', 'to_address', 'city', 'no_of_passengers', 'intercity', 'load', 'time', 'request_vehicle_type',]

    


class RequestCreateSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=False)
    driver = serializers.PrimaryKeyRelatedField(many=False, read_only=True, required=False)
    passenger = serializers.PrimaryKeyRelatedField(many=False, read_only=True, required=False)
    from_address = serializers.CharField(max_length=50)
    to_address = serializers.CharField(max_length=50)
    city = serializers.ChoiceField(choices=Driver.City.choices)
    no_of_passengers = serializers.IntegerField()
    intercity = serializers.BooleanField()
    load = serializers.BooleanField()
    time = serializers.DateTimeField()
    request_vehicle_type = serializers.ChoiceField(choices=Vehicle.Vehicle_type.choices)
    payment_method = serializers.ChoiceField(choices=Ride.Payment_method.choices)

    def create(self, validated_data):
        return Request.objects.create(from_address=validated_data.get('from_address', ''), to_address=validated_data.get('to_address', ''),city=validated_data.get('city', ''), no_of_passengers=validated_data.get('no_of_passengers', ''), intercity=validated_data.get('intercity', ''), load=validated_data.get('load', ''), time=validated_data.get('time', ''), request_vehicle_type=validated_data.get('request_vehicle_type', ''))
        

    def update(self, instance, validated_data):
        instance.from_address = validated_data.get('from_address', instance.from_address)
        instance.to_address = validated_data.get('to_address', instance.to_address)
        instance.city = validated_data.get('city', instance.city)
        instance.no_of_passengers = validated_data.get('no_of_passengers', instance.no_of_passengers)
        instance.intercity = validated_data.get('intercity', instance.intercity)
        instance.load = validated_data.get('load', instance.load)
        instance.time = validated_data.get('time', instance.time)
        instance.request_vehicle_type = validated_data.get('request_vehicle_type', instance.request_vehicle_type)
        instance.save()
        instance.ride.payment_method = validated_data.get('payment_method', instance.ride.payment_method)
        instance.ride.save()
        return instance


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride 
        fields = ['pk', 'request', 'status', 'price', 'payment_status', 'payment_method', ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['pk', 'request', 'driver', 'time_posted', 'accepted', 'slug', ]


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['pk', 'user', 'name', 'amount', 'date', 'reason', 'account_no', 'bank', 'status', ]

    
class WithdrawalCreateSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=False)
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True, required=False)
    name = serializers.CharField(max_length=30)
    amount = serializers.IntegerField()
    date = serializers.DateTimeField()
    reason = serializers.CharField(max_length=50, required=False)
    account_no = serializers.IntegerField()
    bank = serializers.CharField(max_length=20)
    status = serializers.ChoiceField(choices=Withdrawal.Status.choices, required=False)

    def create(self, validated_data):
        withdrawal = Withdrawal.objects.create(name=validated_data.get('name'), amount=validated_data.get('amount'), date=validated_data.get('date'), reason=validated_data.get('reason'), account_no=validated_data.get('account_no'), bank=validated_data.get('bank'))
        return withdrawal 

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.amount = validated_data.get('plate_number', instance.amount)
        instance.date = validated_data.get('date', instance.date)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.account_no = validated_data.get('account_no', instance.account_no)
        instance.bank = validated_data.get('bank', instance.bank)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance 