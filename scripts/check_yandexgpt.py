# scripts/check_yandexgpt.py
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def check_yandexgpt_access():
    api_key = os.getenv('YANDEX_API_KEY')
    folder_id = os.getenv('YANDEX_FOLDER_ID')

    print("🔍 Проверка доступа к YandexGPT...")
    print(f"API Key: {'✅ Настроен' if api_key else '❌ Отсутствует'}")
    print(f"Folder ID: {'✅ Настроен' if folder_id else '❌ Отсутствует'}")

    if not api_key or not folder_id:
        print("❌ Не все настройки заполнены")
        return False

    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 50
        },
        "messages": [
            {
                "role": "user",
                "text": "Ответь одним словом: привет"
            }
        ]
    }

    try:
        print("🔄 Отправка тестового запроса...")
        response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            answer = result['result']['alternatives'][0]['message']['text']
            print(f"✅ YandexGPT доступен! Ответ: {answer}")
            return True
        elif response.status_code == 401:
            print("❌ Ошибка аутентификации. Проверьте API ключ")
        elif response.status_code == 403:
            print("❌ Нет доступа к YandexGPT. Проверьте:")
            print("   - Роль ai.languageModels.user у сервисного аккаунта")
            print("   - Активацию YandexGPT в каталоге")
        elif response.status_code == 404:
            print("❌ Каталог не найден. Проверьте folder_id")
        else:
            print(f"❌ Ошибка API: {response.status_code} - {response.text}")

        return False

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    check_yandexgpt_access()
