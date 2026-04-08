import requests
from config import BASE_URL
from services.auth import login

# قائمة المنتجات المحملة عند تشغيل السيرفر
all_products = []


def load_products_once():
    global all_products

    token = login()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    r = requests.get(
        f"{BASE_URL}/products/ai/all",
        headers=headers,
        timeout=20,
    )
    r.raise_for_status()

    data = r.json()
    if isinstance(data, list):
        all_products = data
    elif isinstance(data, dict):
        all_products = data.get("data", [])
    else:
        all_products = []


def build_context(products: list) -> str:
    lines = []
    for p in products[:20]:
        name    = p.get("name")  or p.get("title")      or "Unnamed"
        price   = p.get("price") or p.get("salePrice")   or p.get("finalPrice") or "N/A"
        brand   = p.get("brand")   or "N/A"
        battery = p.get("battery") or "N/A"
        lines.append(f"- {name} | Price: {price} | Brand: {brand} | Battery: {battery}")
    return "\n".join(lines) if lines else "No products returned."


def filter_products(message: str, products: list) -> list:
    msg = message.lower().strip()

    def get_price(p):
        price = p.get("price") or p.get("salePrice") or p.get("finalPrice") or 999999
        try:
            return float(price)
        except Exception:
            return 999999

    if "ارخص" in msg or "cheap" in msg:
        return sorted(products, key=get_price)[:5]

    if "اغلى" in msg or "expensive" in msg:
        return sorted(products, key=get_price, reverse=True)[:5]

    keywords = ["ورد", "bouquet", "flower", "gift", "box", "love", "birthday"]
    for k in keywords:
        if k in msg:
            return [p for p in products if k in (p.get("name", "").lower())][:5]

    return [
        p for p in products
        if any(word in (p.get("name", "").lower()) for word in msg.split())
    ][:5]
