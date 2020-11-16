from django.views import generic
from user.models import User, Driver
from main.models import Request, Ride, Order, Withdrawal
from main.forms import RequestForm, FundAccountForm, WithdrawalForm
from django.http import HttpResponseRedirect
from user.mixins import GetLoggedInDriverMixin, MustBeDriverMixin
from main.mixins import GetLoggedInUserRideMixin, OrderNotAcceptedMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import reverse, redirect
from django.urls import reverse_lazy
from main.paystack_api import authorize, verify
from main.signals import order_accepted


class Index(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        # using SendGrid's Python Library
        # https://github.com/sendgrid/sendgrid-python
        import os
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email='dot360.official@gmail.com',
            to_emails='elishae166@gmail.com',
            subject='Sending with Twilio SendGrid is Fun',
            html_content='<strong>and easy to do anywhere, even with Python</strong>')
        apikey = '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'
        try:
            sg = SendGridAPIClient(apikey)
            # sg = SendGridAPIClient('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')

            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(apikey)
            print(e)
        if self.request.user.is_driver:
            return redirect(reverse('order_list'))
        else:
            return redirect(reverse('request_list'))


class FundAccount(LoginRequiredMixin, generic.FormView):
    form_class = FundAccountForm
    template_name = "main/fund_account.html"

    def form_valid(self, form):
        auth_response = authorize(self.request.user, form.cleaned_data.get('amount', 0))
        if auth_response is not None:
            return redirect(auth_response['data'].get('authorization_url'))
        
        messages.add_message(self.request, messages.ERROR, "An Error Occured, Paystack cannot be reached at this time")
        return self.render_to_response(self.get_context_data())


class VerifyTransaction(generic.View):
    
    def get(self, request):
        if 'reference' in request.GET:
            reference = request.GET.get('reference', "")
            response = verify(request.user, reference)
            if response.get('status', 'False'):
                # add 50 to the referral user if balance is above 200
                try:
                    if request.user.referral and request.user.account_balance >= 200 and request.user.referral_status == 'unpaid':
                        referral_user = User.objects.filter(email=request.user.referral).first()
                        referral_user.account_balance += 50
                        referral_user.save()
                        request.user.referral_status = "paid"
                        request.user.save()
                except:
                    pass
                messages.add_message(request, messages.SUCCESS, response.get('message'))
                return HttpResponseRedirect(reverse("home"))
            else:
                messages.add_message(request, messages.ERROR, response.get('message'))
                return HttpResponseRedirect(reverse("fund_account"))
        else:
            messages.add_message(request, messages.ERROR, "Improperly configured. No reference in verify. Please try again. If this continues, contact Dot360s")
            return HttpResponseRedirect(reverse('fund_account'))


class RequestCreate(LoginRequiredMixin, generic.CreateView):
    model = Request
    form_class = RequestForm
    template_name = "main/request_form.html"
    success_url = reverse_lazy("unaccepted_request")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.passenger = self.request.user
        self.object.save()
        ride = Ride.objects.get(request=self.object)
        ride.payment_method = form.cleaned_data.get('payment_method')
        ride.save()
        # if card payment was chosen 
        if form.cleaned_data.get('payment_method') == 'card':
            if self.request.user.account_balance < ride.price:
                messages.add_message(self.request, messages.ERROR, f"Insufficient Balance. Your ride costs {ride.price} naira.")
                return HttpResponseRedirect(reverse('fund_account'))
        valid_drivers = form.cleaned_data['valid_drivers']
        # valid_drivers can't be empty. if it is then form validations are not
        # effective
        for driver in valid_drivers:
            if driver.status != 'AV' or not driver.completed or not driver.user.is_active or driver.user == self.request.user:
                valid_drivers.remove(driver)
        order = Order.objects.filter(request=self.object).first()
        if valid_drivers != []:
            for driver in valid_drivers:
                order.driver.add(driver)
            order.save()
        else:
            self.object.save()
            return HttpResponseRedirect(reverse('no_avaliable_driver', kwargs={'slug': order.slug}))# no avaliable driver
        self.object.save()
        # user would be redirect to the detail page if the request is accepted
        return HttpResponseRedirect(reverse('unaccepted_request'))


class NoAvaliableDriver(generic.DetailView):
    model = Order
    template_name = "main/no_avaliable_driver.html"


class UnacceptedRequest(GetLoggedInUserRideMixin,  OrderNotAcceptedMixin, generic.DetailView):
    model = Ride
    template_name = "main/unaccepted_request.html"


class RequestListView(generic.ListView):
    template_name = "main/home.html"
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        return Request.objects.filter(passenger=self.request.user).order_by('-time')[:5]


class OrderDetail(generic.DetailView):
    model = Order 
    template_name = "main/order_detail.html"


class AnotherDriver(generic.DetailView):
    model = Order
    template_name = "main/another_driver.html"


# get a list of all the drivers of an order
# remove a driver from the main field and 
# add him to another for hold, do this and if all the drivers are exhausted then get
# start from begining with the first driver 
# if they are on the last driver then let 
# them know then take them back
    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.accepted = False
        order.save()
        order.driver.remove(order.request.driver)
        order.save()
        order.request.driver = None
        order.request.save()
        return HttpResponseRedirect(reverse('unaccepted_request')) 


class CancelRequest(generic.DeleteView):
    success_url = reverse_lazy("home")
    model = Order

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        order = self.get_object()
        success_url = self.get_success_url()
        if order.request.passenger == request.user:
            order.request.ride.status = "cancelled"
            order.request.ride.save()
            try:
                order.request.driver.status = 'AV'
                order.request.driver.save()
            except: 
                pass
            return HttpResponseRedirect(success_url)
        else:
            messages.add_message(request, messages.ERROR, "Error! You are not the creator of this request")
            return HttpResponseRedirect(reverse('home'))

            
class OrderListView(MustBeDriverMixin, generic.ListView):
    template_name = "main/home.html"
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        driver = self.request.user.driver
        return Order.objects.filter(driver=driver).exclude(request__ride__status="cancelled").order_by('-time_posted')

    def get_context_data(self, *args, **kwargs):
        kwargs = super(OrderListView, self).get_context_data(*args, **kwargs)
        
        your_orders = [ order for order in kwargs['orders'] if order.accepted == True ]
        new_orders = [ order for order in kwargs['orders'] if order.accepted == False ]

        kwargs['your_orders'] = your_orders 
        kwargs['new_orders'] = new_orders

        if self.request.user.driver.status == 'BU':
            order = Order.objects.filter(request__driver=self.request.user.driver).last()
            kwargs['current_order'] = order 
        return kwargs


class TakeOrder(MustBeDriverMixin, generic.DetailView):
    model = Order
    template_name = "main/take_order.html"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.accepted = True 
        order.save()
        driver = Driver.objects.get(user=request.user)
        order_accepted.send(sender=Order, Order=order, Driver=driver)
        return super(TakeOrder, self).get(request, *args, **kwargs)


class OngoingOrder(MustBeDriverMixin, generic.DetailView):
    model = Order
    template_name = "main/take_order.html"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.request.ride.status = "ongoing"
        order.request.ride.save()
        # charge the passenger for ride
        if order.request.ride.payment_status == "unpaid":
            if order.request.ride.payment_method == "card": 
                order.request.passenger.account_balance -= order.request.ride.price
                order.request.passenger.save()
            order.request.ride.payment_status = "paid"
            order.request.ride.save()
        return super(OngoingOrder, self).get(request, *args, **kwargs)


class VerifyCompleted(MustBeDriverMixin, generic.DetailView):
    model = Order
    template_name = "main/verify_completed.html"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order.request.ride.status = "completed"
        order.request.ride.save()
        order.request.driver.status = 'AV'
        order.request.driver.save()
        return super(VerifyCompleted, self).get(request, *args, **kwargs)


class ChangeDriverStatus(MustBeDriverMixin, GetLoggedInDriverMixin, generic.detail.BaseDetailView):
    model = Driver

    def get(self, request, *args, **kwargs):
        driver = self.request.user.driver
        if driver.status == 'AV':
            driver.status = 'NA'
            driver.save()
        elif driver.status == 'NA':
            driver.status = 'AV'
            driver.save()
        else:
            messages.add_message(request, messages.ERROR, "you are busy now, complete your current ride to change your status")
        return redirect(request.GET.get('next'))


class WithdrawalDetail(LoginRequiredMixin, generic.DetailView):
    model = Withdrawal
    template_name = "main/withdrawal_detail.html"

class WithdrawalList(LoginRequiredMixin, generic.ListView):
    model = Withdrawal
    template_name = "main/withdrawal_list.html"
    context_object_name = 'withdrawals'
    paginate_by = 10

    def get_queryset(self):
        return Withdrawal.objects.filter(user=self.request.user).order_by('-date')


class HistoryListView(LoginRequiredMixin, generic.ListView):
    model = Request 
    template_name = "main/history.html"
    context_object_name = "requests"
    paginate_by = 10


    def get_queryset(self):
        if self.request.user.is_driver:
            return Request.objects.filter(driver__user=self.request.user).order_by('-time')
        else:
            return Request.objects.filter(passenger=self.request.user).order_by('-time')   


class WithdrawalCreateView(LoginRequiredMixin, generic.CreateView):
    model = Withdrawal 
    form_class = WithdrawalForm 
    template_name = "main/withdrawal_form.html"

    def get_initial(self):
        user = self.request.user
        data = {'name': user.get_full_name()}
        past = None
        try: 
            past = Withdrawal.objects.filter(user=user).last()
            data['bank'] = past.bank
            data['account_no'] = past.account_no
        except: 
            pass
        return data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user 
        self.object.save()

        if form.cleaned_data.get('amount') > self.request.user.account_balance:
            messages.add_message(self.request, messages.ERROR, f"Insufficient Balance. Your account balance is {self.request.user.account_balance} NGN")
            return self.render_to_response(self.get_context_data(form=form))
        return super(WithdrawalCreateView, self).form_valid(form)

    def get_success_url(self):
        withdrawal = self.object
        return reverse('withdrawal_detail', kwargs={'pk': withdrawal.pk})

