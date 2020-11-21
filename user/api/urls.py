from django.urls import path 
from user.api.views import (
    RegistrationView,
    ObtainAuthTokenView,
    ProfileView,
    UserDetailView,
    DriverDetailView,
    VehicleDetailView,
)

app_name = 'api_user'

urlpatterns = [
    path('vehicle', VehicleDetailView.as_view(), name='vehicle'),
    path('driver', DriverDetailView.as_view(), name='driver'),
    path('user', UserDetailView.as_view(), name='user'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('login', ObtainAuthTokenView.as_view(), name='login'),
    path('register', RegistrationView.as_view(), name='register'),
]