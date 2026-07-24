import requests
import json
import os
import io
from PIL import Image

# ------------------- Загрузка секретов -------------------
def load_secrets():
    secrets_path = os.path.join(os.path.dirname(__file__), "secret.json")
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(
            "Файл secret.json не найден. Создайте его в той же папке, что и скрипт, "
            "с полями USER_AGENT, ACCESS_TOKEN, USER_ID, USERNAME."
        )
    with open(secrets_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    required = ["USER_AGENT", "ACCESS_TOKEN", "USER_ID", "USERNAME"]
    missing = [k for k in required if k not in data]
    if missing:
        raise KeyError(f"В secret.json отсутствуют обязательные поля: {', '.join(missing)}")
    return data

SECRETS = load_secrets()

USER_AGENT = SECRETS["USER_AGENT"]
ACCESS_TOKEN = SECRETS["ACCESS_TOKEN"]
USER_ID = SECRETS["USER_ID"]
USERNAME = SECRETS["USERNAME"]

BASE_URL = "https://dragonfly-flash.ru"

# ------------------- Загрузка настроек ASCII -------------------
def load_settings():
    settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
    if not os.path.exists(settings_path):
        # значения по умолчанию, если файл отсутствует
        return {
            "ascii_columns": 60,
            "ascii_chars": "█▓▒░@%#*+=-:. "
        }
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)

SETTINGS = load_settings()
ASCII_COLUMNS = SETTINGS.get("ascii_columns", 60)
ASCII_CHARS = SETTINGS.get("ascii_chars", "█▓▒░@%#*+=-:. ")

# ------------------- Заголовки и куки -------------------
BASE_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Accept-Language": "ru,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": f"https://dragonfly-flash.ru/?id={USERNAME}",
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

# ------------------- Вспомогательные функции -------------------
def input_user(possible: list, text: str):
    while True:
        print(text)
        user_input = input(">>> ")
        if user_input not in possible:
            print("Введите свой выбор")
        else:
            return user_input

def input_with_cancel(prompt: str, cancel_values=('q', 'отмена', 'cancel')):
    value = input(prompt).strip()
    if value.lower() in cancel_values:
        return None
    return value

def input_multiline_with_cancel(prompt: str, cancel_values=('q', 'отмена', 'cancel')):
    print(prompt)
    lines = []
    first_line = input(">>> ").strip()
    if first_line.lower() in cancel_values:
        return None
    if first_line == "":
        return ""
    lines.append(first_line)
    while True:
        line = input(">>> ")
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)

# ------------------- Функции API -------------------

def publish_post(text: str) -> dict:
    url = f"{BASE_URL}/api/upload_post_modernized"
    files = {"description": (None, text, "text/plain")}
    response = requests.post(url, headers=BASE_HEADERS, cookies=COOKIES, files=files)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def publish_post_with_media(text: str, audio_ids: list = None, file_paths: list = None) -> dict:
    url = f"{BASE_URL}/api/upload_post_modernized"
    data = {}
    if text:
        data["description"] = text
    if audio_ids:
        data["audio_ids"] = ",".join(map(str, audio_ids))
    
    files = []
    if file_paths:
        for path in file_paths:
            if os.path.exists(path):
                ext = os.path.splitext(path)[1].lower()
                content_type = "image/jpeg"
                if ext in [".png"]:
                    content_type = "image/png"
                elif ext in [".gif"]:
                    content_type = "image/gif"
                elif ext in [".webp"]:
                    content_type = "image/webp"
                files.append(("files", (os.path.basename(path), open(path, "rb"), content_type)))
            else:
                print(f"Файл {path} не найден, пропускаем.")
    
    response = requests.post(url, headers=BASE_HEADERS, cookies=COOKIES, data=data, files=files)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def publish_post_with_poll(description: str, poll_question: str, poll_choices: list, 
                           audio_ids: list = None, file_paths: list = None) -> dict:
    url = f"{BASE_URL}/api/upload_post_modernized"
    data = {}
    if description:
        data["description"] = description
    data["poll_question"] = poll_question
    data["poll_choices"] = json.dumps(poll_choices)
    
    if audio_ids:
        data["audio_ids"] = ",".join(map(str, audio_ids))
    
    files = []
    if file_paths:
        for path in file_paths:
            if os.path.exists(path):
                ext = os.path.splitext(path)[1].lower()
                content_type = "image/jpeg"
                if ext in [".png"]:
                    content_type = "image/png"
                elif ext in [".gif"]:
                    content_type = "image/gif"
                elif ext in [".webp"]:
                    content_type = "image/webp"
                files.append(("files", (os.path.basename(path), open(path, "rb"), content_type)))
            else:
                print(f"Файл {path} не найден, пропускаем.")
    
    response = requests.post(url, headers=BASE_HEADERS, cookies=COOKIES, data=data, files=files)
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
        comment_id = comment.get('id', 'N/A')
        author = comment.get('author', {}).get('username', 'Неизвестный')
        text = comment.get('text', '')
        date = comment.get('created_at', '')
        print(f"{i}. [ID {comment_id}] {author} ({date}): {text}")

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

def image_to_ascii(url: str, columns: int = None, chars: str = None) -> str:
    if columns is None:
        columns = ASCII_COLUMNS
    if chars is None:
        chars = ASCII_CHARS

    try:
        response = requests.get(url, headers=BASE_HEADERS, timeout=15)
        response.raise_for_status()

        img = Image.open(io.BytesIO(response.content)).convert("RGB")

        width, height = img.size
        aspect = height / width
        new_height = max(1, int(columns * aspect * 0.55))

        img = img.resize((columns, new_height), Image.Resampling.LANCZOS)

        out = []

        for y in range(new_height):
            line = ""
            for x in range(columns):
                r, g, b = img.getpixel((x, y))
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                ch = chars[gray * (len(chars) - 1) // 255]
                line += f"\033[38;2;{r};{g};{b}m{ch}"
            line += "\033[0m"
            out.append(line)

        return "\n".join(out)

    except Exception as e:
        return f"[Не удалось преобразовать изображение: {e}]"

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
        print(f"   {description}")
        print(f"   👍 {likes}  💬 {comments}  {is_liked}")
        
        photos = post.get("photos", [])
        if photos:
            photo_url = photos[0].get("url")
            if photo_url:
                full_url = BASE_URL + photo_url if photo_url.startswith("/") else photo_url
                print("   📷 Изображение (ASCII-art):")
                try:
                    ascii_art = image_to_ascii(full_url)
                    for line in ascii_art.splitlines():
                        print(f"   {line}")
                except Exception as e:
                    print(f"   [Ошибка: {e}]")
                print(f"   Ссылка: {full_url}")
            else:
                print(f"   📷 {len(photos)} фото")
        
        audios = post.get("audios", [])
        if audios:
            audio_strs = []
            for audio in audios:
                artist = audio.get("artist", "Неизвестный")
                title = audio.get("title", "Без названия")
                audio_strs.append(f"{artist} - {title}")
            print(f"   🎵 {', '.join(audio_strs)}")
        
        poll = post.get("poll")
        if poll:
            print(f"   📊 Опрос: {poll.get('question')}")
        print()

def like_post(post_id: int) -> dict:
    url = f"{BASE_URL}/api/like"
    files = {"post_id": (None, str(post_id))}
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    response = requests.post(url, headers=headers, cookies=COOKIES, files=files)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def add_comment(post_id: int, text: str) -> dict:
    url = f"{BASE_URL}/api/add_comment"
    files = {
        "post_id": (None, str(post_id)),
        "text": (None, text)
    }
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    response = requests.post(url, headers=headers, cookies=COOKIES, files=files)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def delete_comment(comment_id: int) -> dict:
    url = f"{BASE_URL}/api/comment/{comment_id}"
    response = requests.delete(url, headers=BASE_HEADERS, cookies=COOKIES)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def repost_post(post_id: int) -> dict:
    url = f"{BASE_URL}/api/posts/{post_id}/repost"
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    headers["Content-Length"] = "0"
    response = requests.post(url, headers=headers, cookies=COOKIES)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def vote_poll(poll_id: int, choice_id: int) -> dict:
    url = f"{BASE_URL}/api/polls/{poll_id}/vote"
    files = {"choice_id": (None, str(choice_id))}
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    response = requests.post(url, headers=headers, cookies=COOKIES, files=files)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def get_notifications(limit: int = 15, offset: int = 0) -> dict:
    url = f"{BASE_URL}/api/notifications"
    params = {"limit": limit, "offset": offset}
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    response = requests.get(url, headers=headers, cookies=COOKIES, params=params)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def print_notifications(notifications_list: list) -> None:
    if not notifications_list:
        print("Уведомлений нет.")
        return
    print(f"Всего уведомлений: {len(notifications_list)}")
    for i, notif in enumerate(notifications_list, 1):
        notif_id = notif.get('id', 'N/A')
        notif_type = notif.get('type', 'unknown')
        text = notif.get('text', '')
        target_id = notif.get('target_id', 'N/A')
        is_read = notif.get('is_read', False)
        created = notif.get('created_at', '')
        read_status = "✅ Прочитано" if is_read else "🔴 Не прочитано"
        print(f"{i}. [ID {notif_id}] {notif_type} — {text}")
        print(f"   Цель: {target_id} | {read_status} | {created}")
        print()

def get_my_audio() -> dict:
    url = f"{BASE_URL}/api/audio/my"
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    response = requests.get(url, headers=headers, cookies=COOKIES)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def get_all_audio(query: str = "", limit: int = 5000) -> dict:
    url = f"{BASE_URL}/api/audio/all"
    params = {"q": query, "limit": limit}
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    response = requests.get(url, headers=headers, cookies=COOKIES, params=params)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def print_audio_list(audio_list: list, title: str, show_owner: bool = False) -> None:
    if not audio_list:
        print(f"{title}: нет записей.")
        return
    print(f"{title}: {len(audio_list)} записей")
    for i, audio in enumerate(audio_list, 1):
        audio_id = audio.get('id', 'N/A')
        title_str = audio.get('title', 'Без названия')
        artist = audio.get('artist', 'Неизвестен')
        created = audio.get('created_at', '')
        owner = ""
        if show_owner:
            owner_name = audio.get('owner_name', '')
            if owner_name:
                owner = f" (владелец: {owner_name})"
        print(f"{i}. {title_str} — {artist}{owner}")
        print(f"   ID: {audio_id}, добавлено: {created}")
        if 'is_added' in audio:
            added = "✅" if audio['is_added'] else "❌"
            print(f"   В моих: {added}")
        print()

def get_top_users(limit: int = 50) -> dict:
    url = f"{BASE_URL}/api/users/top"
    params = {"limit": limit}
    headers = BASE_HEADERS.copy()
    headers["Referer"] = "https://dragonfly-flash.ru/"
    headers["Priority"] = "u=0"
    response = requests.get(url, headers=headers, cookies=COOKIES, params=params)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.text else {}
    }

def print_top_users(top_data: dict) -> None:
    if top_data.get('status') != 'success':
        print("Ошибка при получении топа пользователей.")
        print(json.dumps(top_data, indent=4, ensure_ascii=False))
        return
    users = top_data.get('top_users', [])
    if not users:
        print("Топ пользователей пуст.")
        return
    print(f"🏆 Топ пользователей (лучшие стрекозойды): {len(users)} записей")
    print("-" * 60)
    for user in users:
        rank = user.get('rank', '?')
        username = user.get('username', 'Неизвестный')
        rating = user.get('rating', 0)
        badge = user.get('achievement_badge')
        badge_str = f" [{badge}]" if badge else ""
        print(f"{rank:>2}. {username:<20} — рейтинг: {rating}{badge_str}")
    print("-" * 60)

# ------------------- Основное меню -------------------

if __name__ == "__main__":
    while True:
        choice = input_user(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'],
                            "0. Выйти\n"
                            "1. Вывести JSON пользователя (своего)\n"
                            "2. Сделать текстовый пост\n"
                            "3. Удалить пост по ID\n"
                            "4. Показать комментарии к посту\n"
                            "5. Показать количество непрочитанных уведомлений\n"
                            "6. Показать ленту (тип: all или friends)\n"
                            "7. Сделать пост с аудио и/или изображениями\n"
                            "8. Поставить/убрать 'Мне нравится'\n"
                            "9. Добавить комментарий\n"
                            "10. Удалить комментарий по ID\n"
                            "11. Сделать репост поста\n"
                            "12. Сделать пост с опросом\n"
                            "13. Проголосовать в опросе\n"
                            "14. Прочитать уведомления\n"
                            "15. Мои аудиозаписи\n"
                            "16. Все аудиозаписи\n"
                            "17. Топ пользователей (лучшие стрекозойды)\n"
                            "18. Показать профиль пользователя (по имени)")

        if choice == '0':
            print("Выход.")
            break

        elif choice == '1':
            print(json.dumps(get_profile(USERNAME, USER_ID).get("data", {}), indent=4, ensure_ascii=False))
            print()

        elif choice == '2':
            text = input_multiline_with_cancel("Введите текст поста (пустая строка — завершить ввод, q/отмена — отменить):")
            if text is None:
                print("Действие отменено.")
            else:
                result = publish_post(text)
                print(f"Код статуса: {result['status_code']}")
                print(f"Данные: {result['data']}")
            print()

        elif choice == '3':
            post_id_str = input_with_cancel("Введите ID поста для удаления (q — отмена): ")
            if post_id_str is None:
                print("Действие отменено.")
            else:
                try:
                    post_id = int(post_id_str)
                    result = delete_post(post_id)
                    print(f"Код статуса: {result['status_code']}")
                    print(f"Ответ сервера: {result['data']}")
                except ValueError:
                    print("ID должен быть числом.")
            print()

        elif choice == '4':
            post_id_str = input_with_cancel("Введите ID поста для просмотра комментариев (q — отмена): ")
            if post_id_str is None:
                print("Действие отменено.")
            else:
                try:
                    post_id = int(post_id_str)
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
            print()

        elif choice == '5':
            result = get_unread_count()
            print(f"Код статуса: {result['status_code']}")
            print_unread_count(result)
            print()

        elif choice == '6':
            feed_type = input_with_cancel("Введите тип ленты ('all' или 'friends', по умолчанию 'all', q — отмена): ") or "all"
            if feed_type is None:
                print("Действие отменено.")
            else:
                if feed_type not in ['all', 'friends']:
                    print("Неверный тип, используем 'all'")
                    feed_type = 'all'
                try:
                    limit_str = input_with_cancel("Введите количество постов (по умолчанию 20, q — отмена): ")
                    if limit_str is None:
                        print("Действие отменено.")
                        continue
                    limit = int(limit_str) if limit_str else 20

                    offset_str = input_with_cancel("Введите offset (по умолчанию 0, q — отмена): ")
                    if offset_str is None:
                        print("Действие отменено.")
                        continue
                    offset = int(offset_str) if offset_str else 0
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
            print()

        elif choice == '7':
            text = input_multiline_with_cancel("Введите текст поста (пустая строка — без текста, q/отмена — отменить):")
            if text is None:
                print("Действие отменено.")
                print()
                continue

            audio_input = input_with_cancel("Введите ID аудио через запятую (или оставьте пустым, q — отмена): ")
            if audio_input is None:
                print("Действие отменено.")
                print()
                continue
            audio_ids = []
            if audio_input.strip():
                try:
                    audio_ids = [int(x.strip()) for x in audio_input.split(",") if x.strip()]
                except ValueError:
                    print("Некорректный ввод ID аудио, пропускаем.")

            file_paths = []
            print("Введите пути к файлам изображений (по одному, пустая строка для завершения, q/отмена — отменить действие):")
            while True:
                path = input(">>> ").strip()
                if path.lower() in ('q', 'отмена', 'cancel'):
                    print("Действие отменено.")
                    file_paths = None
                    break
                if not path:
                    break
                if os.path.exists(path):
                    file_paths.append(path)
                else:
                    print(f"Файл не найден: {path}")
            if file_paths is None:
                print()
                continue

            result = publish_post_with_media(text, audio_ids, file_paths)
            print(f"Код статуса: {result['status_code']}")
            print(f"Ответ сервера: {result['data']}")
            print()

        elif choice == '8':
            post_id_str = input_with_cancel("Введите ID поста для отметки 'Мне нравится' (q — отмена): ")
            if post_id_str is None:
                print("Действие отменено.")
            else:
                try:
                    post_id = int(post_id_str)
                    result = like_post(post_id)
                    print(f"Код статуса: {result['status_code']}")
                    if result['status_code'] == 200:
                        status = result['data'].get('status')
                        if status == 'liked':
                            print("✅ 'Мне нравится' поставлено")
                        elif status == 'unliked':
                            print("❌ 'Мне нравится' убрано")
                        else:
                            print(f"Ответ сервера: {result['data']}")
                    else:
                        print("Ошибка при выполнении запроса:")
                        print(json.dumps(result['data'], indent=4, ensure_ascii=False))
                except ValueError:
                    print("ID должен быть числом.")
            print()

        elif choice == '9':
            post_id_str = input_with_cancel("Введите ID поста для комментария (q — отмена): ")
            if post_id_str is None:
                print("Действие отменено.")
                print()
                continue
            try:
                post_id = int(post_id_str)
            except ValueError:
                print("ID должен быть числом.")
                print()
                continue

            while True:
                comment_text = input_with_cancel("Введите текст комментария (q/отмена — отменить): ")
                if comment_text is None:
                    print("Действие отменено.")
                    break
                if comment_text.strip() == "":
                    print("Комментарий не может быть пустым. Попробуйте снова.")
                    continue
                result = add_comment(post_id, comment_text)
                print(f"Код статуса: {result['status_code']}")
                if result['status_code'] == 200:
                    data = result['data']
                    comment_id = data.get('id') or data.get('comment_id')
                    if comment_id:
                        print(f"✅ Комментарий добавлен (ID: {comment_id})")
                    else:
                        print(f"✅ {data.get('message', 'Комментарий добавлен')}")
                        if data:
                            print("Полный ответ:", json.dumps(data, ensure_ascii=False))
                else:
                    print("Ошибка при добавлении комментария:")
                    print(json.dumps(result['data'], indent=4, ensure_ascii=False))
                break
            print()

        elif choice == '10':
            comment_id_str = input_with_cancel("Введите ID комментария для удаления (q — отмена): ")
            if comment_id_str is None:
                print("Действие отменено.")
            else:
                try:
                    comment_id = int(comment_id_str)
                    result = delete_comment(comment_id)
                    print(f"Код статуса: {result['status_code']}")
                    if result['status_code'] == 200:
                        if result['data'].get('status') == 'deleted':
                            print("✅ Комментарий удалён")
                        else:
                            print(f"Ответ сервера: {result['data']}")
                    else:
                        print("Ошибка при удалении комментария:")
                        print(json.dumps(result['data'], indent=4, ensure_ascii=False))
                except ValueError:
                    print("ID должен быть числом.")
            print()

        elif choice == '11':
            post_id_str = input_with_cancel("Введите ID поста для репоста (q — отмена): ")
            if post_id_str is None:
                print("Действие отменено.")
            else:
                try:
                    post_id = int(post_id_str)
                    result = repost_post(post_id)
                    print(f"Код статуса: {result['status_code']}")
                    if result['status_code'] == 200:
                        data = result['data']
                        if data.get('status') == 'success':
                            print("✅ Репост создан")
                            if data.get('message'):
                                print(f"Сообщение: {data['message']}")
                        else:
                            print(f"Ответ сервера: {data}")
                    else:
                        print("Ошибка при репосте:")
                        print(json.dumps(result['data'], indent=4, ensure_ascii=False))
                except ValueError:
                    print("ID должен быть числом.")
            print()

        elif choice == '12':
            description = input_multiline_with_cancel("Введите описание поста (пустая строка — без описания, q/отмена — отменить):")
            if description is None:
                print("Действие отменено.")
                print()
                continue

            poll_question = input_with_cancel("Введите вопрос опроса (q/отмена — отменить): ")
            if poll_question is None:
                print("Действие отменено.")
                print()
                continue
            if poll_question.strip() == "":
                print("Вопрос опроса не может быть пустым.")
                print()
                continue

            print("Введите варианты ответа (по одному, пустая строка для завершения, q/отмена — отменить):")
            poll_choices = []
            while True:
                choice_text = input(">>> ").strip()
                if choice_text.lower() in ('q', 'отмена', 'cancel'):
                    print("Действие отменено.")
                    poll_choices = None
                    break
                if choice_text == "":
                    if len(poll_choices) < 2:
                        print("Нужно ввести минимум 2 варианта. Продолжайте.")
                        continue
                    else:
                        break
                poll_choices.append(choice_text)
            if poll_choices is None:
                print()
                continue
            if len(poll_choices) < 2:
                print("Недостаточно вариантов (нужно минимум 2). Действие отменено.")
                print()
                continue

            audio_input = input_with_cancel("Введите ID аудио через запятую (или оставьте пустым, q — отмена): ")
            if audio_input is None:
                print("Действие отменено.")
                print()
                continue
            audio_ids = []
            if audio_input.strip():
                try:
                    audio_ids = [int(x.strip()) for x in audio_input.split(",") if x.strip()]
                except ValueError:
                    print("Некорректный ввод ID аудио, пропускаем.")

            file_paths = []
            print("Введите пути к файлам изображений (по одному, пустая строка для завершения, q/отмена — отменить действие):")
            while True:
                path = input(">>> ").strip()
                if path.lower() in ('q', 'отмена', 'cancel'):
                    print("Действие отменено.")
                    file_paths = None
                    break
                if not path:
                    break
                if os.path.exists(path):
                    file_paths.append(path)
                else:
                    print(f"Файл не найден: {path}")
            if file_paths is None:
                print()
                continue

            result = publish_post_with_poll(description, poll_question, poll_choices, audio_ids, file_paths)
            print(f"Код статуса: {result['status_code']}")
            if result['status_code'] == 200:
                data = result['data']
                post_id = data.get('post_id')
                if post_id:
                    print(f"✅ Пост с опросом опубликован (ID: {post_id})")
                else:
                    print(f"Ответ сервера: {data}")
            else:
                print("Ошибка при публикации поста с опросом:")
                print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            print()

        elif choice == '13':
            poll_id_str = input_with_cancel("Введите ID опроса (poll_id) (q — отмена): ")
            if poll_id_str is None:
                print("Действие отменено.")
                print()
                continue
            try:
                poll_id = int(poll_id_str)
            except ValueError:
                print("ID опроса должен быть числом.")
                print()
                continue

            choice_id_str = input_with_cancel("Введите ID варианта (choice_id) (q — отмена): ")
            if choice_id_str is None:
                print("Действие отменено.")
                print()
                continue
            try:
                choice_id = int(choice_id_str)
            except ValueError:
                print("ID варианта должен быть числом.")
                print()
                continue

            result = vote_poll(poll_id, choice_id)
            print(f"Код статуса: {result['status_code']}")
            if result['status_code'] == 200:
                data = result['data']
                if data.get('status') == 'ok':
                    print(f"✅ {data.get('message', 'Голос учтён')}")
                else:
                    print(f"Ответ сервера: {data}")
            else:
                print("Ошибка при голосовании:")
                print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            print()

        elif choice == '14':
            try:
                limit_str = input_with_cancel("Введите количество уведомлений (по умолчанию 15, q — отмена): ")
                if limit_str is None:
                    print("Действие отменено.")
                    continue
                limit = int(limit_str) if limit_str else 15

                offset_str = input_with_cancel("Введите offset (по умолчанию 0, q — отмена): ")
                if offset_str is None:
                    print("Действие отменено.")
                    continue
                offset = int(offset_str) if offset_str else 0
            except ValueError:
                print("Введено не число, используем значения по умолчанию.")
                limit, offset = 15, 0

            result = get_notifications(limit, offset)
            print(f"Код статуса: {result['status_code']}")
            if result['status_code'] == 200:
                if isinstance(result['data'], list):
                    print_notifications(result['data'])
                else:
                    print("Неожиданный формат ответа:")
                    print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            else:
                print("Ошибка при получении уведомлений:")
                print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            print()

        elif choice == '15':
            result = get_my_audio()
            print(f"Код статуса: {result['status_code']}")
            if result['status_code'] == 200:
                if isinstance(result['data'], list):
                    print_audio_list(result['data'], "Мои аудиозаписи", show_owner=False)
                else:
                    print("Неожиданный формат ответа:")
                    print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            else:
                print("Ошибка при получении моих аудиозаписей:")
                print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            print()

        elif choice == '16':
            query = input_with_cancel("Введите поисковый запрос (или оставьте пустым, q — отмена): ") or ""
            if query is None:
                print("Действие отменено.")
                print()
                continue
            try:
                limit_str = input_with_cancel("Введите лимит (по умолчанию 5000, q — отмена): ")
                if limit_str is None:
                    print("Действие отменено.")
                    continue
                limit = int(limit_str) if limit_str else 5000
            except ValueError:
                print("Введено не число, используем лимит 5000.")
                limit = 5000

            result = get_all_audio(query, limit)
            print(f"Код статуса: {result['status_code']}")
            if result['status_code'] == 200:
                if isinstance(result['data'], list):
                    print_audio_list(result['data'], "Все аудиозаписи", show_owner=True)
                else:
                    print("Неожиданный формат ответа:")
                    print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            else:
                print("Ошибка при получении всех аудиозаписей:")
                print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            print()

        elif choice == '17':
            try:
                limit_str = input_with_cancel("Введите количество пользователей в топе (по умолчанию 50, q — отмена): ")
                if limit_str is None:
                    print("Действие отменено.")
                    continue
                limit = int(limit_str) if limit_str else 50
            except ValueError:
                print("Введено не число, используем лимит 50.")
                limit = 50

            result = get_top_users(limit)
            print(f"Код статуса: {result['status_code']}")
            if result['status_code'] == 200:
                print_top_users(result['data'])
            else:
                print("Ошибка при получении топа пользователей:")
                print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            print()

        elif choice == '18':
            username = input_with_cancel("Введите имя пользователя (q — отмена): ")
            if username is None:
                print("Действие отменено.")
                print()
                continue
            if username.strip() == "":
                print("Имя пользователя не может быть пустым.")
                print()
                continue

            result = get_profile(username, USER_ID)
            print(f"Код статуса: {result['status_code']}")
            if result['status_code'] == 200:
                profile_data = result['data']
                if profile_data:
                    print_profile(profile_data)
                else:
                    print("Профиль не найден или данные пусты.")
            else:
                print("Ошибка при получении профиля:")
                print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            print()