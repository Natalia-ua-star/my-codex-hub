---
name: notion-automation
description: "Налаштування Notion workspace і автоматизацій: бази даних, шаблони, API, Make-інтеграція. Використовуй коли: 'Notion база', 'автоматизуй Notion', 'Notion API'."
risk: low
source: local
date_added: "2026-06-12"
---

# Notion Automation

## Що робить цей скіл

Проектує Notion workspace: бази даних, шаблони сторінок, relation/rollup поля, views, автоматизації через Notion API та інтеграції з Make.com, Zapier, n8n.

## Тригери (коли активується)

- "Notion база", "автоматизуй Notion", "Notion API"
- "зроби workspace в Notion", "трекер задач Notion"
- "підключи Notion до...", "шаблон Notion"
- "Notion database", "relation в Notion", "rollup Notion"

## Вхідні дані (що уточнити перед роботою)

1. **Мета**: CRM, wiki, проектний трекер, контент-план, база знань?
2. **Структура**: які сторінки/бази потрібні та їх зв'язки?
3. **Автоматизація**: вбудована (Notion automations) чи зовнішня (API/Make)?
4. **Інтеграції**: Slack, Gmail, Google Calendar, Make, Zapier?
5. **Команда**: скільки учасників, які права (Full access / Can edit / Can view)?

## Алгоритм роботи

### Крок 1 — Архітектура workspace
Визначити ієрархію:
- **Workspace** → **Teamspaces** (для команд) → **Pages** → **Databases**.
- Головна сторінка-хаб з посиланнями на ключові бази.
- Sidebar: закріпити найчастіше використовувані сторінки.

### Крок 2 — Проектування баз даних
Типи властивостей (properties):
- `Title` — обов'язкове; `Text`, `Number`, `Select`, `Multi-select`.
- `Date`, `Person`, `Checkbox`, `URL`, `Email`, `Phone`.
- `Relation` — зв'язок між двома базами (як foreign key).
- `Rollup` — агрегація значень із пов'язаної бази (SUM, COUNT, MAX).
- `Formula` — обчислювальне поле (синтаксис JavaScript-подібний).

Приклади формул:
- `if(prop("Статус") == "Виконано", "✅", "⏳")`
- `dateBetween(prop("Дедлайн"), now(), "days")` — днів до дедлайну.
- `slice(prop("Назва"), 0, 50)` — обрізати текст.

### Крок 3 — Views та фільтри
- **Table** — стандартна таблиця.
- **Board** — kanban за Select-полем (Статус задачі).
- **Calendar** — за Date-полем.
- **Gallery** — карточки з обкладинкою (Cover).
- **List** — мінімалістичний список.
- **Timeline** — Gantt-подібний графік (платно).
Фільтри та сортування зберігаються для кожного view окремо.

### Крок 4 — Шаблони сторінок
- Створити шаблон кнопкою "+ New → Template".
- Шаблон може містити: заготовлені блоки, таблиці, чеклісти, callout-блоки.
- Корисні блоки: `/callout` (виділений блок), `/toggle` (спойлер), `/table` (inline-таблиця).

### Крок 5 — Notion Automations (вбудовані)
Відкрити базу → кнопка "..." → "Automate":
1. **Тригер**: "Page added to database", "Property edited", "Date reached".
2. **Дія**: Edit property, Add page to database, Send Slack notification, Send email (платно).

### Крок 6 — Notion API + Make.com
Отримати Integration token: notion.so/my-integrations → New Integration.
Поділитися базою з інтеграцією: "..." → "Connections" → додати integration.

Make.com:
- Модуль "Notion → Watch Database Items" — стежити за новими записами.
- "Create Database Item" / "Update Database Item" — запис у базу.
- "Search Objects" — пошук існуючих записів.

API напряму (cURL / HTTP):
```
POST https://api.notion.com/v1/pages
Authorization: Bearer {token}
Notion-Version: 2022-06-28
```

### Крок 7 — Тестування
- Додати тестовий запис → перевірити що automation / Make-сценарій спрацьовує.
- Перевірити rollup після додавання пов'язаних записів.
- Переконатись що integration має доступ до потрібних баз.

## Формат відповіді

- Структура workspace зі списком баз і їх properties.
- Готові формули у блоках коду.
- JSON-приклад для API-запиту якщо потрібно.
- Покрокова інструкція налаштування automations або Make-сценарію.

## Правила

- Кожна база — один тип сутності; не змішувати задачі і проекти в одній базі.
- Relation між базами — замість дублювання даних.
- Integration token зберігати у Make/Zapier як credentials, не в тексті.
- Для командного використання — увімкнути Teamspaces і виставити права.
- Попереджати: Notion API має rate limit 3 req/sec; для масових операцій — додавати затримку у Make.
