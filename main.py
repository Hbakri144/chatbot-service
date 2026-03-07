from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

BASE_URL = "https://mutah.app/api/v2"

# ✅ نموذج للطلب اللي رح ييجي من الموقع
class ChatRequest(BaseModel):
    message: str
    storeId: str = "693317265438"
    pageSize: int = 5
    page: int = 1

def login() -> str:
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"identifier": "ai@mutah.app", "password": "123123123"},
        timeout=20,
    )

    # ✅ نطبع الرد عشان نعرف وين التوكن موجود
    print("LOGIN STATUS:", r.status_code)
    print("LOGIN JSON:", r.json())

    r.raise_for_status()

    token = r.json().get("token")
    if not token:
        raise RuntimeError("No token returned from login")
    return token

def get_products(token: str, store_id: str, page_size: int, page: int):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    params = {
        "storeId": store_id,
        "pageSize": str(page_size),
        "page": str(page),
        "withElevatedAuth": "true",
    }

    r = requests.get(
        f"{BASE_URL}/products",
        headers=headers,
        params=params,
        timeout=20,
    )

    print("PRODUCTS STATUS:", r.status_code)
    print("PRODUCTS TEXT:", r.text[:500])

    r.raise_for_status()
    return r.json()

def build_context(products_json: dict) -> str:
    # ⚠️ أحياناً شكل الـ JSON يختلف، فبنحاول نطلع قائمة المنتجات بأكثر من طريقة
    data = products_json.get("data")

    if isinstance(data, list):
        products = data
    elif isinstance(data, dict):
        products = data.get("items") or data.get("products") or data.get("data") or []
    else:
        products = []

    lines = []
    for p in products[:20]:
        name = p.get("name") or p.get("title") or "Unnamed"
        price = p.get("price") or p.get("salePrice") or p.get("finalPrice") or "N/A"
        brand = p.get("brand") or "N/A"
        battery = p.get("battery") or "N/A"
        lines.append(f"- {name} | Price: {price} | Brand: {brand} | Battery: {battery}")

    return "\n".join(lines) if lines else "No products returned."

@app.get("/")
def home():
    return {"message": "Chatbot service is running 🚀"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        token = login()
        products_json = get_products(token, req.storeId, req.pageSize, req.page)
        context = build_context(products_json)

        # ✅ حالياً بنرجّع المنتجات كنص (للتأكد إن الربط شغال)
        # بعد ما تتأكد، بنضيف ollama عشان يعمل الرد الذكي.
        return {
            "user_message": req.message,
            "products_context": context,
            "note": "إذا شايف المنتجات ظهرت، معناه الربط مع المتجر شغال ✅"
        }
    except Exception as e:
        return {"error": str(e)}