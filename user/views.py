from django.views import generic
from user.models import Driver
from django.urls import reverse_lazy
from user.mixins import Update_view, GetLoggedInDriverMixin


class profile_detail_view(GetLoggedInDriverMixin, generic.DetailView):
    template_name = "user/driver_profile_detail.html"
    model = Driver


class driver_update_profile(GetLoggedInDriverMixin, Update_view, generic.UpdateView):
    """inheriting the main deadly mixin I wrote"""
    success_url = reverse_lazy('driver_profile_update')
    template_name = "user/driver_profile_update.html"
    model = Driver


