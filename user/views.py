from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from user.models import Profile, User
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from user.forms import UserRegistrationForm, ProfileUpdateForm, UserUpdateForm
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from user.mixins import Update_view
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from braces.views import CsrfExemptMixin
from django.views.generic.base import RedirectView


# class basehome(RedirectView):
#     pattern_name = 'register'


class update_profile(LoginRequiredMixin, Update_view):
    """inheriting the main deadly mixin I wrote"""
    success_url = reverse_lazy('user_profile_detail')
    template_name = "user/profile_update.html"


class profile_detail_view(DetailView):
    template_name = "user/profile_detail.html"
    model = Profile


class user_profile_detail_view(LoginRequiredMixin, DetailView):
    template_name = "user/profile_detail.html"
    model = Profile

    def get_object(self, queryset=None):
        pk = self.request.user.id
        user = User.objects.get(pk=pk)
        queryset = Profile.objects.filter(user=user)
        if queryset:
            # Get the single item from the filtered queryset
            obj = queryset.first()
        else:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
