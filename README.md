# Проект Foodgram

### https://foodgram-project.serveftp.com

 Это проект социальной сети в которой пользователи могут публиковать рецепты, добавлять другие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Содержание
- [Функционал](#функционал)
- [Технологии](#технологии)
- [Начало работы](#начало-работы)

## Функционал
- Регистрируется и восстанавливается доступ по электронной почте;
- Добавляются изображения к посту;
- Создаются и редактируются собственные записи;
- Просмотриваются страницы других авторов;
- Подписки и отписки от авторов;
- Публикации можно присвоить несколько тегов;
- Личная страница пользователя;
- Раздел подписки который отображает авторов на которых подписан пользователь;
- Через панель администратора модерируются записи, происходит управление пользователями и создаются теги.

## Технологии
- Python 3.11 ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
- Django 3.2 ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
- Django REST framework 3.14
- Nginx
- Docker
- Postgres

## Начало работы
### Необходимо:
1. Клонировать репозиторий:
2. Перейти в папку с проектом:
3. Установить виртуальное окружение для проекта:
```sh
python -m venv venv
``` 
4. Активировать виртуальное окружение для проекта:
```sh
# для OS Lunix и MacOS
source venv/bin/activate

# для OS Windows
source venv/Scripts/activate
```
5. Установить зависимости:
```sh
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
6. Выполнить миграции на уровне проекта:
```sh
python3 manage.py migrate
```
7. Запустить проект локально:
```sh
python3 manage.py runserver

# адрес запущенного проекта
http://127.0.0.1:8000
```
8. Зарегистирировать суперпользователя Django:
```sh
python3 manage.py createsuperuser

# адрес панели администратора
http://127.0.0.1:8000/admin
```
### Сборка в контейнерах:

Из папки infra/ разверните контейнеры при помощи docker-compose:
```sh
docker-compose up -d --build
```
Выполните миграции:
```sh
docker-compose exec backend python manage.py migrate
```
Создайте суперпользователя:
```sh
docker-compose exec backend python manage.py createsuperuser
```
Соберите статику:
```sh
docker-compose exec backend python manage.py collectstatic --no-input
```
Наполните базу данных ингредиентами и тегами. Выполняйте команду из дериктории где находится файл manage.py:
```sh
docker-compose exec backend python manage.py csv_to_sql
```
Остановка проекта:
```sh
docker-compose down
```
