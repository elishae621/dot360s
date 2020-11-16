from django.http.response import HttpResponseRedirect
from user.forms import DriverProfileUpdateForm, VehicleUpdateForm
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from user.models import Driver, User
from django.http import Http404



class MustBeDriverMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_driver:
            return True
        else:
            return False 

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return redirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)
    

class Update_view(MustBeDriverMixin):
    def setup(self, request, *args, **kwargs):
        self.driver = Driver.objects.filter(
            user=request.user).first()
        super(Update_view, self).setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        
        
        dForm = DriverProfileUpdateForm(
            request.POST, request.FILES, instance=self.driver)
        vForm = VehicleUpdateForm(request.POST, instance=self.driver.vehicle)
        
        if dForm.is_valid() and vForm.is_valid():
            return self.forms_valid(dForm, vForm)
        else:
            return self.forms_invalid(dForm, vForm)

    def forms_valid(self, dForm, vForm):
        self.driver = dForm.save()
        self.driver.vehicle = vForm.save()
        self.driver.completed = True
        self.driver.save()
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, dForm, vForm):
        return self.render_to_response(self.get_context_data(
            dForm=dForm, vForm=vForm))

    def get_context_data(self, **kwargs):
        if 'dForm' not in kwargs and 'vForm' not in kwargs:
            kwargs['dForm'] = DriverProfileUpdateForm(
                self.request.POST or None, self.request.FILES or None, instance=self.driver)
            kwargs['vForm'] = VehicleUpdateForm(
                self.request.POST or None, instance=self.driver.vehicle)
        return kwargs

    def get(self, request, *args, **kwargs):
        self.dForm = DriverProfileUpdateForm(instance=self.driver)
        self.vForm = VehicleUpdateForm(instance=self.driver.vehicle)
        return self.render_to_response(self.get_context_data())



class GetLoggedInDriverMixin(LoginRequiredMixin):
    def get_object(self, queryset=None):
        pk = self.request.user.id
        user = User.objects.get(pk=pk)
        queryset = Driver.objects.filter(user=user)
        if queryset:
            # Get the single item from the filtered queryset
            obj = queryset.first()
        else:
            raise Http404(("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


