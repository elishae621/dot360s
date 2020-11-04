from user.paystack_api import authorize, verify 
from django.test import TestCase
from faker import Faker
from user.models import User
from unittest.mock import Mock,patch
import pytest
import requests

fake = Faker()


class TestAuthorizeAndVerify(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'), password=fake.password())
        self.old_balance = self.passenger.account_balance

    @patch('user.paystack_api.requests.post')    
    def test_auth_response_status_is_true(self, auth_mock):
        auth_json = {
            'status': True, 
            'message': 'Authorization URL created', 
            'data': {
                'authorization_url': 'https://checkout.paystack.com/9mzlnrn30akanzp', 
                'access_code': '9mzlnrn30akanzp', 
                'reference': 'yzlei4h480'
            }
        }

        auth_mock.return_value.json.return_value = auth_json
        auth_response = authorize(user=self.passenger, amount=fake.random_int(min=1000, max=5000))
        self.assertTrue(auth_response.get('status'))

    @patch('user.paystack_api.requests.post')    
    def test_account_is_not_funded_if_status_is_false(self, auth_mock):
        auth_json = {
            'status': False, 
            'message': 'Some error', 
            'data': {
                'authorization_url': 'not avaliable', 
                'access_code': 'not avaliable', 
                'reference': 'not avaliable'
            }
        }
        auth_mock.return_value.json.return_value = auth_json
        auth_response = authorize(self.passenger, fake.random_int(min=100, max=10000))
        self.assertEqual(self.passenger.account_balance, self.old_balance)

    def test_auth_returns_none_if_unseccessful_request(self):
        auth_response = authorize(self.passenger, fake.random_int(min=100, max=4000))
        self.assertEqual(auth_response, None)

    @patch('user.paystack_api.requests.post')    
    def test_auth_returns_none_if_response_not_ok(self, auth_mock):
        auth_mock.return_value = Mock(ok=False)
        auth_response = authorize(self.passenger, fake.random_int(min=100, max=2000))
        
        self.assertEqual(auth_response, None)

    
    @patch('user.paystack_api.requests.get')
    @patch('user.paystack_api.requests.post')    
    def test_verify_response_status_is_true(self, auth_mock, verify_mock):
        auth_json = {
            'status': True, 
            'message': 'Authorization URL created', 
            'data': {
                'authorization_url': 'https://checkout.paystack.com/9mzlnrn30akanzp', 
                'access_code': '9mzlnrn30akanzp', 
                'reference': 'yzlei4h480'
            }
        }
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                "amount": 27000,
                "currency": "NGN",
                "transaction_date": "2020-10-01T11:03:09.000Z",
                "status": "success",
                "reference": "yzlei4h480",
                "domain": "test",
                "metadata": 0,
                "gateway_response": "Successful",
                "message": None,
                "channel": "card"
            }
        }
        auth_mock.return_value.json.return_value = auth_json
        verify_mock.return_value.json.return_value = verify_json
        auth_response = authorize(self.passenger, 27000)
        reference = auth_response['data'].get("reference")
        verify_response = verify(self.passenger, reference)
        self.assertTrue(verify_response.get('status'))
  
    @patch('user.paystack_api.requests.get')
    @patch('user.paystack_api.requests.post')    
    def test_user_account_balance_changes_when_transaction_verified(self, auth_mock, verify_mock):
        auth_json = {
            'status': True, 
            'message': 'Authorization URL created', 
            'data': {
                'authorization_url': 'https://checkout.paystack.com/9mzlnrn30akanzp', 
                'access_code': '9mzlnrn30akanzp', 
                'reference': 'yzlei4h480'
            }
        }
        verify_json = {
            "status": True,
            "message": "Verification successful",
            "data": {
                "amount": 27000,
                "currency": "NGN",
                "transaction_date": "2020-10-01T11:03:09.000Z",
                "status": "success",
                "reference": "yzlei4h480",
                "domain": "test",
                "metadata": 0,
                "gateway_response": "Successful",
                "message": None,
                "channel": "card"
            }
        }
        auth_mock.return_value.json.return_value = auth_json
        verify_mock.return_value.json.return_value = verify_json
        auth_response = authorize(self.passenger, 27000)
        reference = auth_response['data'].get("reference")
        verify_response = verify(self.passenger, reference)
        self.passenger.refresh_from_db()
        self.assertEqual(self.passenger.account_balance, self.old_balance + 270.00)

    def test_verify_returns_none_if_unseccessful_request(self):
        verify_response = verify(self.passenger, "somecrapreference")
        self.assertEqual(verify_response, None)

    @patch('user.paystack_api.requests.get')    
    def test_verify_returns_none_if_response_not_ok(self, verify_mock):
        verify_mock.return_value = Mock(ok=False)
        verify_response = verify(self.passenger, "some_reference")
        
        self.assertEqual(verify_response, None)


@pytest.mark.skip()
class LivePaystackTest(TestCase):
    def setUp(self):
        user = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password(), is_driver=True)
        self.driver = user.driver
        self.passenger = User.objects.create(email=fake.email(), firstname=fake.first_name(),lastname=fake.last_name(),
            phone=fake.numerify(text='080########'),
            password=fake.password())

    def test_paystack_initialization_response_keys(self):
        auth_response = authorize(self.passenger, fake.random_int(min=200, max=3000))
        auth_keys = auth_response.keys()
        with patch('user.paystack_api.requests.post') as auth_mock:
            auth_json = {
                'status': True, 
                'message': 'Authorization URL created', 
                'data': {
                    'authorization_url': 'https://checkout.paystack.com/9mzlnrn30akanzp', 
                    'access_code': '9mzlnrn30akanzp',
                    'reference': 'yzlei4h480'
                }
            }
            auth_mock.return_value.json.return_value = auth_json
            mocked_keys = auth_json.keys()

        print(list(auth_keys))
        print(list(mocked_keys))
        self.assertListEqual(list(auth_keys), list(mocked_keys))

    # I need to execute the transaction after I have initialize it 
    # before I can verify it correctly
    def test_paystack_verification_response_keys(self):
        auth_response = authorize(self.passenger, 27000)
        auth_url = auth_response['data'].get('authorization_url')
        response = requests.get(auth_url)
        reference = auth_response['data'].get('reference')
        verify_response = verify(self.passenger, reference)
        verify_keys = verify_response.keys()
        with patch('user.paystack_api.requests.get') as verify_mock:    
            verify_json = {
                "status": True,
                "message": "Verification successful",
                "data": {
                    "amount": 27000,
                    "currency": "NGN",
                    "transaction_date": "2020-10-01T11:03:09.000Z",
                    "status": "success",
                    "reference": "DG4uishudoq9OLD",
                    "domain": "test",
                    "metadata": 0,
                    "gateway_response": "Successful",
                    "message": None,
                    "channel": "card"
                }
            }
            verify_mock.return_value.json.return_value = verify_json
            mocked_keys = verify_json.keys()
        
        print(list(verify_keys))
        print(list(mocked_keys))
        self.assertListEqual(list(verify_keys), list(mocked_keys))