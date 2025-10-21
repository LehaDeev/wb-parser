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
        """Проверяет, есть ли текст в отзыве"""
        return bool(self.text and len(self.text.strip()) > 3)
