from django.urls import reverse_lazy
from django.views import generic
from user.models import Driver
from user.mixins import Update_view, GetLoggedInDriverMixin
from django.shortcuts import render, reverse



def error_400(request, exception):
    data = {} 
    return render(request, 'user/400.html', data) 


def error_403(request, exception):
    data = {} 
    return render(request, 'user/403.html', data) 


def error_404(request, exception):
    data = {} 
    return render(request, 'user/404.html', data) 


def error_500(request):
    data = {} 
    return render(request, 'user/500.html', data) 


class profile_detail_view(GetLoggedInDriverMixin, generic.DetailView):
    template_name = "user/profile_detail.html"
    model = Driver


class driver_update_profile(GetLoggedInDriverMixin, Update_view, generic.UpdateView):
    """inheriting the main deadly mixin I wrote"""
    template_name = "user/driver_profile_update.html"
    model = Driver

    def get_success_url(self):
        return reverse('driver_profile_detail', kwargs={'pk': self.request.user.pk})

