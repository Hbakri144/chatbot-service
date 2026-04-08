from fastapi import FastAPI
from pydantic import BaseModel

import services.products as products_module
from services.products import load_products_once, filter_products, build_context
from services.ai import ask_ai_general, ask_ai_products
from utils.language import detect_language, is_product_question
from services.memory import get_user_history,add_to_history
app = FastAPI()


class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.on_event("startup")
def startup_event():
    load_products_once()


@app.get("/")
def home():
    return {
        "message": "Chatbot service is running",
        "products_count": len(products_module.all_products)
    }


@app.get("/products")
def get_products():
    return {
        "count": len(products_module.all_products),
        "products": products_module.all_products
    }


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        lang = detect_language(req.message)
        history = get_user_history(req.user_id)

        if is_product_question(req.message):
            filtered    = filter_products(req.message, products_module.all_products)
            context     = build_context(filtered)
            ai_response = ask_ai_products(req.message, context, lang, history)
        else:
            ai_response = ask_ai_general(req.message, lang, history)

        # احفظ الرسالة والرد
        add_to_history(req.user_id, "user", req.message)
        add_to_history(req.user_id, "bot", ai_response)

        return {
            "user_id": req.user_id,
            "user_message": req.message,
            "ai_response": ai_response
        }

    except Exception as e:
        return {"error": str(e)}