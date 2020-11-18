from django.urls import path 
from user.api.views import (
    RegistrationView,
)

app_name = 'api_user'

urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),v
]