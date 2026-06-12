---
name: klaviyo-automation
description: "Email/SMS автоматизація в Klaviyo: flows, сегменти, кампанії для e-commerce. Використовуй коли: 'Klaviyo', 'email автоматизація', 'налаштувати flow'."
risk: medium
source: local
date_added: "2026-06-12"
---

# klaviyo-automation

## Що робить

Налаштовує email та SMS автоматизації в Klaviyo для e-commerce: flows, сегменти, кампанії, A/B-тести, умовні розгалуження. Орієнтовано на Shopify-магазини та дропшипінг.

## Тригери

- "Klaviyo"
- "email автоматизація"
- "налаштувати flow"
- "Klaviyo flow"
- "email кампанія"
- "SMS автоматизація"
- "налаштувати Klaviyo для Shopify"

## Вхідні дані

- Назва і мета flow (welcome series, abandoned cart, post-purchase тощо)
- Аудиторія: новий підписник, покупець, конкретний сегмент
- Тип повідомлень: email / SMS / обидва
- Тон бренду, наявні шаблони або приклади
- Підключений Shopify-магазин (так/ні)

## Алгоритм

1. **Визначити flow-тригер** — Metric (Placed Order, Added to Cart), List/Segment, Date, API тощо.
2. **Спроектувати структуру** — намалювати гілки flow: Trigger → Time Delay → Email → Conditional Split → Email A / Email B.
3. **Сегментація** — описати умови Conditional Split (купив / не купив, відкрив / не відкрив).
4. **Зміст листів** — для кожного кроку вказати: тема, preview text, CTA, персоналізація (first name, product name).
5. **Затримки** — рекомендувати тайминги: Welcome (одразу), Abandoned Cart (1 год → 24 год → 3 дні).
6. **Фільтри flow** — додати Smart Sending, quiet hours, виключити вже-конвертованих.
7. **SMS (якщо потрібно)** — окремий SMS-крок з текстом до 160 символів + opt-out посилання.
8. **A/B тест** — визначити змінну (тема листа / час відправки / CTA), розмір вибірки, переможний критерій.
9. **Аналітика** — вказати KPI для моніторингу: Open Rate, Click Rate, Revenue per Recipient, Unsubscribe Rate.

## Правила

- Smart Sending вмикати для всіх promotional flows (запобігає надмірній частоті).
- Для abandoned cart — обов'язково перевіряти чи замовлення не розміщено перед кожним наступним листом.
- Персоналізація: `{{ first_name|default:'there' }}` — завжди з fallback.
- SMS в США/Канаді вимагає явного opt-in — не додавати номери без згоди.
- Не надсилати більше 1 SMS на тиждень на холодну аудиторію.
- Welcome series: мінімум 3 листи (1-й одразу, 2-й через 2 дні, 3-й через 5 днів).
- Post-purchase flow відокремлювати від transactional emails (вони йдуть з різних відправників).

## Стандартні flow для e-commerce

| Flow | Тригер | Кількість кроків | Мета |
|------|--------|-----------------|------|
| Welcome Series | Joined List | 3-5 emails | Знайомство з брендом |
| Abandoned Cart | Added to Cart | 3 emails (+ SMS) | Повернути покупця |
| Browse Abandonment | Viewed Product | 2 emails | Нагадування |
| Post-Purchase | Placed Order | 2-4 emails | Retention + upsell |
| Win-Back | Last Order > 90 days | 2-3 emails | Реактивація |
| Sunset | Low engagement > 180 days | 1 email + clean | Гігієна списку |

## Формат виходу

```
## Flow: [назва]
Тригер: [тип тригера]
Аудиторія: [опис сегмента]

### Структура
Trigger
↓ Delay: [час]
Email 1: "[тема]" — [мета листа]
↓ Conditional Split: [умова]
  ├─ YES → Email 2A: "[тема]"
  └─ NO  → Delay 24h → Email 2B: "[тема]"

### Зміст листів
| # | Тема | Preview Text | CTA | Персоналізація |
|---|------|-------------|-----|----------------|
| 1 | ... | ... | ... | ... |

### KPI для відстеження
- Open Rate: ціль > X%
- Revenue per Recipient: ціль $X
```
