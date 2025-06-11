# Запуск проекта

Запустить проект можно в двух вариантах: локальной и полной (на Docker) версиях.

## Локальный запуск

Запуск сервера Django с опцией DEBUG и базой данных SQLite3.
Перед запуском установите [Python 3.10](https://www.python.org/downloads/release/python-3100/) и создайте свой файл .env в папке infra/ (пример можно найти в infra/example.env)

После запуска можно будет посмотреть следующие страницы:
- **http://localhost:8000/** - Ссылка на основную страницу бэкенда
- **http://localhost:8000/api** - API бэкенда
- **http://localhost:8000/admin** - Django Admin

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

## Полный запуск с Docker

Запуск всего compose-стека в Docker (включает Django, PostgreSQL и Nginx).
Перед запуском установите [Docker](https://docs.docker.com/get-started/) для своей ОС и создайте свой файл .env в папке infra/ (пример можно найти в infra/example.env):

После запуска можно будет посмотреть следующие страницы:
- **http://localhost/** - Ссылка на основную страницу Foodgram
- **http://localhost/api/docs/** - Ссылка на спецификацию документации
- **http://localhost/api** - API бэкенда
- **http://localhost/admin** - Django Admin

Разверните compose-стек:
```powershell
# В папке /infra
docker compose up --force-recreate --build -d
```

Для полного запуска рекомендуются параметры `DJANGO_IS_DEBUG=False` и `DJANGO_IS_SQLITE3=False` в вашем файле .env.

Выполните миграции, импорт тестовых данных и коллекцию статики:
```powershell
docker compose exec backend python foodgram/manage.py migrate
docker compose exec backend python foodgram/manage.py loaddata data/initial_data.json
docker compose exec backend python foodgram/manage.py collectstatic --noinput
```
