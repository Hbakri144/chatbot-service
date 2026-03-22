from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BASE_URL = os.getenv("BASE_URL")
all_products = []


class ChatRequest(BaseModel):
    message: str


def login() -> str:
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "identifier": os.getenv("API_USER"),
            "password": os.getenv("API_PASS")
        },
        timeout=20
    )

    print("LOGIN STATUS:", r.status_code)
    print("LOGIN JSON:", r.json())

    r.raise_for_status()

    token = r.json().get("token")
    if not token:
        raise RuntimeError("No token returned from login")

    return token

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

    print("PRODUCTS STATUS:", r.status_code)
    print("PRODUCTS TEXT:", r.text[:500])

    r.raise_for_status()

    data = r.json()

    if isinstance(data, list):
        all_products = data
    elif isinstance(data, dict):
        all_products = data.get("data", [])
    else:
        all_products = []


def build_context(products) -> str:
    lines = []

    for p in products[:20]:
        name = p.get("name") or p.get("title") or "Unnamed"
        price = p.get("price") or p.get("salePrice") or p.get("finalPrice") or "N/A"
        brand = p.get("brand") or "N/A"
        battery = p.get("battery") or "N/A"

        lines.append(
            f"- {name} | Price: {price} | Brand: {brand} | Battery: {battery}"
        )

    return "\n".join(lines) if lines else "No products returned."

def filter_products(message, products):
    msg = message.lower().strip()

    # تنظيف السعر
    def get_price(p):
        price = p.get("price") or p.get("salePrice") or p.get("finalPrice") or 999999
        try:
            return float(price)
        except:
            return 999999

    #  أرخص
    if "ارخص" in msg or "cheap" in msg:
        return sorted(products, key=get_price)[:5]

    #  أغلى
    if "اغلى" in msg or "expensive" in msg:
        return sorted(products, key=get_price, reverse=True)[:5]

    #  كلمات عامة (فئات)  
    keywords = [
        "ورد", "bouquet", "flower", "gift", "box", "love", "birthday"
    ]

    for k in keywords:
        if k in msg:
            return [
                p for p in products
                if k in (p.get("name", "").lower())
            ][:5]

    #  بحث عام (أي كلمة)
    return [
        p for p in products
        if any(word in (p.get("name", "").lower()) for word in msg.split())
    ][:5]


def ask_ai(message, context):
    import requests

    prompt = f"""
أنت مساعد متجر ذكي.

مهم جداً:
- جاوب فقط اعتماداً على المنتجات المعطاة.
- لا تخترع منتجات غير موجودة.
- إذا ما كان في منتج مناسب، قل: "لا يوجد منتج مطابق حالياً."
- جاوب بالعربي بشكل قصير وواضح.
- إذا كان السؤال عن الأرخص أو الأغلى، اذكر اسم المنتج وسعره.
- إذا كان هناك أكثر من خيار مناسب، اذكر أفضل 3 فقط.

سؤال المستخدم:
{message}

المنتجات المتاحة:
{context}

الجواب:
"""

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    return r.json()["response"]




@app.on_event("startup")
def startup_event():
    load_products_once()


@app.get("/")
def home():
    return {
        "message": "Chatbot service is running",
        "products_count": len(all_products)
    }


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        filtered = filter_products(req.message, all_products)
        context = build_context(filtered)
        ai_response = ask_ai(req.message, context)

        return {
            "user_message": req.message,
            "ai_response": ai_response
        }

    except Exception as e:
        return {"error": str(e)}