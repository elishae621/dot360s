from django.urls import path
from main import views as main_views


urlpatterns = [

    path('', main_views.Index.as_view(), name="home"),

    path('home/', main_views.home.as_view(), name='passenger_home'),

    path('request/', main_views.RequestCreate.as_view(), name='create_request'),

    path('verify-transaction/', main_views.VerifyTransaction.as_view(), name='verify_transaction'),

    path('no-driver/', main_views.NoAvaliableDriver.as_view(), name='no_avaliable_driver'),

    path('cancel/', main_views.CancelRequest.as_view(), name="cancel_request"),

    path('requests/', main_views.RequestListView.as_view(), name="request_list"),

    path('orders/', main_views.OrderListView.as_view(), name="driver_orders"),

    path('order/<slug:slug>/', main_views.OrderDetail.as_view(), name="order_detail"),

    path('take-order/<slug:slug>/', main_views.TakeOrder.as_view(), name="take_order"),

    path('unaccepted-request/', main_views.UnacceptedRequest.as_view(), name="unaccepted_request"),

    path('verify-completed/<slug:slug>/', main_views.VerifyCompleted.as_view(), name = "verify_completed"), 

    path('fund-account/', main_views.FundAccount.as_view(), name="fund_account"),

    path('ongoing-order/<slug:slug>/', main_views.OngoingOrder.as_view(), name="ongoing_order"),

    path('another-driver/<slug:slug>/', main_views.AnotherDriver.as_view(), name="another_driver")
]
