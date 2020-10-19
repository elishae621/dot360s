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
from django.views.generic import CreateView
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic.base import RedirectView
from django.shortcuts import redirect


class home(TemplateView):
    template_name = "user/home.html"


class driver_update_profile(GetLoginedInUserMixin, Update_view):
    """inheriting the main deadly mixin I wrote"""
    success_url = reverse_lazy('home')
    template_name = "user/driver_profile_update.html"


class profile_detail_view(GetLoginedInUserMixin, DetailView):
    template_name = "user/driver_profile_detail.html"
    model = Driver
