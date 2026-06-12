---
name: nocodb-automation
description: "Робота з NocoDB: таблиці, API, автоматизації, self-hosted налаштування. Використовуй коли: 'NocoDB', 'no-code база даних', 'налаштуй NocoDB'."
risk: low
source: local
date_added: "2026-06-12"
---

# NocoDB Automation

## Що робить цей скіл

Допомагає розгорнути та налаштувати NocoDB: створити таблиці та зв'язки, підключити існуючі бази даних (PostgreSQL, MySQL, SQLite), налаштувати REST API, webhooks та інтеграції з Make.com.

## Тригери (коли активується)

- "NocoDB", "no-code база даних", "налаштуй NocoDB"
- "self-hosted Airtable", "відкрита альтернатива Airtable"
- "NocoDB API", "webhook NocoDB"
- "підключи PostgreSQL до no-code", "NocoDB Docker"

## Вхідні дані (що уточнити перед роботою)

1. **Розгортання**: cloud (nocodb.com) чи self-hosted (Docker / VPS)?
2. **База даних**: нова SQLite чи підключення існуючої (PostgreSQL/MySQL)?
3. **Мета**: що потрібно побудувати (CRM, інвентар, трекер, API-backend)?
4. **Автоматизація**: webhooks, Make/Zapier, або прямі API-запити?
5. **Доступ**: публічний API чи тільки для внутрішнього використання?

## Алгоритм роботи

### Крок 1 — Розгортання NocoDB

**Cloud (швидкий старт):**
- Зареєструватись на app.nocodb.com — безкоштовний план доступний.

**Self-hosted (Docker):**
```bash
docker run -d \
  --name nocodb \
  -v /local/path:/usr/app/data \
  -p 8080:8080 \
  nocodb/nocodb:latest
```
Відкрити: `http://localhost:8080`

**З PostgreSQL:**
```bash
docker run -d \
  -e NC_DB="pg://host:5432?u=user&p=password&d=dbname" \
  -p 8080:8080 \
  nocodb/nocodb:latest
```

### Крок 2 — Підключення бази даних
- Новий проект → "New Project" (SQLite за замовчуванням).
- Або "Connect to existing database" → вказати host, port, credentials.
- NocoDB автоматично читає існуючі таблиці та зв'язки (foreign keys).

### Крок 3 — Структура таблиць і полів
Типи полів у NocoDB:
- `SingleLineText`, `LongText`, `Number`, `Decimal`, `Currency`.
- `SingleSelect`, `MultiSelect`, `Checkbox`, `Date`, `DateTime`.
- `Attachment` — файли (зберігаються локально або у S3).
- `LinkToAnotherRecord` — зв'язок між таблицями (FK у БД).
- `Lookup`, `Rollup` — агрегація з пов'язаних записів.
- `Formula` — обчислення (синтаксис схожий на Excel/Airtable).

### Крок 4 — Views та фільтри
- **Grid** — таблиця зі стовпцями та рядками.
- **Gallery** — карточки (для продуктів, контактів).
- **Form** — вбудована форма збору даних (публічна або приватна).
- **Kanban** — за полем SingleSelect.
- **Calendar** — за полем Date (в нових версіях).
Кожен view зберігає власні фільтри, сортування, приховані поля.

### Крок 5 — REST API
NocoDB автоматично генерує REST API для кожної таблиці.

Базовий URL: `https://your-nocodb.com/api/v1/db/data/noco/{projectId}/{tableName}`

Отримати API Token: Team & Auth → API Tokens → Add Token.

Приклади запитів:
```bash
# Список записів з фільтром
GET /api/v1/db/data/noco/{projId}/{table}?where=(Статус,eq,Активний)&limit=25

# Створити запис
POST /api/v1/db/data/noco/{projId}/{table}
{ "Назва": "Новий запис", "Статус": "Активний" }

# Оновити запис
PATCH /api/v1/db/data/noco/{projId}/{table}/{rowId}
{ "Статус": "Виконано" }
```

### Крок 6 — Webhooks
Налаштувати: Table → Toolbar → More → Webhooks → Add Webhook.
- Тип події: `after.insert`, `after.update`, `after.delete`.
- URL: endpoint Make.com, Zapier або власного сервера.
- Метод: POST; тіло — JSON з даними запису.

### Крок 7 — Інтеграція з Make.com
- Тригер: "Webhooks → Custom webhook" — скопіювати URL та вставити у NocoDB.
- Дія: HTTP-модуль з API-запитом до NocoDB для створення/оновлення записів.
- Або: використовувати готовий Make-модуль NocoDB (якщо доступний в акаунті).

### Крок 8 — Тестування
- Додати запис через UI → перевірити чи webhook надіслав дані.
- Перевірити API-запит через Postman або cURL.
- Переконатись що API token має правильний scope.

## Формат відповіді

- Docker-команда для розгортання (якщо self-hosted).
- Структура таблиць зі списком полів і типів.
- Готові API-запити у блоках коду.
- Інструкція налаштування webhook крок за кроком.

## Правила

- Self-hosted: завжди встановлювати `NC_AUTH_JWT_SECRET` через env-змінну.
- API token зберігати у Make/Zapier credentials, не у відкритому вигляді.
- Для production — використовувати PostgreSQL, не SQLite.
- При підключенні існуючої БД — NocoDB може змінювати структуру таблиць; використовувати Read-Only connection якщо потрібно лише читати.
- Попереджати: безкоштовний cloud-план має ліміти; для великих даних — self-hosted.
