from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from user.models import User
from main.models import Request, Ride
from django.http import Http404
from django.urls import reverse_lazy



class GetLoggedInUserRideMixin(LoginRequiredMixin):
    def get_object(self, queryset=None):
        pk = self.request.user.id
        user = User.objects.get(pk=pk)
        request = Request.objects.filter(passenger=user).last()
        queryset = Ride.objects.filter(request=request)
        if queryset:
            # Get the single item from the filtered queryset
            obj = queryset.last()
        else:
            raise Http404(("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
        

class OrderNotAcceptedMixin(UserPassesTestMixin):
    def test_func(self):
        ride = self.get_object()
        order = ride.request.request_order
        order.refresh_from_db()
        if order.accepted:
            return False
        else:
            return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            ride = self.get_object()
            order = ride.request.request_order
            return redirect(reverse_lazy('order_detail', kwargs={'slug': order.slug}))
        return super().dispatch(request, *args, **kwargs)
    