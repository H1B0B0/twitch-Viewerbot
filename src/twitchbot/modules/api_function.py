import requests
import base64
import json

BASE_URL = "https://velbots.shop"

def call_register_api(username: str, password: str):
    url = f"{BASE_URL}/auth/register"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return response

def call_login_api(username: str, password: str):
    url = f"{BASE_URL}/auth/login"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return response

def call_payment_success_api(session_id: str):
    url = f"{BASE_URL}/auth/payment/success"
    params = {"session_id": session_id}
    response = requests.get(url, params=params)
    return response

def call_payment_cancel_api():
    url = f"{BASE_URL}/auth/payment/cancel"
    response = requests.get(url)
    return response

def call_create_checkout_session_api(token: str, months: int = 1):
    url = f"{BASE_URL}/auth/create-checkout"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"months": months}
    response = requests.post(url, headers=headers, json=data)
    return response

def call_register_hwid_api(token: str, hwid: str):
    url = f"{BASE_URL}/auth/register-hwid"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"hwid": hwid}
    response = requests.post(url, headers=headers, json=data)
    return response

def call_get_hwid_api(token: str):
    url = f"{BASE_URL}/auth/hwid"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def call_profile_api(token: str):
    url = f"{BASE_URL}/auth/profile"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def call_check_subscription_api(token: str):
    url = f"{BASE_URL}/auth/check-subscription"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def call_is_subscribed_api(token: str):
    url = f"{BASE_URL}/auth/is-subscribed"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def call_get_banned_status_api(token: str):
    url = f"{BASE_URL}/auth/is-banned"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def call_ban_user_api(token: str):
    url = f"{BASE_URL}/auth/ban"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Extrai o userId do token JWT
        payload = token.split('.')[1]
        # Ajusta o padding
        payload += "=" * ((4 - len(payload) % 4) % 4)
        # Decodifica e converte para JSON
        decoded = json.loads(base64.b64decode(payload))
        # Pega o ID do usuário
        user_id = decoded.get('id') or decoded.get('sub')  # Tenta ambos os campos
        
        # Envia o userId no body
        data = {"userId": user_id}
        response = requests.put(url, headers=headers, json=data)
        return response
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Ban request failed: {str(e)}")