# Contacts API

REST API для зберігання та управління контактами на FastAPI, SQLAlchemy і PostgreSQL.

## Можливості

- створення контакту;
- отримання списку контактів;
- пошук за іменем, прізвищем або email через query-параметри;
- отримання одного контакту за `id`;
- оновлення контакту;
- видалення контакту;
- список контактів з днями народження у найближчі 7 днів;
- Swagger-документація FastAPI.

## Структура

```text
├── src
│   ├── api
│   │   ├── contacts.py
│   │   └── utils.py
│   ├── services
│   │   └── contacts.py
│   ├── repository
│   │   └── contacts.py
│   ├── database
│   │   ├── models.py
│   │   └── db.py
│   ├── conf
│   │   └── config.py
│   └── schemas.py
├── main.py
├── requirements.txt
└── docker-compose.yml
```

## Запуск

1. Створіть віртуальне оточення та встановіть залежності:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Для Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Запустіть PostgreSQL:

```bash
docker compose up -d
```

3. Створіть `.env` на основі `.env.example` або використайте стандартний рядок підключення:

```env
DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/contacts_db
```

4. Запустіть застосунок:

```bash
uvicorn main:app --reload
```

Swagger буде доступний за адресою:

```text
http://127.0.0.1:8000/docs
```

## Приклади запитів

Створити контакт:

```bash
curl -X POST http://127.0.0.1:8000/api/contacts/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Ivan","last_name":"Petrenko","email":"ivan@example.com","phone":"+380501234567","birthday":"1998-05-21","additional_data":"friend"}'
```

Пошук:

```text
GET /api/contacts/?first_name=Ivan
GET /api/contacts/?last_name=Petrenko
GET /api/contacts/?email=ivan
```

Найближчі дні народження:

```text
GET /api/contacts/birthdays
```
