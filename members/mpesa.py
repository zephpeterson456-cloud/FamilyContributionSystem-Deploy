import base64
from datetime import datetime

import requests

from .models import SystemSettings


def get_access_token():
    settings_obj = SystemSettings.objects.first()

    if not settings_obj:
        raise Exception("M-Pesa settings have not been configured.")

    consumer_key = str(settings_obj.mpesa_consumer_key).strip()
    consumer_secret = str(settings_obj.mpesa_consumer_secret).strip()

    if not consumer_key or not consumer_secret:
        raise Exception(
            "M-Pesa Consumer Key or Consumer Secret is missing."
        )

    credentials = f"{consumer_key}:{consumer_secret}"

    encoded = base64.b64encode(
        credentials.encode()
    ).decode()

    url = (
        "https://sandbox.safaricom.co.ke/oauth/v1/"
        "generate?grant_type=client_credentials"
    )

    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    print("MPESA OAUTH STATUS:", response.status_code)
    print("MPESA OAUTH RESPONSE:", response.text)

    if response.status_code != 200:
        raise Exception(
            f"M-Pesa OAuth failed "
            f"({response.status_code}): {response.text}"
        )

    data = response.json()

    access_token = data.get("access_token")

    if not access_token:
        raise Exception(
            f"No access token returned by M-Pesa: {data}"
        )

    return access_token


def stk_push(phone, amount, account_reference, transaction_desc):

    settings_obj = SystemSettings.objects.first()

    if not settings_obj:
        raise Exception("M-Pesa settings have not been configured.")

    shortcode = str(settings_obj.mpesa_shortcode).strip()
    passkey = str(settings_obj.mpesa_passkey).strip()

    if not shortcode:
        raise Exception("M-Pesa shortcode is missing.")

    if not passkey:
        raise Exception("M-Pesa passkey is missing.")

    access_token = get_access_token()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password = base64.b64encode(
        f"{shortcode}{passkey}{timestamp}".encode()
    ).decode()

    url = (
        "https://sandbox.safaricom.co.ke/"
        "mpesa/stkpush/v1/processrequest"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": (
            "https://fuzzy-rights-ready-teaches"
            ".trycloudflare.com/mpesa/callback/"
        ),
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30,
    )

    print("MPESA STK STATUS:", response.status_code)
    print("MPESA STK RESPONSE:", response.text)

    try:
        return response.json()
    except ValueError:
        return {
            "error": True,
            "status_code": response.status_code,
            "response": response.text,
        }
