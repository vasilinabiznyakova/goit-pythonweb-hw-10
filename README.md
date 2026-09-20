# Contacts API

Асинхронний REST API на FastAPI для керування приватною книгою контактів.

## Можливості

- реєстрація, підтвердження email та JWT-авторизація;
- безпечний запит на скидання пароля без розкриття наявності облікового запису;
- ролі `user` і `admin`;
- зміна аватара через Cloudinary лише для адміністратора;
- CRUD, пошук контактів і найближчі дні народження;
- кешування поточного користувача в Redis із TTL;
- PostgreSQL, Redis та застосунок у Docker Compose;
- unit- та integration-тести з покриттям понад 75%;
- документація, згенерована Sphinx із docstrings.

## Налаштування і запуск

Створіть `.env` на основі `.env.example` та замініть усі демонстраційні значення.

```bash
docker compose up --build
```

Після запуску доступні Swagger UI `http://localhost:8000/docs` і health-check
`http://localhost:8000/api/healthchecker`.

Нові користувачі отримують роль `user`. Першому адміністратору потрібно безпечно
призначити значення `admin` у колонці `users.role` засобами адміністрування БД.
Публічного API для самопризначення ролі адміністратора навмисно немає.

## Основні маршрути

| Метод | Маршрут | Призначення |
|---|---|---|
| POST | `/api/auth/register` | Реєстрація |
| POST | `/api/auth/login` | Отримання access token |
| GET | `/api/auth/confirmed_email/{token}` | Підтвердження email |
| POST | `/api/auth/request-password-reset` | Запит скидання пароля |
| POST | `/api/auth/reset-password` | Встановлення нового пароля |
| GET | `/api/users/me` | Поточний користувач |
| PATCH | `/api/users/avatar` | Зміна аватара адміністратором |
| GET/POST | `/api/contacts/` | Список або створення контакту |
| GET/PUT/DELETE | `/api/contacts/{id}` | Операції з контактом |
| GET | `/api/contacts/birthdays` | Найближчі дні народження |

## Тести та покриття

```bash
python -m pip install -r requirements.txt
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=75
```

Тести використовують окрему SQLite-базу в пам'яті та моки зовнішніх сервісів,
тому не змінюють робочу базу і не надсилають реальні листи чи файли.

## Sphinx

```bash
python -m sphinx -W -b html docs docs/_build/html
```

Готова документація: `docs/_build/html/index.html`.

## Конфіденційні дані

Файл `.env` виключений із Git. У репозиторії зберігається лише `.env.example`
без справжніх паролів, JWT-секретів та ключів зовнішніх сервісів.
