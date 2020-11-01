from user.mixins import MustbeDriverMixin
import time
from django.http.response import HttpResponseBadRequest
import requests
from django.views import generic
from user.models import (
    User,
    Driver, Request,
    Ride, Order)
from user.forms import (
    RequestForm, 
    FundAccountForm,
)
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from user.mixins import (
    Update_view, 
    GetLoggedInDriverMixin, 
    GetLoggedInUserRequestMixin,
    GetLoggedInUserRideMixin,
    LoginRequiredMixin,
    OrderAcceptedMixin,
    OrderNotAcceptedMixin,
)
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from user.paystack_api import authorize, verify
from user.signals import order_accepted


class Index(generic.RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_driver:
            return reverse_lazy('driver_orders')
        else:
            return reverse_lazy('passenger_home')


class home(LoginRequiredMixin, generic.TemplateView):
    template_name = "user/home.html"


class FundAccount(LoginRequiredMixin, generic.FormView):
    form_class = FundAccountForm
    template_name = "user/fund_account.html"

    def form_valid(self, form):
        auth_response = authorize(self.request.user, form.cleaned_data.get('amount', 0))
        if auth_response is not None:
            return redirect(auth_response['data'].get('authorization_url'))
        
        messages.add_message(self.request, messages.ERROR, "An Error Occured, Paystack cannot be reached at this time")
        return self.render_to_response(self.get_context_data())


class VerifyTransaction(GetLoggedInUserRideMixin, OrderAcceptedMixin, generic.detail.BaseDetailView):
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


class driver_update_profile(GetLoggedInDriverMixin, Update_view, generic.UpdateView):
    """inheriting the main deadly mixin I wrote"""
    success_url = reverse_lazy('driver_profile_update')
    template_name = "user/driver_profile_update.html"
    model = Driver


class profile_detail_view(GetLoggedInDriverMixin, generic.DetailView):
    template_name = "user/driver_profile_detail.html"
    model = Driver

class RequestCreate(LoginRequiredMixin, generic.CreateView):
    model = Request
    form_class = RequestForm
    template_name = "user/request_form.html"
    success_url = reverse_lazy("unaccepted_request")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.passenger = self.request.user
        self.object.save()
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


class UnacceptedRequest(GetLoggedInUserRideMixin,  OrderNotAcceptedMixin, generic.DetailView):
    template_name = "user/unaccepted_request.html"


class NoAvaliableDriver(OrderNotAcceptedMixin, generic.TemplateView):
    template_name = "user/no_avaliable_driver.html"


class RequestDelete(GetLoggedInUserRequestMixin, generic.DeleteView):
    success_url = reverse_lazy("home")
    model = Request


class OrderListView(MustbeDriverMixin, generic.ListView):
    template_name = "user/home.html"
    context_object_name = 'orders'
    ordering = ['-time_posted']
    paginate_by = 10

    def get_queryset(self):
        driver = get_object_or_404(Driver, user=self.request.user)
        return Order.objects.filter(driver=driver).filter(accepted=False).order_by('-time_posted')


class OrderDetail(MustbeDriverMixin, generic.DetailView):
    model = Order 
    template_name = "user/detail_order.html"

class TakeOrder(MustbeDriverMixin, generic.DetailView):
    model = Order
    template_name = "user/take_order.html"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.accepted = True 
        order.save()
        order_accepted.send(sender=Order, Order=self.order, Driver=self.driver)
        order.request.ride.status = 3
        order.request.ride.save()
        if order.request.ride.time >= time.now():
            order.request.ride.status = 4
        order.request.ride.save()
        return super(TakeOrder, self).get(request, *args, **kwargs)


class OngoingOrder(generic.detail.BaseDetailView):
    model = Order

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.request.ride.status = 4
        order.request.ride.save()
        return super(OngoingOrder, self).get(request, *args, **kwargs)


class VerifyCompleted(generic.DetailView):
    """verify from the passenger if the ride hass been completed"""
    model = Order
    template_name = "user/verify_completed.html"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.request.ride.status = 5
        order.request.ride.save()
        return super(VerifyCompleted, self).get(request, *args, **kwargs)

