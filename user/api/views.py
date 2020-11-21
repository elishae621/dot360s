from main.models import Ride, Withdrawal
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.http import Http404
from django.contrib.auth import authenticate 

from user.models import User, Driver, Vehicle
from user.api.serializers import ( 
    UserSerializer, 
    DriverSerializer, 
    DriverUpdateSerializer, 
    VehicleSerializer,  
    VehicleUpdateSerializer,
    RegistrationSerializer,
)
from user.api.permissions import IsDriver


class ChoiceView(APIView):
    
    def get(self, request, *args, **kwargs):
        data= {}
        data['referral_status']    = [ choice[0] for choice in User.Referral_status.choices ] 
        data['cities']             = [ choice[0] for choice in Driver.City.choices ] 
        data['journey type']       = [ choice[0] for choice in Driver.Journey_type.choices ]
        data['driver status']      = [ choice[0] for choice in Driver.Driver_status.choices ]
        data['vehicle type']       = [ choice[0] for choice in Vehicle.Vehicle_type.choices ]
        data['ride status']        = [ choice[0] for choice in Ride.Ride_status.choices ]
        data['payment method']     = [ choice[0] for choice in Ride.Payment_method.choices ] 
        data['payment status']     = [ choice[0] for choice in Ride.Payment_status.choices ]
        data['Withdrawal status']  = [ choice[0] for choice in Withdrawal.Status.choices ]
        return Response(data=data, status=status.HTTP_200_OK)

class UserDetailView(APIView):

    def get_object(self):
        try:
            return User.objects.get(pk=self.request.query_params['pk'])
        except User.DoesNotExist:
            return Http404

    def get(self, request, *args, **kwargs):
        data = {}
        pk = request.query_params.get('pk', None)
        if pk == None:
            data['response']      = 'Error'
            data['error_message'] = 'pk must be in the query parameters'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 

        user = self.get_object()
        if user == Http404:
            data['response'] = 'User with pk does not exist'
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, context={'request': request})
        data = serializer.data
        return Response(data=data, status=status.HTTP_200_OK)


class DriverDetailView(APIView):

    def get_object(self):
        try:
            return Driver.objects.get(pk=self.request.query_params['pk'])
        except Driver.DoesNotExist:
            return Http404

    def get(self, request, *args, **kwargs):
        data = {}
        pk = request.query_params.get('pk', None)
        if pk == None:
            data['response']      = 'Error'
            data['error_message'] = 'pk must be in the query parameters'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 

        driver = self.get_object()
        if driver == Http404:
            data['response'] = 'Driver with pk does not exist'
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DriverSerializer(driver, context={'request': request})
        data = serializer.data
        return Response(data=data, status=status.HTTP_200_OK)


class VehicleDetailView(APIView):

    def get_object(self):
        try:
            return Vehicle.objects.get(pk=self.request.query_params['pk'])
        except Vehicle.DoesNotExist:
            return Http404

    def get(self, request, *args, **kwargs):
        data = {}
        pk = request.query_params.get('pk', None)
        if pk == None:
            data['response']      = 'Error'
            data['error_message'] = 'pk must be in the query parameters'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 

        vehicle = self.get_object()
        if vehicle == Http404:
            data['response'] = 'Vehicle with pk does not exist'
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = VehicleSerializer(vehicle, context={'request': request})
        data = serializer.data
        return Response(data=data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def get_object(self):
        try:
            return Driver.objects.get(pk=self.request.user.driver.pk)
        except Driver.DoesNotExist:
            return Http404

    def get(self, request, format=None):
        if self.get_object() != Http404:
            driver = self.get_object()
            driver_serializer  = DriverSerializer(driver, context={'request': request})
            vehicle_serializer = VehicleSerializer(driver.vehicle, context={'request': request})
            data = {}
            data['driver']  = driver_serializer.data 
            data['vehicle'] = vehicle_serializer.data 
            return Response(data)
        return Response({'detail': 'User has no profile'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, format=None):
        if self.get_object() != Http404:
            driver = self.get_object()
            driver_serializer  = DriverUpdateSerializer(driver, data=request.data)
            vehicle_serializer = VehicleUpdateSerializer(driver.vehicle, data=request.data)
            data = {}
            
            if driver_serializer.is_valid() and vehicle_serializer.is_valid():
                driver_serializer.save()
                vehicle_serializer.save()
                data['response'] = 'Profile Updated successfully'
                return Response(data=data, status=status.HTTP_202_ACCEPTED)
        
            errors = {}
            if not driver_serializer.is_valid():
                errors['driver'] = driver_serializer.errors 
                
            if not vehicle_serializer.is_valid():
                errors['vehicle'] = vehicle_serializer.errors 
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'User has no profile'}, status=status.HTTP_404_NOT_FOUND)


class RegistrationView(APIView):
    authorization_classes = []
    permission_classes    = []

    def post(self, request, *args, **kwargs):
        data = {}
        email = request.data.get('email', '0').lower()
        if self.validate_email(email) != None:
            data['response']      = 'Error'
            data['error_message'] = 'email is already in use'
            return Response(data=data, status=status.HTTP_226_IM_USED) 

        phone = request.data.get('phone', '0') 
        if self.validate_phone(phone) != None:
            data['response']      = 'Error' 
            data['error_message'] = "phone number is already in use" 
            return Response(data=data, status=status.HTTP_226_IM_USED)

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            data['response'] = 'successfully registered new user'
            data['email']    = user.email 
            data['pk']       = user.pk 
            token            = Token.objects.get(user=user).key
            data['token']    = token 
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors 
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

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


# LOGIN
class ObtainAuthTokenView(APIView):

    authentication_classes = []
    permission_classes     = []

    def post(self, request):
        context = {}

        email    = request.POST.get('email')
        password = request.POST.get('password')
        user     = authenticate(email=email, password=password)
        if user: 
            try:
                token = Token.objects.get(user=user) 
            except Token.DoesNotExist:
                token = Token.objects.create(user=user) 
            context['response'] = 'Successfully authenticated'
            context['pk']       = user.pk 
            context['email']    = email.lower()
            context['token']    = token.key 
        
        else:
            context['response']      = 'Error'
            context['error_message'] = 'Invalid credentials' 
        
        return Response(data=context, status=status.HTTP_202_ACCEPTED)

