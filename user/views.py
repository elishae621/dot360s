from django.views import generic
from django.shortcuts import render, reverse
from django.contrib.auth.tokens import default_token_generator 
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage 
from django.http import HttpResponse 
from django.shortcuts import render 
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, authenticate, logout 
from django.http import HttpResponseRedirect 

from user.models import Driver, User
from user.mixins import Update_view, GetLoggedInDriverMixin
from user.forms import RegistrationForm, LoginForm


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


class RegistrationView(generic.CreateView):
    template_name = "user/signup.html"
    model = User 
    form_class = RegistrationForm

    def form_valid(self, form):
        user = form.save(commit=False) 
        user.is_active = False 
        user.save() 
        current_site = get_current_site(self.request)
        mail_subject = 'Activate your account.'
        message = render_to_string('user/acc_active_email.html', {
            'user': user, 
            'domain': current_site.domain, 
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(mail_subject, message, to=[to_email], from_email='dot360.official@gmail.com')
        email.send()
        return HttpResponse('Please confirm your email address to complete registration')
        
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None 
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True 
            user.save() 
            return HttpResponse('Your email has been confirmed. Now you can login')
        else: 
            return HttpResponse('Activation link is invalid')


def loginView(request):
    
    context = {}
    
    user = request.user 
    if user.is_authenticated:
        return HttpResponseRedirect(reverse('home')) 
    
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
    
    else:
        form = LoginForm() 
    
    context['form'] = form 

    return render(request, "user/login.html", context)


def logoutView(request):
    logout(request)
    context = {}
    return render(request, "user/logout.html", context)


class profile_detail_view(GetLoggedInDriverMixin, generic.DetailView):
    template_name = "user/profile_detail.html"
    model = Driver


class driver_update_profile(GetLoggedInDriverMixin, Update_view, generic.UpdateView):
    """inheriting the main deadly mixin I wrote"""
    template_name = "user/driver_profile_update.html"
    model = Driver

    def get_success_url(self):
        return reverse('driver_profile_detail', kwargs={'pk': self.request.user.pk})

