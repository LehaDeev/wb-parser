from typing import List
from src.api.models import WBReview
from src.ai.generator import AIGenerator

class ReviewProcessor:
    """Обработчик отзывов"""

    def __init__(self, ai_generator: AIGenerator):
        self.ai_generator = ai_generator
        self.processed_ids = set()

    def should_process(self, review: WBReview) -> bool:
        """Проверяет, нужно ли обрабатывать отзыв"""
        if review.id in self.processed_ids:
            return False

        if not review.has_text:
            return False

        if len(review.text.strip()) < 5 and any(char.isdigit() for char in review.text):
            return False

        return True

    def process_reviews(self, reviews: List[WBReview]) -> List[dict]:
        """Обрабатывает список отзывов"""
        if not reviews:
            print("📭 Нет отзывов для обработки")
            return []

        results = []

        for review in reviews:
            print(f"\n--- Обработка отзыва ---")
            print(f"📄 Отзыв ID: {review.id}")
            print(f"⭐ Рейтинг: {review.rating}/5")
            print(f"👤 Имя: {review.user_name if review.user_name else 'Не указано'}")

            # Детальная информация о текстовых полях
            if review.text:
                print(f"💬 Текст: {review.text[:100]}{'...' if len(review.text) > 100 else ''}")
            if review.pros:
                print(f"👍 Pros: {review.pros[:100]}{'...' if len(review.pros) > 100 else ''}")
            if review.cons:
                print(f"👎 Cons: {review.cons[:100]}{'...' if len(review.cons) > 100 else ''}")

            if not self.should_process(review):
                print("⏭️ Пропускаем отзыв")
                continue

            # Генерируем ответ используя полный текст отзыва
            reply = self.ai_generator.generate_reply(
                review_text=review.review_text,  # Используем свойство которое объединяет все поля
                product_name=review.product_name,
                rating=review.rating,
                user_name=review.user_name,
                pros=review.pros,
                cons=review.cons
            )

            if reply:
                results.append({
                    "review": review,
                    "reply": reply,
                    "success": True
                })
                self.processed_ids.add(review.id)
                print(f"✅ Ответ сгенерирован для отзыва {review.id}")
            else:
                results.append({
                    "review": review,
                    "reply": "",
                    "success": False
                })
                print(f"⚠️ Не удалось сгенерировать ответ для отзыва {review.id}")

        return results
