import os
import requests

CDN_PURGE_URL = os.getenv("CDN_PURGE_URL", "https://api.cdn-provider.com/v1/purge")
CDN_API_KEY = os.getenv("CDN_API_KEY", "")

def purge_cdn_cache():
    """
    Отправляет запрос в службу доставки контента (CDN) для сброса кеша
    при изменении источника данных.
    """
    if not CDN_API_KEY:
        print("Предупреждение: CDN_API_KEY не задан. Сброс кэша пропущен.")
        return False

    headers = {
        "Authorization": f"Bearer {CDN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "purge_everything": True
    }

    try:
        response = requests.post(CDN_PURGE_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print("Кэш CDN успешно очищен. Новые данные доступны пользователям.")
            return True
        else:
            print(f"Ошибка сброса кэша CDN: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Ошибка при обращении к CDN API: {e}")
        return False

if __name__ == "__main__":
    purge_cdn_cache()