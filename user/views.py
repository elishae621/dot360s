from django.views.generic.detail import DetailView
from user.models import (
    Driver, User, Vehicle, Request,
    Ride)
from django.views.generic import TemplateView
from user.forms import (
    UserRegistrationForm,
    DriverProfileUpdateForm,
    VehicleUpdateForm
)
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from user.mixins import Update_view, GetLoginedInUserMixin
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from allauth.account.views import SignupView, complete_signup, app_settings, ImmediateHttpResponse


class RegisterView(SignupView):
    def form_valid(self, form):
        self.user = form.save(self.request)
        if self.kwargs.get('driver'):
            self.user.is_driver = True
            Driver.objects.create(user=self.user)
        try:
            return complete_signup(
                self.request, self.user,
                app_settings.EMAIL_VERIFICATION,
                self.get_success_url())
        except ImmediateHttpResponse as e:
            return e.response

    def get_success_url(self):
        if self.user.is_driver:
            self.success_url = reverse_lazy("driver_profile_update")
        else:
            self.success_url = reverse_lazy("user_profile_detail")


class home(TemplateView):
    pass


class driver_update_profile(GetLoginedInUserMixin, Update_view):
    """inheriting the main deadly mixin I wrote"""
    success_url = reverse_lazy('user_profile_detail')
    template_name = "user/driver_profile_update.html"


class profile_detail_view(GetLoginedInUserMixin, DetailView):
    template_name = "user/driver_profile_detail.html"
    model = Driver
