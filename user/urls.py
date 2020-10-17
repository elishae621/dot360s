from django.urls import path
from user import views as user_views


urlpatterns = [

    path('', user_views.home.as_view(), name='home'),

    path('register/', user_views.RegisterView.as_view(), name="passenger_register"),

    path('register/<slug:driver>/',
         user_views.RegisterView.as_view(), name="driver_register"),

    path('<int:pk>/',
         user_views.profile_detail_view.as_view(), name="driver_profile_detail"),

    path('update/', user_views.driver_update_profile.as_view(),
         name="driver_profile_update")

]
