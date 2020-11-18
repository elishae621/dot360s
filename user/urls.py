from django.urls import path
from user import views as user_views

app_name = "user"

urlpatterns = [
    path('register/', user_views.RegistrationView.as_view(), name="register"),
    path('login/', user_views.loginView, name="login"),
    path('logout/', user_views.logoutView, name="logout"),
    path('activate/<uidb64>/<token>/', user_views.activate, name="activate"),
    path('<int:pk>/', user_views.profile_detail_view.as_view(), name="driver_detail"),
    path('update/', user_views.driver_update_profile.as_view(),
        name="driver_update"),
]
