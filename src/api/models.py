from typing import Dict, Any

class WBReview:
    """Модель отзыва Wildberries"""

    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get('id', '')
        self.text: str = data.get('text', '')
        self.product_details: Dict[str, Any] = data.get('productDetails', {})
        self.created_date: str = data.get('createdDate', '')
        self.answered: bool = data.get('answered', False)
        self.rating: int = data.get('productValuation', 5)
        self.was_viewed: bool = data.get('wasViewed', False)
        self.pros: str = data.get('pros', '')
        self.cons: str = data.get('cons', '')
        self.user_name: str = data.get('userName', '')

    @property
    def product_name(self) -> str:
        """Название товара"""
        return self.product_details.get('productName', '')

    @property
    def has_text(self) -> bool:
        """Проверяет, есть ли текст в отзыве (text, pros или cons)"""
        # Проверяем все возможные поля с текстом
        has_main_text = bool(self.text and len(self.text.strip()) > 3)
        has_pros = bool(self.pros and len(self.pros.strip()) > 3)
        has_cons = bool(self.cons and len(self.cons.strip()) > 3)

        return has_main_text or has_pros or has_cons

    @property
    def review_text(self) -> str:
        """Возвращает полный текст отзыва из всех доступных полей"""
        parts = []

        if self.text and self.text.strip():
            parts.append(f"Отзыв: {self.text}")

        if self.pros and self.pros.strip():
            parts.append(f"Преимущества: {self.pros}")

        if self.cons and self.cons.strip():
            parts.append(f"Недостатки: {self.cons}")

        return "\n".join(parts) if parts else "Текст отзыва отсутствует"
