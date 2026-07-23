[Инструкция для Firefox](#firefox)
[Инструкция для Chromium, Chrome, Yandex Browser, Edge...](#chromium-chrome-yandex-browser-edge)

## Firefox
1. Если у вас уже открыта панель перейдите к шагу 5
2. Перейдите на свой профиль
3. Нажмите F12
4. если панель снизу, то нажмите на 3 точки справа сверху панели и нажмите на `Dock to Right`
5. Перейдите в вкладку `Network` на верхней панели
6. Нажмите кнопку `Reload` или перезагрузите страницу с открытой панели
7. Нажмите в панели на запрос как в примере (В колонке File должно быть get_profile?username=<Ваш username>&current_...): ![Пример Запроса](request_get_profile_example.png)
8. У вас появится панель справа, Там в самом верху будет `GET https://dragonfly-flash.ru/api/get_profile?username=<Ваш username>&current_user_id=<Ваш user_id>`
9. Вы нашли user_id!

## Chromium, Chrome, Yandex Browser, Edge...
1. Если у вас уже открыта панель перейдите к шагу 6
2. Перейдите на свой профиль
3. Нажмите F12
4. Перейдите в вкладку `Network` на верхней панели
5. Нажмите кнопку `Reload page` или перезагрузите страницу с открытой панелью
6. Сверху перейдите в владку `Fetch/XHR`
7. Нажмите на `get_profile?username=<ваш username>&current_user_id=<ваш user_id>`
8. Вы нашли user_id! осталось только скопировать user_id из ссылки