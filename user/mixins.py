from django.views.generic.edit import FormView
from user.forms import DriverProfileUpdateForm, VehicleUpdateForm
from django.shortcuts import redirect, reverse
from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from user.models import Vehicle, User, Driver
from django.http import Http404
from django.views.generic.detail import DetailView


class Update_view(FormView):

    def setUp(self, request, *args, **kwargs):
        self.driver = User.objects.filter(user_type=1).filter(
            email=request.user.email).first()
        super(Update_view, self).setUp(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        dForm = DriverProfileUpdateForm(
            request.POST, request.FILES, instance=self.driver.driver_profile)
        vForm = VehicleUpdateForm(request.POST, instance=self.driver.vehicle)
        if dForm.is_valid() and vForm.is_valid():
            return self.forms_valid(dForm, vForm)
        else:
            return self.forms_invalid(dForm, vForm)

    def forms_valid(self, dForm, vForm):
        self.driver.driver_profile = dForm.save()
        self.driver.vehicle = vForm.save()
        return redirect(self.success_url)

    def forms_invalid(self, dForm, pForm, vForm):
        return self.render_to_response(self.get_context_data(
            dForm=dForm, vForm=vForm))

    def get(self, request, *args, **kwargs):
        self.dForm = DriverProfileUpdateForm(instance=self.driver.Driver)
        self.vForm = VehicleUpdateForm(instance=self.driver.vehicle)
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        if 'dForm' not in kwargs and 'vForm' not in kwargs:
            kwargs['dForm'] = DriverProfileUpdateForm(
                self.request.POST, self.request.FILES, instance=self.driver.Driver)
            kwargs['vForm'] = VehicleUpdateForm(
                self.request.POST, instance=self.driver.vehicle)
        return kwargs


class GetLoginedInUserMixin(LoginRequiredMixin, DetailView):
    def get_object(self, queryset=None):
        pk = self.request.user.id
        user = User.objects.get(pk=pk)
        queryset = Driver.objects.filter(user=user)
        if queryset:
            # Get the single item from the filtered queryset
            obj = queryset.first()
        else:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
