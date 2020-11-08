from django.views import generic
from user.models import User, Driver
from main.models import Request, Ride, Order
from main.forms import RequestForm, FundAccountForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from user.mixins import MustbeDriverMixin
from main.mixins import GetLoggedInUserRideMixin, OrderNotAcceptedMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from main.paystack_api import authorize, verify
from main.signals import order_accepted




class Index(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_driver:
            return redirect(reverse_lazy('driver_orders'))
        else:
            return redirect(reverse_lazy('passenger_home'))


class home(LoginRequiredMixin, generic.TemplateView):
    template_name = "main/home.html"


class FundAccount(LoginRequiredMixin, generic.FormView):
    form_class = FundAccountForm
    template_name = "main/fund_account.html"

    def form_valid(self, form):
        auth_response = authorize(self.request.user, form.cleaned_data.get('amount', 0))
        if auth_response is not None:
            return redirect(auth_response['data'].get('authorization_url'))
        
        messages.add_message(self.request, messages.ERROR, "An Error Occured, Paystack cannot be reached at this time")
        return self.render_to_response(self.get_context_data())


class VerifyTransaction(generic.detail.BaseDetailView):
    model = User
    
    def get(self, request):
        if 'reference' in request.GET:
            reference = request.GET.get('reference', "")
            response = verify(self.request.user, reference)
            if response.get('status', 'False'):
                messages.add_message(request, messages.SUCCESS, response.get('message'))
                return HttpResponseRedirect(reverse_lazy("passenger_home"))
            else:
                messages.add_message(request, messages.ERROR, response.get('message'))
                return HttpResponseRedirect(reverse_lazy("fund_account"))
        else:
            messages.add_message(request, messages.ERROR, "Improperly configured. No reference in verify. Please try again. If this continues, contact Dot360s")
            return HttpResponseRedirect(reverse_lazy('fund_account'))


class RequestCreate(LoginRequiredMixin, generic.CreateView):
    model = Request
    form_class = RequestForm
    template_name = "main/request_form.html"
    success_url = reverse_lazy("unaccepted_request")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.passenger = self.request.user
        self.object.save()
        ride = Ride.objects.get(request=self.object)
        ride.payment_method = form.cleaned_data.get('payment_method')
        ride.save()
        # if card payment was chosen 
        if form.cleaned_data.get('payment_method') == 'card':
            if self.request.user.account_balance < ride.price:
                messages.add_message(self.request, messages.ERROR, f"Insufficient Balance. Your ride costs {ride.price} naira.")
                return HttpResponseRedirect(reverse_lazy('fund_account'))
        valid_drivers = form.cleaned_data['valid_drivers']
        # valid_drivers can't be empty. if it is then form validations are not
        # effective
        for driver in valid_drivers:
            if driver.status != 'AV':
                valid_drivers.remove(driver)
        if valid_drivers != []:
            order = Order.objects.filter(request=self.object).first()
            order.save()
            for driver in valid_drivers:
                order.driver.add(driver)
            order.save()
        else:
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('no_avaliable_driver'))# no avaliable driver
        self.object.save()
        # user would be redirect to the detail page if the request is accepted
        return HttpResponseRedirect(reverse_lazy('unaccepted_request'))


class NoAvaliableDriver(generic.TemplateView):
    template_name = "main/no_avaliable_driver.html"


class UnacceptedRequest(GetLoggedInUserRideMixin,  OrderNotAcceptedMixin, generic.DetailView):
    model = Ride
    template_name = "main/unaccepted_request.html"


class RequestListView(generic.ListView):
    template_name = "main/home.html"
    context_object_name = 'requests'
    ordering = ['-time']
    paginate_by = 10

    def get_queryset(self):
        return Request.objects.filter(passenger=self.request.user).exclude(ride__status="cancelled").order_by('-time')


class OrderDetail(generic.DetailView):
    model = Order 
    template_name = "main/order_detail.html"


class AnotherDriver(generic.DetailView):
    model = Order
    template_name = "main/another_driver.html"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.accepted = False
        order.save()
        order.driver.remove(order.request.driver)
        order.save()
        order.request.driver = None
        order.request.save()
        return HttpResponseRedirect(reverse_lazy('unaccepted_request')) 


class CancelRequest(GetLoggedInUserRideMixin, generic.DeleteView):
    success_url = reverse_lazy("home")
    model = Request

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.status = "cancelled"
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderListView(MustbeDriverMixin, generic.ListView):
    template_name = "main/home.html"
    context_object_name = 'orders'
    ordering = ['-time_posted']
    paginate_by = 10

    def get_queryset(self):
        driver = get_object_or_404(Driver, user=self.request.user)
        return Order.objects.filter(driver=driver).exclude(request__ride__status="cancelled").filter(accepted=False).order_by('-time_posted')


class TakeOrder(MustbeDriverMixin, generic.DetailView):
    model = Order
    template_name = "main/take_order.html"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.accepted = True 
        order.save()
        driver = Driver.objects.get(user=request.user)
        order_accepted.send(sender=Order, Order=order, Driver=driver)
        return super(TakeOrder, self).get(request, *args, **kwargs)


class OngoingOrder(generic.detail.DetailView):
    model = Order

    def get(self, request, *args, **kwargs):
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
        return super(OngoingOrder, self).get(request, *args, **kwargs)


class VerifyCompleted(generic.DetailView):
    """verify from the passenger if the ride hass been completed"""
    model = Order
    template_name = "main/verify_completed.html"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.request.ride.status = "completed"
        order.request.ride.save()
        return super(VerifyCompleted, self).get(request, *args, **kwargs)


# history of the request is avaliable, but I don't really 
# the best way to order it and where it should be