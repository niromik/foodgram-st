# Запуск проекта

Запуск сервера Django с опцией DEBUG и базой данных SQLite3.
Создайте свой файл .env в папке infra/ (пример можно найти в infra/example.env)

Создайте и активируйте виртуальное окружение:
```powershell
# В папке /
cd backend
python -m venv venv
. venv/Scripts/Activate
```

Установите необходимые пакеты:
```powershell
pip install -r requirements.txt
```

Для локального запуска рекомендуются параметры `DJANGO_IS_DEBUG=True` и `DJANGO_IS_SQLITE3=True` в вашем файле .env.

Выполните миграции, импорт тестовых данных и коллекцию статики:
```powershell
python backend/foodgram/manage.py migrate
python backend/foodgram/manage.py loaddata backend/data/initial_data.json
python backend/foodgram/manage.py collectstatic --noinput
```

Запустите сервер:
```powershell
python backend/foodgram/manage.py runserver
```
