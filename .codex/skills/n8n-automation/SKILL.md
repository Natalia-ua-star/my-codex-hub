---
name: n8n-automation
description: "Побудова n8n workflows: вузли, credentials, self-hosted налаштування. Використовуй коли: 'n8n workflow', 'автоматизація n8n', 'зроби в n8n'."
risk: medium
source: local
date_added: "2026-06-12"
---

# n8n-automation

## Що робить

Проектує та реалізує автоматизації в n8n: від простих лінійних workflows до складних розгалужених сценаріїв з умовами, циклами, HTTP-запитами та кодом. Підтримує self-hosted та cloud-версії.

## Тригери

- "n8n workflow"
- "автоматизація n8n"
- "зроби в n8n"
- "n8n вузол"
- "налаштуй n8n"
- "побудуй workflow n8n"

## Вхідні дані

- Опис процесу: подія → трансформація → результат
- Список сервісів для інтеграції
- Тип запуску: Webhook / Schedule / Manual / другий workflow
- Версія n8n (self-hosted / cloud) та наявність credentials

## Алгоритм

1. **Уточнення мети** — що є тригером, які дані обробляються, що є результатом.
2. **Вибір trigger-вузла** — Webhook, Schedule Trigger, n8n Trigger, Manual Trigger або App Trigger.
3. **Побудова ланцюга вузлів** — описати послідовність: Trigger → Set → IF → HTTP Request → [Merge / Split In Batches].
4. **Credentials** — визначити типи автентифікації (API Key, OAuth2, Basic Auth) для кожного сервісу.
5. **Трансформація даних** — використати вузли Set, Code (JavaScript), Function для маппінгу та обчислень.
6. **Умови та гілки** — IF-вузол для бінарного розгалуження; Switch-вузол для множинних умов.
7. **Обробка помилок** — додати Error Trigger workflow або Continue On Fail на критичних вузлах.
8. **Тестування** — Execute workflow → перевірити output кожного вузла в панелі → виправити вирази.
9. **Активація та моніторинг** — увімкнути workflow, налаштувати Executions log retention.

## Правила

- Вирази в n8n мають синтаксис `{{ $json["field"] }}` або `{{ $node["NodeName"].json["field"] }}`.
- Для доступу до даних попереднього вузла: `{{ $json }}` (поточний), `{{ $('NodeName').item.json }}` (конкретний).
- Split In Batches — використовувати при обробці великих масивів (> 100 елементів) щоб уникнути timeout.
- Self-hosted: переконатись що `N8N_BASIC_AUTH_ACTIVE=true` і webhooks доступні ззовні (reverse proxy).
- Не зберігати секрети у вузлах Set — використовувати n8n Credentials або змінні середовища.
- Code-вузол підтримує тільки синхронний JS (або async/await); `require()` недоступний у cloud-версії.
- Зберігати workflow як JSON для бекапу та версіонування.

## Формат виходу

```
## Схема Workflow
[Manual/Webhook/Schedule Trigger]
↓
[Set] — нормалізація вхідних даних
↓
[IF] — умова: ...
  ├─ TRUE → [HTTP Request] — назва запиту
  └─ FALSE → [Set] — fallback значення
↓
[App Node] — фінальна дія

## Вузли та налаштування
| Вузол | Тип | Ключові параметри |
|-------|-----|-----------------|
| ...   | ... | ...             |

## Credentials
| Сервіс | Тип автентифікації | Де взяти ключ |
|--------|--------------------|---------------|
| ...    | ...                | ...           |

## Вирази (приклади)
- `{{ $json["id"] }}` — ID з поточного вузла
- `{{ $('NodeName').item.json["email"] }}` — email з конкретного вузла

## Рекомендації
- [список нюансів та обмежень]
```
