from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from user.models import User, Driver, Vehicle
from main.models import Request, Ride, Order, Withdrawal
from user.api.serializers import ( 
    UserSerializer, DriverSerializer, 
    VehicleSerializer, RequestSerializer, 
    RideSerializer, OrderSerializer, 
    WithdrawalSerializer, RegistrationSerializer,
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer 
    permission_classes = [permissions.IsAuthenticated]


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer 
    permission_classes = [permissions.IsAuthenticated]


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer 
    permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class WithdrawalViewSet(viewsets.ModelViewSet):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer 
    permission_classes = [permissions.IsAuthenticated]


class DriverProfileDetailView(APIView):
    
    def get_object(self):
        try:
            return Driver.objects.get(pk=self.request.user.pk)
        except Driver.DoesNotExist:
            return Http404

    def get(self, request, format=None):
        driver = self.get_object()
        serializer = DriverSerializer(driver)
        return Response(serializer.data)


class RegistrationView(APIView):

    def post(self, request, *args, **kwargs):
        data = {}
        email = request.data.get('email', '0').lower()
        if self.validate_email(email) != None:
            data['error_message'] = 'email is already in use'
            data['response'] = 'Error'
            return Response(data) 

        phone = request.data.get('phone', '0') 
        if self.validate_phone(phone) != None:
            data['error_message'] = "phone number is already in use" 
            data['response'] = 'Error' 
            return Response(data)

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            data['response'] = 'successfully registered new user'
            data['email'] = user.email 
            data['pk'] = user.pk 
            token = Token.objects.get(user=user).key
            data['token'] = token 
        else:
            data = serializer.errors 
        return Response(data)

    def validate_email(self, email):
        user = None 
        try:
            user = User.objects.filter(email=email).first()
        except User.DoesNotExist:
            return None 
        if user != None:
            return email

    def validate_phone(self, phone):
        user = None 
        try:
            user = User.objects.filter(phone=phone).first()
        except User.DoesNotExist:
            return None 
        if user != None:
            return phone
