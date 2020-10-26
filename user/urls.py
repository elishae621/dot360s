from django.urls import path
from user import views as user_views


urlpatterns = [

    path('', user_views.home.as_view(), name='home'),

    path('<int:pk>/',
         user_views.profile_detail_view.as_view(), name="driver_profile_detail"),

    path('update/', user_views.driver_update_profile.as_view(),
         name="driver_profile_update"),

    path('request/', user_views.RequestView.as_view(), name='create_request'),

    path('verify-transaction/<str:reference>/', user_views.VerifyTransaction.as_view(), name='verify_transaction'),

    path('price/', user_views.PriceConfirmation.as_view(), name='price_confirmation'),

    path('no-driver/', user_views.NoAvaliableDriver.as_view(), name='no_avaliable_driver'),

    path('update-request/', user_views.RequestUpdate.as_view(), name="update_request"),

    path('delete_request/', user_views.RequestDelete.as_view(), name="delete_request"),

]
