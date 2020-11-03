from django.urls import path, re_path
from user import views as user_views


urlpatterns = [

    path('', user_views.Index.as_view(), name="home"),

    path('home/', user_views.home.as_view(), name='passenger_home'),

    path('<int:pk>/',
         user_views.profile_detail_view.as_view(), name="driver_profile_detail"),

    path('update/', user_views.driver_update_profile.as_view(),
         name="driver_profile_update"),

    path('request/', user_views.RequestCreate.as_view(), name='create_request'),

    re_path(r'^verify-transaction/', user_views.VerifyTransaction.as_view(), name='verify_transaction'),

    path('no-driver/', user_views.NoAvaliableDriver.as_view(), name='no_avaliable_driver'),

    path('delete-request/', user_views.RequestDelete.as_view(), name="delete_request"),

    path('requests/', user_views.RequestListView.as_view(), name="request_list"),

    path('orders/', user_views.OrderListView.as_view(), name="driver_orders"),

    path('order/<slug:slug>/', user_views.OrderDetail.as_view(), name="order_detail"),

    path('take-order/<slug:slug>/', user_views.TakeOrder.as_view(), name="take_order"),

    path('unaccepted-request/', user_views.UnacceptedRequest.as_view(), name="unaccepted_request"),

    path('verify-completed/<slug:slug>/', user_views.VerifyCompleted.as_view(), name = "verify_completed"), 

    path('fund-account/', user_views.FundAccount.as_view(), name="fund_account"),

    path('ongoing-order/<slug:slug>/', user_views.OngoingOrder.as_view(), name="ongoing_order"),

    path('another-driver/<slug:slug>/', user_views.AnotherDriver.as_view(), name="another_driver")
]
