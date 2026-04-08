PRODUCT_KEYWORDS = [
    # عربي
    "منتج", "سعر", "ارخص", "اغلى", "باقة", "ورد", "هدية", "طلب",
    "بكم", "كم سعر", "فرق", "أحسن", "انسب", "اشتري", "اقترح",
    "عندكم", "متوفر", "توصية", "بوكيه",
    # إنجليزي
    "product", "price", "cheap", "expensive", "bouquet", "flower",
    "gift", "box", "buy", "recommend", "compare", "difference",
    "birthday", "love", "available", "offer"
]

GENERAL_KEYWORDS = [
    # عربي
    "كيفك", "كيف حالك", "مرحبا", "هلا", "أهلا", "صباح", "مساء",
    "شكرا", "شكراً", "يسلمو", "ممتاز", "تمام", "ساعدني",
    "مين انت", "شو اسمك", "من انت",
    # إنجليزي
    "hello", "hi", "hey", "how are you", "thanks", "thank you",
    "who are you", "what are you", "good morning", "good evening"
]


def detect_language(message: str) -> str:
    arabic_chars = sum(1 for c in message if "\u0600" <= c <= "\u06FF")
    return "ar" if arabic_chars > len(message) * 0.15 else "en"


def is_product_question(message: str) -> bool:
    """Returns True if the message is about products, False if it's a general question."""
    msg = message.lower().strip()

    for kw in GENERAL_KEYWORDS:
        if kw in msg:
            return False

    for kw in PRODUCT_KEYWORDS:
        if kw in msg:
            return True

    # رسالة قصيرة بدون كيورد → عامة
    if len(msg.split()) < 4:
        return False

    return True  # افتراضي: سؤال منتجات
