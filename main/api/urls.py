from django.urls import path 
from main.api.views import (
    RequestCreateView, 
    RequestDetailView,
    RideDetailView,
    OrderDetailView, 
    WithdrawalDetailView,
    VerifyTransactionView,
    RequestListView,
    RideListView,
    OrderListView,
    WithdrawalListView,
    AnotherDriverView,
    CancelRequestView,
    TakeOrderView,
    OngoingOrderView,
    VerifyCompletedView,
    ChangeDriverStatusView,
)

app_name = 'api_main'

urlpatterns = [
    path('change-driver-status', ChangeDriverStatusView.as_view(), name='change_driver_status'),
    path('verify-completed', VerifyCompletedView.as_view(), name='verify_completed'),
    path('ongoing-order', OngoingOrderView.as_view(), name='ongoing_order'),
    path('take-order', TakeOrderView.as_view(), name='take_order'),
    path('cancel-request', CancelRequestView.as_view(), name='cancel_request'),
    path('another-driver', AnotherDriverView.as_view(), name='another_driver'),
    path('ride-list', RideListView.as_view(), name='ride_list'),
    path('order-list', OrderListView.as_view(), name='order_list'),
    path('withdrawal-list', WithdrawalListView.as_view(), name='withdrawal_list'),
    path('request-list', RequestListView.as_view(), name='request_list'),
    path('create-request', RequestCreateView.as_view(), name='create_request'),
    path('verify', VerifyTransactionView.as_view(), name='verify'),
    path('request', RequestDetailView.as_view(), name='request'),
    path('ride', RideDetailView.as_view(), name='ride'),
    path('order', OrderDetailView.as_view(), name='order'),
    path('withdrawal', WithdrawalDetailView.as_view(), name='withdrawal')
]