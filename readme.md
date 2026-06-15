# TeamFinder - Платформа для поиска команды для pet-проектов

## О проекте

TeamFinder - это веб-платформа, на которой разработчики, дизайнеры и другие специалисты могут находить единомышленников для совместной работы над pet-проектами.
### Основные возможности

- Регистрация и аутентификация пользователей
- Создание, редактирование и завершение проектов
- Добавление проектов в избранное
- Участие в проектах других пользователей
- Фильтрация пользователей по различным критериям
- Управление профилем пользователя
- Смена пароля

## Технологии

- **Backend**: Django 5.2
- **Database**: PostgreSQL 15
- **Frontend**: HTML, CSS, JavaScript (готовые шаблоны)
- **Containerization**: Docker, Docker Compose

## Системные требования

- Python 3.12+
- PostgreSQL 15+
- Docker и Docker Compose (для контейнеризации)
- Git

## Установка и запуск

# 1. Клонируйте репозиторий
git clone https://github.com/marktokarev/team-finder-ad-main
cd team-finder-ad-main

# 2. Создайте и активируйте виртуальное окружение
# Windows:
python -m venv venv
venv\Scripts\activate

# Linux/Mac:
python3 -m venv venv
source venv/bin/activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Создайте файл .env, склонировав .env_example коммандой:
cp .env_example .env

# 5. Поднимите PostgreSQL
docker-compose up -d

# 6. Примените миграции
python manage.py migrate

# 7. Создайте суперпользователя
python manage.py createsuperuser



# 8. Запустите сервер разработки
python manage.py runserver

# 9. Приложение доступно по адресу:
# http://localhost:8000