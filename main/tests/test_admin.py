from django.test import TestCase, RequestFactory
from main.admin import RequestAdmin, RideAdmin, OrderAdmin, WithdrawalAdmin
from user.models import User
from main.models import Request, Ride, Order, Withdrawal
from unittest.mock import Mock, patch
from faker import Faker
fake = Faker()


class TestRequestAdmin(TestCase):
    def setUp(self):
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.http_request = RequestFactory().get(f'/admin/user/request/{self.request.pk}/change/')
    
    def test_no_add_permissions(self):
        self.assertFalse(RequestAdmin.has_add_permission(RequestAdmin, self.http_request))

class TestRideAdmin(TestCase):
    def setUp(self):
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.ride = Ride.objects.filter(request=self.request).first()
        self.http_request = RequestFactory().get(f'/admin/user/ride/{self.ride.pk}/change/')
    
    def test_no_add_permissions(self):
        self.assertFalse(RideAdmin.has_add_permission(RideAdmin, self.http_request))


class TestOrderAdmin(TestCase):
    def setUp(self):
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

        self.request = Request.objects.create(passenger=self.passenger, 
        from_address=fake.address(), to_address=fake.address(),
        request_vehicle_type='T', intercity=True,
        city = 1, no_of_passengers=3,
        load=True)
        self.order = Order.objects.filter(request=self.request).first()
        self.http_request = RequestFactory().get(f'/admin/user/order/{self.order.pk}/change/')
    
    def test_no_add_permissions(self):
        self.assertFalse(OrderAdmin.has_add_permission(OrderAdmin, self.http_request))


class TestWithdrawalAdmin(TestCase):
    def setUp(self):
        self.user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), account_balance=3000)
        self.withdrawal = Withdrawal.objects.create(user=self.user, amount=2000, account_no=3324323333, bank="GT Bank", reason=fake.text())
        self.http_request = RequestFactory().get('/admin/main/withdrawal/')

    @patch('main.admin.messages')
    def test_confirm_withdrawal_change_from_another_model(self, message_mock):
        message_mock.return_value = Mock()
        http_request = RequestFactory().get('/admin/main/order/')
        WithdrawalAdmin.confirm_withdrawal(modelAdmin=WithdrawalAdmin, request=http_request, queryset=Withdrawal.objects.all())
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, "Oga, no dey try deadly things. go to the withdrawal model and do this stuff")

    @patch('main.admin.messages')
    def test_confirm_withdrawal_status_change(self, message_mock):
        message_mock.return_value = Mock()
        WithdrawalAdmin.confirm_withdrawal(modelAdmin=WithdrawalAdmin, request=self.http_request, queryset=Withdrawal.objects.all())
        self.withdrawal.refresh_from_db()
        self.assertEqual(self.withdrawal.status, "completed")

    @patch('main.admin.messages')
    def test_confirm_withdrawal_message_for_little_account_balance(self, message_mock):
        message_mock.return_value = Mock()
        self.user.account_balance = 2000
        self.user.save()
        self.withdrawal.amount = 3000 
        self.withdrawal.save()
        self.withdrawal.refresh_from_db()
        WithdrawalAdmin.confirm_withdrawal(modelAdmin=WithdrawalAdmin, request=self.http_request, queryset=Withdrawal.objects.all())
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, "Withdrawal amount is_less than the user's account balance")

    @patch('main.admin.messages')
    def test_confirm_withdrawal_amount_change(self, message_mock):
        message_mock.return_value = Mock()
        old_balance = self.user.account_balance
        WithdrawalAdmin.confirm_withdrawal(modelAdmin=WithdrawalAdmin, request=self.http_request, queryset=Withdrawal.objects.all())
        self.withdrawal.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.user.account_balance, old_balance - self.withdrawal.amount)

    @patch('main.admin.messages')
    def test_cancel_withdrawal_change_from_another_model(self, message_mock):
        message_mock.return_value = Mock()
        http_request = RequestFactory().get('/admin/main/order/')
        WithdrawalAdmin.cancel_withdrawal(modelAdmin=WithdrawalAdmin, request=http_request, queryset=Withdrawal.objects.all())
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, "Oga, no dey try deadly things. go to the withdrawal model and do this stuff")

    @patch('main.admin.messages')
    def test_cancel_withdrawal_status_change(self, message_mock):
        message_mock.return_value = Mock()
        WithdrawalAdmin.cancel_withdrawal(modelAdmin=WithdrawalAdmin, request=self.http_request, queryset=Withdrawal.objects.all())
        self.withdrawal.refresh_from_db()
        self.assertEqual(self.withdrawal.status, "cancelled")

    @patch('main.admin.messages')
    def test_pending_withdrawal_change_from_another_model(self, message_mock):
        message_mock.return_value = Mock()
        http_request = RequestFactory().get('/admin/main/order/')
        WithdrawalAdmin.pending_withdrawal(modelAdmin=WithdrawalAdmin, request=http_request, queryset=Withdrawal.objects.all())
        message = message_mock.call_args_list[0][0][2]
        self.assertEqual(message, "Oga, no dey try deadly things. go to the withdrawal model and do this stuff")

    @patch('main.admin.messages')
    def test_pending_withdrawal_status_change(self, message_mock):
        message_mock.return_value = Mock()
        WithdrawalAdmin.pending_withdrawal(modelAdmin=WithdrawalAdmin, request=self.http_request, queryset=Withdrawal.objects.all())
        self.withdrawal.refresh_from_db()
        self.assertEqual(self.withdrawal.status, "pending")
