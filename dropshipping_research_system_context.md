# Dropshipping Research System — повний контекст системи

> Автоматизована система пошуку й перевірки товарів для дропшипінгу.
> Цільові ринки: **US, CA, GB, AU, NZ**.
> Сховище даних: Google Spreadsheet **«Dropshipping Product Research System»**, 11 вкладок.
> Головний результат — повне доказове досьє кожного товару: попит, країни, постачальники,
> landed cost, конкуренти, ціни, офери, реклама, соцмережі, ризики, можливості та фінальне
> `decision` із `next_action`.

Схема нижче — фактична, експортована зі спредшита (SCHEMA EXPORT, журнал виконання).

---

## 1. Мета системи

Система проводить кожен потенційний товар через єдиний конвеєр перевірок і накопичує
докази в структурованих таблицях. Рішення про запуск ухвалюється не інтуїтивно, а на
основі зібраного досьє: попит → постачання → конкуренція → реклама → оцінка → рішення.

## 2. Конвеєр (8 кроків)

1. **Знайти потенційний товар** — ідея потрапляє в `01_Inbox` (вхід через Telegram)
   або народжується як кандидат у `10_Discoveries` під час аналізу реклами.
2. **Перевірити органічний попит і Google Shopping** — ключові слова в `06_Keywords`,
   сигнали попиту по країнах у `03_Market_Signals`.
3. **Створити товар з одним стабільним `product_id`** — канонічний запис у `02_Products`;
   усі подальші дані в усіх таблицях посилаються на цей `product_id`.
4. **Знайти постачальників і конкурентів** — постачальники та landed cost у `04_Suppliers`,
   конкуренти, їхні ціни й офери в `05_Competitors`.
5. **Перевірити рекламу саме товару** — гілка «Product Ads» у `09_Ads` (зв'язка через
   `product_id` / `keyword_id`): чи рекламується цей товар, ким, де і як довго.
6. **Проаналізувати всю рекламу конкурентів** — гілка «Competitor Ads» у `09_Ads`
   (зв'язка через `discovery_id`): що рекламують конкуренти, тривалість відкрутки,
   формати, офери, хуки й креативи. Нові товари-кандидати з цього аналізу фіксуються
   в `10_Discoveries`.
7. **Знайти продуктові публікації в соцмережах конкурентів** — соціальні сигнали
   (views, likes, comments, shares, saves) записуються в `03_Market_Signals`;
   посилання на соцмережі конкурентів — у `05_Competitors`.
8. **Розрахувати оцінки та фінальне рішення** — зведення в `07_Shortlist`:
   7 оцінок за напрямами, `total_score`, `decision` і `next_action`.

## 3. Таблиці системи (фактична схема, 11 вкладок)

Порядок вкладок відповідає ходу роботи конвеєра.

### TAB 1 — `00_Niches` (sheet_id: 0)
Каталог ніш. Кожен товар належить до ніші.
```
niche_id, niche, marketplace_category, priority, country, language, active,
research_status, last_researched_at, notes, record_type
```

### TAB 2 — `01_Inbox` (sheet_id: 692944208)
Вхідна черга ідей із Telegram: сирі повідомлення до обробки. Після обробки рядок
отримує `product_id` створеного товару.
```
received_at, telegram_message_id, telegram_user_id, telegram_username, input_type,
raw_text, attachment_file_id, processing_status, product_id, error_message
```

### TAB 3 — `02_Products` (sheet_id: 1297735747)
Канонічний реєстр товарів. Тут народжується стабільний `product_id`. Один товар — один рядок.
```
product_id, created_at, niche_id, niche, product_name, product_name_ua, category,
product_description, problem_solved, target_audience, wow_factor, demo_potential,
seasonality, first_found_source, status, notes
```

### TAB 4 — `06_Keywords` (sheet_id: 445875570)
Ключові слова товару для перевірки органічного попиту та Google Shopping по країнах.
```
keyword_id, product_id, niche_id, niche, keyword, keyword_type, search_platform,
country, language, search_intent, date_checked, result_count, trend_direction,
usefulness, status, notes
```

### TAB 5 — `03_Market_Signals` (sheet_id: 899344591)
Сигнали ринку по країнах: органічний попит, тренди, Google Shopping, соціальні
метрики (views/likes/comments/shares/saves), рейтинги та відгуки маркетплейсів.
```
signal_id, product_id, source, signal_type, source_url, keyword_used, country,
date_found, content_date, days_running, views, likes, comments, shares, rank,
rating, reviews, trend_direction, signal_score, notes, keyword, date_checked,
saves, CTR
```

### TAB 6 — `09_Ads` (sheet_id: 1415266174)
Уся реклама — обидві гілки в одній таблиці:
- **Product Ads**: рядок прив'язаний до `product_id` / `keyword_id`;
- **Competitor Ads**: рядок прив'язаний до `discovery_id`.
```
ad_id, discovery_id, keyword_id, product_id, source, advertiser_name,
advertiser_url, ad_library_url, landing_page_url, country, publisher_platforms,
ad_status, start_date, end_date, days_running, ad_format, ad_text, headline, cta,
offer, price, currency, impressions, reach, creative_url, ad_score, checked_at,
notes
```

### TAB 7 — `10_Discoveries` (sheet_id: 1641343226)
Товари-кандидати, знайдені під час аналізу реклами (`source_product_id` — товар,
з дослідження якого прийшла знахідка). Після підтвердження кандидат отримує
власний `product_id` у `02_Products`.
```
discovery_id, source_product_id, discovered_at, candidate_name, candidate_name_ua,
proposed_niche, source, seed_keyword, raw_ads_count, relevant_ads_count,
unique_advertisers, longest_ad_days, countries, advertisers, store_urls,
confidence_score, status, product_id, notes
```

### TAB 8 — `04_Suppliers` (sheet_id: 1132960998)
Постачальники товару: закупівля, доставка, landed cost, якість постачальника, red flags.
```
supplier_id, product_id, platform, supplier_name, product_url, product_cost,
shipping_cost, landed_cost, currency, delivery_country, delivery_days, warehouse,
supplier_rating, orders, reviews, recent_reviews_quality, variants,
branding_available, media_available, stock_status, red_flags, checked_at
```

### TAB 9 — `05_Competitors` (sheet_id: 1371725819)
Конкуренти: магазини, ціни, офери, хуки, соцмережі, сильні/слабкі сторони, насиченість.
```
competitor_id, product_id, brand_name, store_url, product_url, country,
selling_price, compare_at_price, currency, offer, bundle, free_shipping,
main_hook, target_audience, ad_url, youtube_url, facebook_url, instagram_url,
tiktok_url, product_page_quality, review_count, rating, saturation_score,
strengths, weaknesses, opportunity, checked_at
```

### TAB 10 — `07_Shortlist` (sheet_id: 955741328)
Зведене досьє та рішення по товару.
```
product_id, product_name, niche_id, niche, demand_score, creative_score,
competition_score, margin_score, supplier_score, logistics_score, risk_score,
total_score, decision, next_action, analyzed_at
```

### TAB 11 — `99_Lists` (sheet_id: 215873162)
Службові довідники (статуси, країни, джерела, формати тощо) у форматі key-value.
```
list_name, list_value, sort_order, active
```

## 4. Правила ID

- **`product_id` — єдиний і стабільний.** Створюється один раз у `02_Products` і ніколи
  не змінюється, навіть якщо змінюється назва, ніша чи постачальник товару.
- Дочірні записи (`06_Keywords`, `03_Market_Signals`, `09_Ads`, `04_Suppliers`,
  `05_Competitors`, `07_Shortlist`) містять `product_id` товару, якого стосуються.
- `01_Inbox` не має власного ID кандидата: рядок ідентифікується
  `telegram_message_id`, а після обробки отримує `product_id` створеного товару.
- `10_Discoveries` має власний `discovery_id`; поле `source_product_id` вказує на
  товар, під час дослідження якого знайдено кандидата, а поле `product_id`
  заповнюється після підтвердження кандидата й створення товару.
- Дочірні таблиці мають власні локальні ID (`keyword_id`, `signal_id`, `ad_id`,
  `supplier_id`, `competitor_id`), але зв'язування між таблицями йде через
  `product_id` (та `discovery_id` для гілки Competitor Ads).
- Кожен рядок дослідження містить дату знахідки/перевірки
  (`date_checked` / `date_found` / `checked_at` / `analyzed_at`).

## 5. Розділення рекламних гілок

Обидві гілки живуть в одній таблиці `09_Ads`, але не змішуються — їх розрізняє
спосіб прив'язки:

1. **Product Ads (крок 5)** — реклама *саме цього товару*. Рядок має заповнені
   `product_id` (і зазвичай `keyword_id` — за яким ключем знайдено оголошення).
   Відповідає на питання «чи вже продають цей товар через рекламу і наскільки
   агресивно».
2. **Competitor Ads (крок 6)** — *вся* реклама конкурентів. Рядок має заповнений
   `discovery_id` і описує оголошення конкурента: формат (`ad_format`), тривалість
   (`days_running`, `start_date`/`end_date`), офер (`offer`, `price`), хук
   (`headline`, `ad_text`, `cta`), креатив (`creative_url`). Агрегати цього аналізу
   (кількість оголошень, унікальні рекламодавці, найдовша відкрутка) осідають у
   `10_Discoveries`.

## 6. Оцінки та фінальне рішення

`07_Shortlist` зводить досьє в сім оцінок:

| Оцінка | Що вимірює |
|---|---|
| `demand_score` | попит: органіка, Shopping, тренди, соціальні сигнали |
| `creative_score` | якість і потенціал креативів/хуків (з аналізу реклами) |
| `competition_score` | насиченість і сила конкурентів |
| `margin_score` | маржа: ціни конкурентів проти landed cost |
| `supplier_score` | якість і надійність постачальників |
| `logistics_score` | доставка: строки, склади, країни |
| `risk_score` | ризики (сезонність, red flags, насиченість) |

Підсумок — `total_score`, фінальне `decision` та конкретний `next_action`
(що саме робити далі з цим товаром), з датою аналізу `analyzed_at`.

## 7. Поточний стан роботи

- Спредшит створено, всі 11 вкладок мають фінальні заголовки (схема в розділі 3).
- Довідники `99_Lists` наповнено (51 рядок значень).
- `00_Niches` містить перші ніші (7 рядків), `02_Products` і `06_Keywords` — перші
  тестові записи.
- Робочі таблиці (`01_Inbox`, `03_Market_Signals`, `09_Ads`, `10_Discoveries`,
  `04_Suppliers`, `05_Competitors`, `07_Shortlist`) поки порожні — очікують на
  прогін першого товару через повний конвеєр.
- Наступні кроки: автоматизація кроків конвеєра (вхід із Telegram → `01_Inbox`,
  збирання сигналів і реклами) та доведення перших товарів до `decision`
  у `07_Shortlist`.
