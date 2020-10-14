from django.urls import path
from user import views as user_views


urlpatterns = [

    path('', user_views.user_profile_detail_view.as_view(),
         name="user_profile_detail"),

    path('<int:pk>/',
         user_views.profile_detail_view.as_view(), name="profile_detail"),

    path('update/', user_views.update_profile.as_view(),
         name="profile_update")

]
