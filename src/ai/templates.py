"""Шаблоны ответов"""

from src.config.constants import DEFAULT_RESPONSES

def get_fallback_response(rating: int, user_name: str = "") -> str:
    """Возвращает резервный ответ"""
    if rating >= 4:
        template = DEFAULT_RESPONSES["positive"]
    elif rating <= 2:
        template = DEFAULT_RESPONSES["negative"]
    else:
        template = DEFAULT_RESPONSES["neutral"]

    return replace_name_placeholder(template, user_name)

def replace_name_placeholder(text: str, user_name: str) -> str:
    """Заменяет плейсхолдер [имя]"""
    if user_name and user_name.strip():
        clean_name = user_name.strip()
        return text.replace("[имя]", clean_name)
    return text.replace("[имя]", "")
