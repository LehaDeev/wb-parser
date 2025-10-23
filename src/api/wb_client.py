import requests
import time
from typing import List, Dict, Any
from .rate_limiter import RateLimiter
from .models import WBReview
from src.config.settings import settings
from src.config.constants import *

class WBAPIClient:
    """Клиент для работы с API Wildberries"""

    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.base_url = settings.WB_BASE_URL
        self.headers = {
            "Authorization": settings.WB_API_KEY,
            "Content-Type": "application/json"
        }
        self.rate_limiter = RateLimiter(delay=settings.REQUEST_DELAY)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполняет запрос к API"""
        if self.test_mode:
            return {"error": False, "data": None}

        self.rate_limiter.wait_if_needed()

        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)

            if response.status_code == HTTP_UNAUTHORIZED:
                print("❌ Ошибка 401: Неавторизован")
                return {"error": True, "errorText": "Unauthorized"}

            if response.status_code == HTTP_TOO_MANY_REQUESTS:
                print("⚠️ Превышен лимит запросов, ждем...")
                time.sleep(1)
                return self._make_request(method, endpoint, **kwargs)

            response.raise_for_status()

            if response.status_code == 204:
                return {"error": False, "data": None}

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return {"error": True, "errorText": str(e)}
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return {"error": True, "errorText": str(e)}

    def has_unseen_feedbacks(self) -> bool:
        """Проверяет наличие непросмотренных отзывов"""
        if self.test_mode:
            print("🔧 ТЕСТОВЫЙ РЕЖИМ: Есть непросмотренные отзывы")
            return True

        print("🔍 Проверка непросмотренных отзывов...")
        result = self._make_request("GET", "new-feedbacks-questions")

        if result.get("error"):
            return False

        data = result.get("data", {})
        has_new_feedbacks = data.get("hasNewFeedbacks", False)

        print(f"📊 Непросмотренные отзывы: {'ЕСТЬ' if has_new_feedbacks else 'нет'}")
        return has_new_feedbacks

    def get_unanswered_reviews(self) -> List[WBReview]:
        """Получает список неотвеченных отзывов"""
        if self.test_mode:
            return self._get_test_reviews()

        print("🔍 Получение списка отзывов...")

        params = {
            "isAnswered": False,
            "take": 50,
            "skip": 0,
            "order": "dateDesc"
        }

        result = self._make_request("GET", "feedbacks", params=params)

        if result.get("error"):
            print(f"❌ Ошибка при получении отзывов: {result.get('errorText')}")
            return []

        data = result.get("data", {})
        feedbacks_data = data.get("feedbacks", [])

        print(f"📊 Получено сырых данных: {len(feedbacks_data)} отзывов")

        # Детальная информация о полученных данных
        for i, feedback in enumerate(feedbacks_data):
            has_text = bool(feedback.get('text', '').strip())
            has_pros = bool(feedback.get('pros', '').strip())
            has_cons = bool(feedback.get('cons', '').strip())
            is_answered = feedback.get('answered', True)

            print(f"   {i+1}. ID: {feedback.get('id', 'N/A')}")
            print(f"      Текст: {'✅ Есть' if has_text else '❌ Нет'}")
            print(f"      Pros: {'✅ Есть' if has_pros else '❌ Нет'}")
            print(f"      Cons: {'✅ Есть' if has_cons else '❌ Нет'}")
            print(f"      Отвечен: {'✅ Да' if is_answered else '❌ Нет'}")
            print(f"      Рейтинг: {feedback.get('productValuation', 'N/A')}")

            # Показываем превью всех текстовых полей
            if has_text:
                print(f"      Текст: {feedback.get('text', '')[:50]}...")
            if has_pros:
                print(f"      Pros: {feedback.get('pros', '')[:50]}...")
            if has_cons:
                print(f"      Cons: {feedback.get('cons', '')[:50]}...")

        # Фильтруем отзывы с любым текстом (text, pros или cons)
        reviews = [WBReview(item) for item in feedbacks_data
                if (item.get('text') and len(item.get('text', '').strip()) > 3)
                or (item.get('pros') and len(item.get('pros', '').strip()) > 3)
                or (item.get('cons') and len(item.get('cons', '').strip()) > 3)]

        print(f"📥 После фильтрации: {len(reviews)} неотвеченных отзывов с текстом/pros/cons")
        return reviews

    def post_reply_to_review(self, review_id: str, reply_text: str) -> bool:
        """Отправляет ответ на отзыв"""
        if self.test_mode:
            print(f"🔧 ТЕСТОВЫЙ РЕЖИМ: Ответ для отзыва {review_id}")
            print(f"📝 Текст ответа: {reply_text}")
            print("✅ Ответ успешно 'отправлен' (тестовый режим)")
            return True

        print(f"📤 Отправка ответа на отзыв {review_id}...")

        payload = {
            "id": review_id,
            "text": reply_text[:5000]
        }

        result = self._make_request("POST", "feedbacks/answer", json=payload)

        if result.get("error"):
            print(f"❌ Ошибка при отправке ответа: {result.get('errorText')}")
            return False

        print(f"✅ Ответ успешно отправлен на отзыв {review_id}")
        return True

    def get_unanswered_count(self) -> dict:
        """Получает количество неотвеченных отзывов"""
        if self.test_mode:
            return {
                "countUnanswered": 1,
                "countUnansweredToday": 1,
                "valuation": "4.5",
                "feedbacksCount": 1,
                "questionsCount": 0
            }

        try:
            print("📊 Получение статистики...")
            result = self._make_request("GET", "feedbacks/count-unanswered")

            if result.get("error"):
                print(f"❌ Ошибка при получении статистики: {result.get('errorText')}")
                return {
                    "countUnanswered": 0,
                    "countUnansweredToday": 0,
                    "valuation": "N/A"
                }

            data = result.get("data", {})

            # Логируем статистику
            unanswered = data.get('countUnanswered', 0)
            today = data.get('countUnansweredToday', 0)
            valuation = data.get('valuation', 'N/A')

            print(f"📊 Статистика получена: {unanswered} неотвеченных, {today} новых сегодня")

            return data

        except Exception as e:
            print(f"⚠️ Ошибка получения статистики: {e}")
            return {
                "countUnanswered": 0,
                "countUnansweredToday": 0,
                "valuation": "N/A"
            }

    def _get_test_reviews(self) -> List[WBReview]:
        """Возвращает тестовые отзывы"""
        test_data = [
            {
                "id": "test_review_1",
                "text": "Отличный товар! Качество на высоте, доставка быстрая.",
                "productDetails": {"productName": "Тестовый товар 1"},
                "createdDate": "2024-01-01",
                "answered": False,
                "productValuation": 5,
                "wasViewed": False,
                "pros": "Качество, доставка",
                "cons": "",
                "userName": "Анна"
            },
            {
                "id": "test_review_2",
                "text": "",
                "productDetails": {"productName": "Тестовый товар 2"},
                "createdDate": "2024-01-01",
                "answered": False,
                "productValuation": 5,
                "wasViewed": True,
                "pros": "Красивый сарафан, отличное качество",
                "cons": "",
                "userName": "Анастасия"
            }
        ]
        return [WBReview(item) for item in test_data]
