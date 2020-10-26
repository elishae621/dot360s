from django.views import generic
from user.models import (
    Driver, Request,
    Ride)
from user.forms import (
    RequestForm
)
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from user.mixins import (
    Update_view, 
    GetLoggedInDriverMixin, 
    GetLoggedInUserRequestMixin,
    GetLoggedInUserRideMixin,
)
import random
from dot360s.settings import PAYSTACK_PUBLIC_KEY


class home(generic.TemplateView):
    template_name = "user/home.html"

class driver_update_profile(GetLoggedInDriverMixin, Update_view):
    """inheriting the main deadly mixin I wrote"""
    success_url = reverse_lazy('driver_profile_update')
    template_name = "user/driver_profile_update.html"
    model = Driver


class profile_detail_view(GetLoggedInDriverMixin, generic.DetailView):
    template_name = "user/driver_profile_detail.html"
    model = Driver

class RequestView(generic.CreateView):
    model = Request
    form_class = RequestForm
    template_name = "user/request_form.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.passenger = self.request.user
        valid_drivers = form.cleaned_data['valid_drivers']
        # valid_drivers can't be empty. if it is then form validations are not
        # effective
        for driver in valid_drivers:
            if driver.status != 'AV':
                valid_drivers.remove(driver)
        if valid_drivers != []:
            driver = random.choices(valid_drivers)
            self.object.driver = driver[0]
        else:
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('no_avaliable_driver'))# no avaliable driver
        self.object.save()
        return HttpResponseRedirect((self.get_success_url()))


class PriceConfirmation(GetLoggedInUserRideMixin, generic.DetailView):
    template_name = "user/price_confirmation.html"
    model = Ride
    
    def get_context_data(self, **kwargs):
        kwargs = super(PriceConfirmation, self).get_context_data(**kwargs)
        kwargs['PAYSTACK_PUBLIC_KEY'] = PAYSTACK_PUBLIC_KEY
        return kwargs

class NoAvaliableDriver(generic.TemplateView):
    template_name = "user/no_avaliable_driver.html"


class RequestUpdate(GetLoggedInUserRequestMixin, generic.UpdateView):
    template_name = "user/update_request.html"
    form_class = RequestForm
    model = Request

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.passenger = self.request.user
        valid_drivers = form.cleaned_data['valid_drivers']
        # valid_drivers can't be empty. if it is then form validations are not
        # effective
        for driver in valid_drivers:
            if driver.status != 'AV':
                valid_drivers.remove(driver)
        if valid_drivers != []:
            driver = random.choices(valid_drivers)
            self.object.driver = driver[0]
        else:
            self.object.save()
            return HttpResponseRedirect(reverse_lazy('no_avaliable_driver'))# no avaliable driver
        self.object.save()
        return HttpResponseRedirect((self.get_success_url()))


class RequestDelete(GetLoggedInUserRequestMixin, generic.DeleteView):
    success_url = reverse_lazy("home")
    model = Request


class VerifyTransaction(GetLoggedInUserRideMixin):
    model = Ride
    template_name = "verify_transaction.html"

    def get(self, request, *args, **kwargs):
        if 'reference' in kwargs:
            self.get_object().reference = kwargs.get('reference')
            self.get_object().save()
        return super(VerifyTransaction, self).get(request, *args, **kwargs)