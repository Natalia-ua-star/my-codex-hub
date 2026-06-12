---
name: n8n-automation
description: "Побудова n8n workflows: вузли, credentials, self-hosted налаштування. Використовуй коли: 'n8n workflow', 'автоматизація n8n', 'зроби в n8n'."
risk: medium
source: local
date_added: "2026-06-12"
---

# Навичка: n8n-automation

## Що робить
Проєктує та описує n8n workflows: від простих тригер-дія до складних workflows з умовами, циклами, webhook-ендпоінтами та кастомним JavaScript/Python кодом.

## Тригери (коли активується)
- "n8n workflow"
- "автоматизація n8n"
- "зроби в n8n"
- "n8n інтеграція"
- "налаштуй n8n вузол"
- "self-hosted автоматизація"

## Вхідні дані (що запитати у користувача)
1. **Мета workflow** — що повинно відбуватись?
2. **Тригер** — Webhook / Schedule (Cron) / Manual / App-тригер?
3. **Вузли** — які сервіси потрібно підключити?
4. **Логіка** — є умови, цикли, паралельні гілки?
5. **Середовище** — n8n Cloud чи self-hosted?
6. **Credentials** — які акаунти/API-ключі вже налаштовані?

## Алгоритм (кроки)

### Крок 1 — Архітектура workflow
- Визначити тип тригера:
  - `Webhook Node` — для реального часу (Shopify, Stripe hooks)
  - `Schedule Trigger` — для регулярних задач (cron-вираз)
  - `Manual Trigger` — для ручного запуску
- Побудувати граф вузлів: Trigger → Node1 → [IF?] → Node2

### Крок 2 — Вибір вузлів
```
Популярні вузли:
- HTTP Request     — будь-який REST API
- Code (JS/Python) — кастомна логіка
- IF               — умовне розгалуження
- Switch           — множинні гілки
- Set              — встановлення/трансформація полів
- Merge            — об'єднання гілок
- Loop Over Items  — ітерація по масиву
- Wait             — затримка між кроками
- Google Sheets / Notion / Slack / Gmail — вбудовані інтеграції
```

### Крок 3 — Credentials
- Вказати тип авторизації для кожного вузла (OAuth2, API Key, Basic Auth)
- Self-hosted: налаштувати n8n через змінні середовища:
  ```
  N8N_BASIC_AUTH_ACTIVE=true
  N8N_HOST=your-domain.com
  WEBHOOK_URL=https://your-domain.com/
  ```

### Крок 4 — JSON workflow export
- Сформувати JSON структуру workflow (сумісну з n8n import)
- Кожен вузол: `id`, `name`, `type`, `parameters`, `position`
- Connections: описати зв'язки між вузлами

### Крок 5 — Покрокова інструкція
```
1. n8n → New Workflow
2. Додати тригер-вузол → налаштувати параметри
3. Додати вузли послідовно → налаштувати credentials
4. Налаштувати mapping даних між вузлами (expressions: {{ $json.field }})
5. Тестування: Execute Workflow (Manual trigger) або Send test webhook
6. Активувати workflow (toggle Active)
```

### Крок 6 — Оптимізація
- Додати Error Trigger вузол для обробки помилок
- Використовувати `Set` вузол для нормалізації даних
- Для великих обсягів — налаштувати `batch size` в Loop

## Формат виводу
```
## n8n Workflow: [Назва]

### Схема вузлів
[Manual Trigger] → [HTTP Request] → [IF] → [Google Sheets]
                                         → [Slack Notify]

### Конфігурація вузлів
**Вузол 1 — [Назва]**
- Тип: ...
- Параметри: ...
- Credentials: ...

### JSON Export (фрагмент)
\`\`\`json
{ "nodes": [...], "connections": {...} }
\`\`\`

### Розгортання
1. ...
```

## Правила
- Expressions в n8n: `{{ $json.fieldName }}`, `{{ $node["NodeName"].json.field }}`
- Для HTTP Request — завжди вказувати Content-Type header
- Self-hosted: нагадати про SSL та reverse proxy (Nginx/Caddy)
- Для Shopify webhooks — використовувати HMAC-верифікацію в Code вузлі
- Пропонувати Code вузол (JS) замість складних ланцюжків вузлів
