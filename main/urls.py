from main.views import WithdrawalCreateView, WithdrawalList
from django.urls import path
from main import views as main_views


urlpatterns = [

    path('', main_views.Index.as_view(), name="home"),

    path('request/', main_views.RequestCreate.as_view(), name='create_request'),

    path('verify-transaction/', main_views.VerifyTransaction.as_view(), name='verify_transaction'),

    path('no-driver/<slug:slug>/', main_views.NoAvaliableDriver.as_view(), name='no_avaliable_driver'),

    path('cancel/<slug:slug>/', main_views.CancelRequest.as_view(), name="cancel_request"),

    path('requests/', main_views.RequestListView.as_view(), name="request_list"),

    path('orders/', main_views.OrderListView.as_view(), name="order_list"),

    path('order/<slug:slug>/', main_views.OrderDetail.as_view(), name="order_detail"),

    path('take-order/<slug:slug>/', main_views.TakeOrder.as_view(), name="take_order"),

    path('unaccepted-request/', main_views.UnacceptedRequest.as_view(), name="unaccepted_request"),

    path('verify-completed/<slug:slug>/', main_views.VerifyCompleted.as_view(), name = "verify_completed"), 

    path('fund-account/', main_views.FundAccount.as_view(), name="fund_account"),

    path('ongoing-order/<slug:slug>/', main_views.OngoingOrder.as_view(), name="ongoing_order"),

    path('another-driver/<slug:slug>/', main_views.AnotherDriver.as_view(), name="another_driver"),

    path('change-status/', main_views.ChangeDriverStatus.as_view(), name="change_status"),

    path('create-withdrawal/', main_views.WithdrawalCreateView.as_view(), name="create_withdrawal"),

    path('withdrawal/', main_views.WithdrawalList.as_view(), name="withdrawal_list"),

    path('withdrawal/<int:pk>/', main_views.WithdrawalDetail.as_view(), name="withdrawal_detail"),

    path('history/', main_views.HistoryListView.as_view(), name="history"),
]
