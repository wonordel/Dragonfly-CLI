ACCESS_TOKEN = input("Введите ACCESS_TOKEN (инструкция в /ru/access_token_get.md): ")
USER_AGENT = input("Введите USER_AGENT (инструкция в /instructions/user_agent_get.md): ")
USER_ID = input("Введите USER_ID (инструкция в /instructions/user_id_get.md): ")
USERNAME = input("Введите USERNAME (ваше имя пользователя на сайте): ")

with open("secret.json", 'w') as f:
    f.write("{\n" + 
            f'    "USER_AGENT": "{USER_AGENT}",\n' +
            f'    "ACCESS_TOKEN": "{ACCESS_TOKEN}",\n' +
            f'    "USER_ID": {USER_ID},\n' +
            f'    "USERNAME": "{USERNAME}"\n' +
            "}")