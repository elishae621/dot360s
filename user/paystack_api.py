import requests
from dot360s.settings import PAYSTACK_PUBLIC_KEY, PAYSTACK_SECRET_KEY
from user.models import Ride


authorization_url = "https://api.paystack.co/transaction/initialize/"


def authorize(user, amount):
    headers = {
        'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}', 
        'Content_Type': "application/json"
    }
    data = {
        'key': f"{PAYSTACK_PUBLIC_KEY}",
        'email': user.email,
        'phone': user.phone,
        'firstname': user.firstname,
        'lastname': user.lastname,
        "amount": amount,
        'metadata': {},
        'label': "Funding Account",
        'callback_url': "http://localhost:8080/verify-transaction/"
    }
    try:
        response = requests.post("https://api.paystack.co/transaction/initialize/", data=data, headers=headers)
        response_json = response.json()
        if response.ok:
            return response_json
    except:
        return None


def verify(user, reference):
    headers = {'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}
    try:
        response = requests.get(f"https://api.paystack.co/transaction/verify/:{reference}", headers=headers)
        response_json = response.json()
        if response.ok:
            if response_json.get('status'):
                user.account_balance += response_json['data'].get('amount')
                user.save()
            return response_json
    except:
        return None