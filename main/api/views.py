from django.http import Http404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from user.models import Driver, User
from user.api.permissions import IsDriver

from main.paystack_api import verify
from main.models import Request, Ride, Order, Withdrawal
from main.signals import order_accepted
from main.api.serializers import ( 
    RequestCreateSerializer, 
    RequestSerializer, 
    RideSerializer, 
    OrderSerializer, WithdrawalCreateSerializer, 
    WithdrawalSerializer,
)


class ChangeDriverStatusView(APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def get(self, request, *args, **kwargs):
        data = {}
        driver = request.user.driver
        if driver.status == 'AV':
            driver.status = 'NA'
            driver.save()
        elif driver.status == 'NA':
            driver.status = 'AV'
            driver.save()
        else:
            data['response'] = 'Error'
            data['error_message'] = "you are busy now, complete your current ride to change your status"
            return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)

        data['response'] = 'success'
        data['message'] = 'status has been changed'
        data["driver's status"] = driver.status 
        data['driver'] = driver.pk
        return Response(data=data, status=status.HTTP_200_OK)


class VerifyCompletedView(APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def get_object(self):
        request = Request.objects.get(pk=self.request.data.get('pk'))
        return request.order_of_request 

    def get(self, request, *args, **kwargs):
        data = {}
        if 'pk' in request.data:
            order = self.get_object()
            order.request.ride.status = "completed"
            order.request.ride.save()
            order.request.driver.status = 'AV'
            order.request.driver.save()
            data['response'] = 'success'
            data['message']  = "ride has been completed"
            data['request']  = order.request.pk 
            data['ride']     = order.request.ride.pk
            data['order']    = order.pk
            return Response(data=data, status=status.HTTP_200_OK) 
        
        else:
            data['response']      = 'Error'
            data['error_message'] = "Primary key of request should be sent in post body"
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 


class OngoingOrderView(APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def get_object(self):
        request = Request.objects.get(pk=self.request.data.get('pk'))
        return request.order_of_request 

    def get(self, request, *args, **kwargs):
        data = {}
        if 'pk' in request.data:
            order = self.get_object()
            order.request.ride.status = "ongoing"
            order.request.ride.save()
            # charge the passenger for ride
            if order.request.ride.payment_status == "unpaid":
                if order.request.ride.payment_method == "card": 
                    order.request.passenger.account_balance -= order.request.ride.price
                    order.request.passenger.save()
                order.request.ride.payment_status = "paid"
                order.request.ride.save()
            data['response']      = 'success'
            data['message'] = "ride has started"
            data['request'] = order.request.pk 
            data['ride']    = order.request.ride.pk
            data['order']   = order.pk
            return Response(data=data, status=status.HTTP_200_OK) 
        
        else:
            data['response']      = 'Error'
            data['error_message'] = "Primary key of request should be sent in post body"
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 


class TakeOrderView(APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def get_object(self):
        request = Request.objects.get(pk=self.request.data.get('pk'))
        return request.order_of_request 

    def get(self, request, *args, **kwargs):
        data = {}
        if 'pk' in request.data:
            order = self.get_object()
            order.accepted = True 
            order.save()
            driver = Driver.objects.get(user=request.user)
            order_accepted.send(sender=Order, Order=order, Driver=driver)
            data['response'] = 'success'
            data['message']  = "Driver is now the order of the request"
            data['request']  = order.request.pk 
            data['ride']     = order.request.ride.pk
            data['order']    = order.pk
            return Response(data=data, status=status.HTTP_200_OK) 
        
        else:
            data['response']      = 'Error'
            data['error_message'] = "Primary key of request should be sent in post body"
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 
        

class CancelRequestView(APIView):

    def get_object(self):
        request = Request.objects.get(pk=self.request.data.get('pk'))
        return request 

    def post(self, request, *args, **kwargs):
        data = {}
        if 'pk' in request.data:
            request = self.get_object()
            request.ride.status = 'cancelled'
            request.ride.save()

            try: 
                if request.driver.status == 'BU':
                    request.driver.status = 'AV'
                    request.driver.save()
                    data['driver_status'] = "driver's status is now set to avaliable"
            except:
                pass

            data['response'] = 'success'
            data['detail'] = "ride status has been changed to cancelled"
            data['request'] = request.pk
            data['ride'] = request.ride.pk
            data['order'] = request.order_of_request.pk
            return Response(data=data, status=status.HTTP_200_OK)

        else:
            data['response']      = 'Error'
            data['error_message'] = "Primary key of request should be sent in post body"
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 
           


class AnotherDriverView(APIView):

    def get_object(self):
        request = Request.objects.get(pk=self.request.data.get('pk'))
        return request.order_of_request

    def post(self, request, *args, **kwargs):
        data = {}
        if 'pk' in request.data:

            order = self.get_object()
            order.accepted = False
            order.save()
            order.driver.remove(order.request.driver)
            order.save()
            order.request.driver = None
            order.request.save()
                    
            if 'driver' in request.data:
                driver = request.data.get('driver')
                order.driver.add(driver)
                order.save()
                message = "Driver has been added to order. prompt him to accept request"
                
            else:
                message = "Driver has been removed and request is open" 

            data['response']   = 'success'
            data['detail']     = message
            data['request']    = order.request.pk
            data['ride']       = order.request.ride.pk
            data['order']      = order.pk
            return Response(data=data, status=status.HTTP_200_OK)

            
        else:
            data['response']      = 'Error'
            data['error_message'] = "Primary key of request should be sent in post body"
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 
           

class RequestListView(ListAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer 
    pagination_class = PageNumberPagination 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'
    search_fields = ['driver', 'passenger', 'from_address', 'to_address', ]
    order_fields = '__all__'
    ordering = ['-time']


class RideListView(ListAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer 
    pagination_class = PageNumberPagination 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'
    order_fields = '__all__'
    ordering = ['status']


class OrderListView(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer 
    pagination_class = PageNumberPagination 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'
    order_fields = '__all__'
    ordering = ['-time_posted']


class WithdrawalListView(ListAPIView):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer 
    pagination_class = PageNumberPagination 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'
    search_fields = ['name', 'reason']
    order_fields = '__all__'
    ordering = ['-date']


class RequestCreateView(APIView):
    
    def post(self, request, *args, **kwargs):
        data = {}
        serializer = RequestCreateSerializer(data=request.data)

        if serializer.is_valid():

            city = request.data.get('city').lower()
            list_of_drivers = Driver.objects.filter(location=city)
            if not list_of_drivers:
                data['response']      = 'Error'
                data['error_message'] = "We are coming to your city soon. We appologize for any inconviences"
                return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE) 

            intercity = request.data.get('intercity')
            list_of_out_drivers = []
            list_of_in_drivers  = []
            valid_drivers = list_of_drivers
            for driver in list(valid_drivers):
                if 'OUT' in driver.journey_type:
                    list_of_out_drivers.append(driver)
                if 'IN' in driver.journey_type:
                    list_of_in_drivers.append(driver)
            if intercity == 'True' or intercity == True:
                list_of_drivers = list_of_out_drivers
            elif intercity == 'False' or intercity == False:
                list_of_drivers = list_of_in_drivers
            if not list_of_drivers:
                data['response']      = 'Error'
                data['error_message'] = "No driver offers this journey type in your city"
                return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE) 

            request_vehicle_type = request.data.get('request_vehicle_type')   
            list_of_drivers_with_vehicle = []
            for driver in list(list_of_drivers):
                if driver.vehicle.vehicle_type == request_vehicle_type:
                    list_of_drivers_with_vehicle.append(driver)
            if list_of_drivers_with_vehicle == []:
                data['response']      = 'Error'
                data['error_message'] = "None of our Drivers with this vehicle type in your city are avaliable at this time. Please try again at another time"
                return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE) 
           
            else:
                list_of_drivers = list_of_drivers_with_vehicle
             
            request_created = serializer.save()
            request_created.passenger = request.user
            request_created.save()
            
            ride = Ride.objects.get(request=request_created)
            ride.payment_method = request.data.get('payment_method')
            ride.save()
            # if card payment was chosen 
            if request.data.get('payment_method') == 'card':
                if self.request.user.account_balance < ride.price:
                    data['response']      = 'Error'
                    data['error_message'] = f"Insufficient Balance. Your ride costs {ride.price} naira."
                    return Response(data=data, status=status.HTTP_402_PAYMENT_REQUIRED)

            # list_of_drivers can't be empty. if it is then form validations are not effective
            for driver in list_of_drivers:
                if driver.status != 'AV' or not driver.completed or not driver.user.is_active or driver.user == self.request.user:
                    list_of_drivers.remove(driver)
            order = Order.objects.filter(request=request_created).first()

            if list_of_drivers != []:
                for driver in list_of_drivers:
                    order.driver.add(driver)
                order.save()
            else:
                request_created.save()
                data['response'] = 'request created sucessfully'
                data['message']  = "No avaliable driver"
                data['pk'] = request_created.pk
                return Response(data=data, status=status.HTTP_201_CREATED)

            request_created.save()
            data['response'] = 'request created sucessfully'
            data['message']  = "Request is yet to be accepted"
            data['pk'] = request_created.pk
            data['ride'] = ride.pk
            data['order'] = order.pk
            return Response(data=data, status=status.HTTP_201_CREATED)
 
        else:
            data = serializer.errors 
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class VerifyTransactionView(APIView):
    def get(self, request, *args, **kwargs):
        data = {}
        if 'reference' in request.query_params:
            reference = request.query_params.get('reference', "")
            response  = verify(request.user, reference)
            if response.get('status', 'False'):
                # add 50 to the referral user if balance is above 200
                try:
                    if request.user.referral and request.user.account_balance >= 200 and request.user.referral_status == 'unpaid':
                        referral_user = User.objects.filter(email=request.user.referral).first()
                        referral_user.account_balance += 50
                        referral_user.save()
                        request.user.referral_status = "paid"
                        request.user.save()
                except:
                    pass
                data['response'] = "success"
                data['detail'] = response.get('message')
                return Response(data=data, status=status.HTTP_202_ACCEPTED)
                
            else:
                data['response'] = "Error"
                data['detail']   = response.get('message')
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            data['response'] = "Error"
            data['detail']   = "Improperly configured. No reference in verify. Please try again. If this continues, contact Dot360s"
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class RequestDetailView(APIView):

    def get_object(self):
        try:
            return Request.objects.get(pk=self.request.query_params['pk'])
        except Request.DoesNotExist:
            return Http404

    def get(self, request, *args, **kwargs):
        data = {}
        pk = request.query_params.get('pk', None)
        if pk == None:
            data['response']      = 'Error'
            data['error_message'] = 'pk must be in the query parameters'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 

        request_obtained = self.get_object()
        if request_obtained == Http404:
            data['response'] = 'Request with pk does not exist'
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RequestSerializer(request_obtained, context={'request': request})
        data       = serializer.data
        data['ride'] = request_obtained.ride.pk
        data['order'] = request_obtained.order_of_request.pk
        return Response(data=data, status=status.HTTP_200_OK)


class RideDetailView(APIView):

    def get_object(self):
        try:
            return Ride.objects.get(pk=self.request.query_params['pk'])
        except Ride.DoesNotExist:
            return Http404

    def get(self, request, *args, **kwargs):
        data = {}
        pk = request.query_params.get('pk', None)
        if pk == None:
            data['response']      = 'Error'
            data['error_message'] = 'pk must be in the query parameters'
            return Response(data, status=status.HTTP_400_BAD_REQUEST) 

        ride = self.get_object()
        if ride == Http404:
            data['response'] = 'Ride with pk does not exist'
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RideSerializer(ride, context={'request': request})
        data       = serializer.data
        data['order'] = ride.request.order_of_request.pk
        return Response(data=data, status=status.HTTP_200_OK)


class OrderDetailView(APIView):

    def get_object(self):
        try:
            return Order.objects.get(pk=self.request.query_params['pk'])
        except Order.DoesNotExist:
            return Http404

    def get(self, request, *args, **kwargs):
        data = {}
        pk = request.query_params.get('pk', None)
        if pk == None:
            data['response']      = 'Error'
            data['error_message'] = 'pk must be in the query parameters'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 

        order = self.get_object()
        if order == Http404:
            data['response'] = 'Order with pk does not exist'
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderSerializer(order, context={'request': request})
        data       = serializer.data
        data['ride'] = order.request.ride.pk
        return Response(data=data, status=status.HTTP_200_OK)


class WithdrawalDetailView(APIView):

    def get_object(self):
        try:
            return Withdrawal.objects.get(pk=self.request.query_params['pk'])
        except Withdrawal.DoesNotExist:
            return Http404

    def get(self, request, *args, **kwargs):
        data = {}
        pk = request.query_params.get('pk', None)
        if pk == None:
            data['response']      = 'Error'
            data['error_message'] = 'pk must be in the query parameters'
            return Response(data, status=status.HTTP_400_BAD_REQUEST) 

        withdrawal = self.get_object()
        if withdrawal == Http404:
            data['response'] = 'Withdrawal with pk does not exist'
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = WithdrawalSerializer(withdrawal, context={'request': request})
        data       = serializer.data
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = {}
        serializer = WithdrawalCreateSerializer(data=request.data)

        if serializer.is_valid():

            amount = request.data.get('amount', 0)
            if int(amount) < 1000:
                data['response'] = 'Error'
                data['error_message'] = "Minimum withdrawal amount is 1000 naira"
                return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            if int(amount) > request.user.account_balance:
                data['response'] = 'Error'
                data['error_message'] = f"Insufficient Balance. Your account balance is {request.user.account_balance} NGN"
                return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            withdrawal = serializer.save()
            withdrawal.user = self.request.user 
            withdrawal.save()
            data['response']   = 'success'
            data['message']    = 'withdrawal request has been created' 
            data['withdrawal'] = withdrawal.pk 
            return Response(data=data, status=status.HTTP_201_CREATED)

        else:
            data = serializer.errors 
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)