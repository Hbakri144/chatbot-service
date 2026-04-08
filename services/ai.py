import requests
from config import OLLAMA_URL, OLLAMA_MODEL


def _call_ollama(prompt: str) -> str:
    r = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )
    data = r.json()
    print("OLLAMA RESPONSE:", data)  # ← أضف هاد
    return (
        data.get("response") or
        data.get("message", {}).get("content") or
        str(data)
    )

def ask_ai_general(message: str, lang: str = "ar", history: list = []) -> str:
    lang_instruction = (
        "جاوب بالعربي بشكل قصير وودّي."
        if lang == "ar"
        else "Reply in English, short and friendly."
    )
    history_text = "\n".join(
        [f"{'User' if h['role'] == 'user' else 'Bot'}: {h['content']}" for h in history]
    )
    prompt = f"""
You are a smart and friendly store assistant named "Store Bot".
- Respond naturally to greetings and general questions.
- Do NOT mention products unless the user asks about them.
- {lang_instruction}

Previous conversation:
{history_text}

User message: {message}
Reply:
"""
    return _call_ollama(prompt)


def ask_ai_products(message: str, context: str, lang: str = "ar", history: list = []) -> str:
    lang_instruction = (
        """جاوب بالعربي بشكل مرتب وواضح:
- ابدأ بجملة قصيرة تجاوب على السؤال
- استخدم نقاط إذا في أكثر من منتج
- اذكر الاسم والسعر بشكل واضح
- إذا ما كان في منتج مناسب قل: 'لا يوجد منتج مطابق حالياً'"""
        if lang == "ar"
        else """Reply in English in a clean format:
- Start with a short sentence answering the question
- Use bullet points if there are multiple products
- Clearly mention name and price
- If no product matches say: 'No matching product available right now'"""
    )
    history_text = "\n".join(
        [f"{'User' if h['role'] == 'user' else 'Bot'}: {h['content']}" for h in history]
    )
    prompt = f"""
You are a smart store assistant.

Important rules:
- Answer ONLY based on the products listed below.
- Do NOT invent products that are not listed.
- If asked to compare two products, compare them by price and features, do NOT say 'no matching product'.
- {lang_instruction}

Previous conversation:
{history_text}

User question:
{message}

Available products:
{context}

Reply:
"""
    return _call_ollama(prompt)