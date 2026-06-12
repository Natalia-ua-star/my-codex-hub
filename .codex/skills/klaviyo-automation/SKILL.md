---
name: klaviyo-automation
description: "Email/SMS автоматизація в Klaviyo: flows, сегменти, кампанії для e-commerce. Використовуй коли: 'Klaviyo', 'email автоматизація', 'налаштувати flow'."
risk: medium
source: local
date_added: "2026-06-12"
---

# Навичка: klaviyo-automation

## Що робить
Будує email та SMS автоматизації в Klaviyo для e-commerce: flows (потоки), сегменти аудиторій, кампанії. Орієнтована на Shopify-магазини та дропшипінг.

## Тригери (коли активується)
- "Klaviyo"
- "email автоматизація"
- "налаштувати flow"
- "email flow Klaviyo"
- "SMS кампанія"
- "покинутий кошик email"
- "welcome series"

## Вхідні дані (що запитати у користувача)
1. **Тип завдання** — Flow / Кампанія / Сегмент / Інтеграція Shopify?
2. **Мета** — відновлення кошика, welcome series, post-purchase, win-back?
3. **Аудиторія** — хто отримує (нові підписники, покупці, VIP)?
4. **Канал** — Email, SMS або обидва?
5. **Тон бренду** — формальний / неформальний / агресивний sale?
6. **Інтеграція** — Shopify підключений до Klaviyo?

## Алгоритм (кроки)

### Крок 1 — Визначення типу автоматизації

**Основні Flow (потоки):**
```
1. Welcome Series      — тригер: список "Newsletter"
2. Abandoned Cart      — тригер: Shopify "Started Checkout"
3. Abandoned Browse    — тригер: Shopify "Viewed Product"
4. Post-Purchase       — тригер: Shopify "Ordered Product"
5. Win-Back            — тригер: "Customer hasn't purchased in 90 days"
6. Sunset Flow         — тригер: "Hasn't opened email in 180 days"
```

### Крок 2 — Архітектура Flow
```
Trigger → [Time Delay] → Email 1
                      → [Conditional Split: opened?]
                         Yes → Email 2 (Upsell)
                         No  → Email 2 (Reminder, stronger CTA)
                      → [Time Delay] → Email 3
```

### Крок 3 — Структура листів

**Email шаблон (структура):**
- Subject Line (A/B тест: варіант A та B)
- Preview Text (≤90 символів)
- Header: логотип + навігація
- Body: заголовок → проблема/бажання → рішення → CTA
- Footer: unsubscribe link (обов'язково), адреса

**Abandoned Cart Email послідовність:**
```
Email 1 (1 год): "Ти щось забув?" — м'який нагадувач
Email 2 (24 год): Показати товари + соціальний доказ
Email 3 (72 год): Знижка 10% або безкоштовна доставка
```

### Крок 4 — Сегменти аудиторій
```
VIP Customers:       "Placed Order" count ≥ 3 AND total ≥ $200
At-Risk Customers:   "Last purchase > 60 days" AND "purchased ≥ 2x"
Engaged Subscribers: "Opened email in last 30 days"
SMS Subscribers:     "Consented to SMS" = true
```

### Крок 5 — Налаштування в Klaviyo UI
```
1. Flows → Create Flow → Browse Templates або From Scratch
2. Вибрати тригер → налаштувати фільтри тригера
3. Додати Time Delay (напр. 1 hour)
4. Додати Email action → Templates → Design email
5. Додати Conditional Split (якщо потрібно)
6. Review → Set Flow Live (або Manual для тесту)
```

### Крок 6 — SMS автоматизація (якщо потрібно)
- Підключити Klaviyo SMS (US/CA: потрібен toll-free номер або short code)
- Дотримання TCPA: SMS тільки з явною згодою
- Обмеження: не надсилати SMS з 21:00 до 8:00 (часовий пояс отримувача)

## Формат виводу
```
## Klaviyo Flow: [Назва]

### Схема Flow
Trigger: [Event]
├── Delay: [X год/днів]
├── Email 1: "[Subject Line]"
│   ├── Conditional Split: Opened?
│   │   ├── Yes → Delay → Email 2a
│   │   └── No  → Delay → Email 2b
└── Email 3: "[Subject Line]"

### Тексти листів

**Email 1**
Subject: ...
Preview: ...
Body: ...
CTA: ...

### Сегменти
- Включити: ...
- Виключити: ...

### KPI для відстеження
- Open Rate ціль: >25%
- Click Rate ціль: >3%
- Revenue per Recipient: $X
```

## Правила
- Unsubscribe link — обов'язковий у кожному листі (CAN-SPAM / GDPR)
- A/B тест subject line — завжди для кампаній з аудиторією > 1000
- Виключати поточних покупців з abandoned cart flow
- SMS вимагає окремої явної згоди — не включати всіх email-підписників
- Для Shopify: перевірити що Klaviyo JS snippet встановлений у темі
- Не надсилати більше 1 листа на день у будь-якому flow
