import requests
from config import BASE_URL, API_USER, API_PASS


def login() -> str:
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"identifier": API_USER, "password": API_PASS},
        timeout=20
    )
    r.raise_for_status()
    token = r.json().get("token")
    if not token:
        raise RuntimeError("No token returned from login")
    return token
