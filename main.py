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
    """Репост (обычный репост без комментария)."""
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

# ------------------- Основное меню -------------------

if __name__ == "__main__":
    while True:
        choice = input_user(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
                            "0. Выйти\n"
                            "1. Вывести JSON пользователя\n"
                            "2. Сделать текстовый пост\n"
                            "3. Удалить пост по ID\n"
                            "4. Показать комментарии к посту\n"
                            "5. Показать количество непрочитанных уведомлений\n"
                            "6. Показать ленту (по умолчанию all, 20 постов)\n"
                            "7. Сделать пост с аудио и/или изображениями\n"
                            "8. Поставить/убрать 'Мне нравится'\n"
                            "9. Добавить комментарий\n"
                            "10. Удалить комментарий по ID\n"
                            "11. Сделать репост поста")

        if choice == '0':
            print("Выход.")
            break

        elif choice == '1':
            print(json.dumps(get_profile("Wonordel", USER_ID).get("data", {}), indent=4, ensure_ascii=False))
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
            feed_type = input_with_cancel("Введите тип ленты (по умолчанию 'all', q — отмена): ") or "all"
            if feed_type is None:
                print("Действие отменено.")
            else:
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