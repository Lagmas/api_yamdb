Склонируйте проект по адресу https://github.com/Lagmas/api_yamdb.git

Создайте и активируйте виртуальное окружение
python3 -m venv venv source venv/Scripts/activate
Установить все необходимые пакеты одной командой:
python -m pip install -r requirements.txt.
Выполните миграции
python manage.py makemigrations python manage.py migrate
Запустите сервер локально командой:
python manage.py runserver
Когда вы запустите проект, по адресу http://127.0.0.1:8000/redoc/ будет доступна документация для API Yatube.