import requests
import json
import os

# ------------------- Загрузка секретов -------------------
def load_secrets():
    secrets_path = os.path.join(os.path.dirname(__file__), "secret.json")
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(
            "Файл secret.json не найден. Создайте его в той же папке, что и скрипт, "
            "с полями USER_AGENT, ACCESS_TOKEN, USER_ID."
        )
    with open(secrets_path, "r", encoding="utf-8") as f:
        return json.load(f)

SECRETS = load_secrets()

USER_AGENT = SECRETS["USER_AGENT"]
ACCESS_TOKEN = SECRETS["ACCESS_TOKEN"]
USER_ID = SECRETS["USER_ID"]

BASE_URL = "https://dragonfly-flash.ru"

# ------------------- Вспомогательные функции -------------------
def input_user(possible: list, text: str):
    while True:
        print(text)
        user_input = input(">>> ")
        if user_input not in possible:
            print("Введите свой выбор")
        else:
            return user_input

# Базовые заголовки, общие для большинства запросов
BASE_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Accept-Language": "ru,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://dragonfly-flash.ru/?id=Wonordel",
    "Origin": "https://dragonfly-flash.ru",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "DNT": "1",
    "Priority": "u=4",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

COOKIES = {"access_token": ACCESS_TOKEN}

# ------------------- Функции API -------------------

def publish_post(text: str) -> dict:
    url = f"{BASE_URL}/api/upload_post_modernized"
    files = {"description": (None, text, "text/plain")}
    response = requests.post(url, headers=BASE_HEADERS, cookies=COOKIES, files=files)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def get_profile(username: str, user_id: int) -> dict:
    url = f"{BASE_URL}/api/get_profile"
    params = {"username": username, "current_user_id": user_id}
    response = requests.get(url, headers=BASE_HEADERS, cookies=COOKIES, params=params)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def print_profile(profile_data: dict) -> None:
    print(f"ID пользователя: {profile_data.get('user_id')}")
    print(f"Имя пользователя: {profile_data.get('username')}")
    print(f"Статус: {profile_data.get('status')}")
    print(f"О себе: {profile_data.get('about')}")
    print(f"Аватар: {profile_data.get('avatar_url')}")
    print(f"Рейтинг: {profile_data.get('rating')}")
    print(f"Онлайн: {'Да' if profile_data.get('is_online') else 'Нет'}")
    print(f"Приватный профиль: {'Да' if profile_data.get('is_private') else 'Нет'}")
    posts = profile_data.get('posts', [])
    print(f"Количество постов: {len(posts)}")
    if posts:
        print("\nПоследние 3 поста:")
        for post in posts[:3]:
            desc = post.get('description', '') or '[без описания]'
            print(f"  - {desc[:70]}... (ID {post.get('post_id')}, лайков: {post.get('likes_count')})")

def delete_post(post_id: int) -> dict:
    url = f"{BASE_URL}/api/post/{post_id}"
    response = requests.delete(url, headers=BASE_HEADERS, cookies=COOKIES)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def get_comments(post_id: int, user_id: int) -> dict:
    url = f"{BASE_URL}/api/get_comments/{post_id}"
    params = {"user_id": user_id}
    response = requests.get(url, headers=BASE_HEADERS, cookies=COOKIES, params=params)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def print_comments(comments_list: list) -> None:
    if not comments_list:
        print("Комментариев нет.")
        return
    print(f"Всего комментариев: {len(comments_list)}")
    for i, comment in enumerate(comments_list, 1):
        author = comment.get('author', {}).get('username', 'Неизвестный')
        text = comment.get('text', '')
        date = comment.get('created_at', '')
        print(f"{i}. {author} ({date}): {text}")

def get_unread_count() -> dict:
    url = f"{BASE_URL}/api/unread_count"
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    response = requests.get(url, headers=headers, cookies=COOKIES)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def print_unread_count(result: dict) -> None:
    """Выводит количество непрочитанных уведомлений в читаемом виде."""
    if result['status_code'] != 200:
        print("Ошибка при получении количества уведомлений:")
        print(json.dumps(result['data'], indent=4, ensure_ascii=False))
        return
    data = result['data']
    if isinstance(data, int):
        print(f"Непрочитанных уведомлений: {data}")
    elif isinstance(data, dict):
        if 'unread_count' in data:
            print(f"Непрочитанных уведомлений: {data['unread_count']}")
        elif 'count' in data:
            print(f"Непрочитанных уведомлений: {data['count']}")
        else:
            print("Ответ сервера:")
            print(json.dumps(data, indent=4, ensure_ascii=False))
    else:
        print("Неожиданный формат ответа:")
        print(json.dumps(data, indent=4, ensure_ascii=False))

def get_feed(feed_type: str = "all", limit: int = 20, offset: int = 0) -> dict:
    url = f"{BASE_URL}/api/feed"
    params = {"type": feed_type, "limit": limit, "offset": offset}
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    response = requests.get(url, headers=headers, cookies=COOKIES, params=params)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def print_feed(feed_data: dict) -> None:
    feed_list = feed_data.get("feed", [])
    if not feed_list:
        print("Лента пуста.")
        return
    print(f"Постов в ленте: {len(feed_list)}")
    for i, post in enumerate(feed_list, 1):
        post_id = post.get("post_id", "N/A")
        author = post.get("author_name", "Неизвестный")
        description = post.get("description", "") or "[без описания]"
        likes = post.get("likes_count", 0)
        comments = post.get("comments_count", 0)
        created = post.get("created_at", "")
        is_liked = "❤️" if post.get("is_liked") else "🤍"
        print(f"{i}. {author} ({created}) — ID: {post_id}")
        print(f"   {description[:100]}{'...' if len(description) > 100 else ''}")
        print(f"   👍 {likes}  💬 {comments}  {is_liked}")
        photos = post.get("photos", [])
        if photos:
            print(f"   📷 {len(photos)} фото")
        audios = post.get("audios", [])
        if audios:
            print(f"   🎵 {len(audios)} аудио")
        poll = post.get("poll")
        if poll:
            print(f"   📊 Опрос: {poll.get('question')}")
        print()

# ------------------- Основное меню -------------------

if __name__ == "__main__":
    while True:
        choice = input_user(['0', '1', '2', '3', '4', '5', '6'],
                            "0. Вывести JSON пользователя\n"
                            "1. Сделать текстовый пост\n"
                            "2. Удалить пост по ID\n"
                            "3. Показать комментарии к посту\n"
                            "4. Показать количество непрочитанных уведомлений\n"
                            "5. Показать ленту (по умолчанию all, 20 постов)\n"
                            "6. Выйти")
        
        if choice == '0':
            print(json.dumps(get_profile("Wonordel", USER_ID).get("data", {}), indent=4, ensure_ascii=False))
        
        elif choice == '1':
            print("Введите пост (``` чтобы закончить, ```` чтобы отменить)")
            lines = []
            while True:
                line = input(">>> ")
                if line == '````':
                    print("Отменено.")
                    lines = None
                    break
                if line == '```':
                    break
                lines.append(line)
            if lines is not None:
                text = '\n'.join(lines)
                publish = publish_post(text) 
                print(f"Код статуса: {publish['status_code']}")
                print(f"Данные: {publish['data']}")
        
        elif choice == '2':
            try:
                post_id = int(input("Введите ID поста для удаления: "))
                result = delete_post(post_id)
                print(f"Код статуса: {result['status_code']}")
                print(f"Ответ сервера: {result['data']}")
            except ValueError:
                print("ID должен быть числом.")
        
        elif choice == '3':
            try:
                post_id = int(input("Введите ID поста: "))
                result = get_comments(post_id, USER_ID)
                print(f"Код статуса: {result['status_code']}")
                if result['status_code'] == 200:
                    if isinstance(result['data'], list):
                        print_comments(result['data'])
                    else:
                        print("Неожиданный формат ответа:")
                        print(json.dumps(result['data'], indent=4, ensure_ascii=False))
                else:
                    print("Ошибка при получении комментариев:")
                    print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            except ValueError:
                print("ID должен быть числом.")
        
        elif choice == '4':
            result = get_unread_count()
            print(f"Код статуса: {result['status_code']}")
            print_unread_count(result)
        
        elif choice == '5':
            feed_type = input("Введите тип ленты (по умолчанию 'all'): ") or "all"
            try:
                limit = int(input("Введите количество постов (по умолчанию 20): ") or 20)
                offset = int(input("Введите offset (по умолчанию 0): ") or 0)
            except ValueError:
                print("Введено не число, используем значения по умолчанию.")
                limit, offset = 20, 0
            result = get_feed(feed_type, limit, offset)
            print(f"Код статуса: {result['status_code']}")
            if result['status_code'] == 200:
                print_feed(result['data'])
            else:
                print("Ошибка при получении ленты:")
                print(json.dumps(result['data'], indent=4, ensure_ascii=False))
        
        elif choice == '6':
            print("Выход.")
            break