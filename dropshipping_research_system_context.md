# АРХІТЕКТУРА ТА КОНТЕКСТ ПРОЄКТУ

## Dropshipping Product Research System

Автоматизована система пошуку, перевірки та оцінювання товарів для дропшипінгу.
Ринки: **US · CA · GB · AU · NZ**.
Поточна версія контексту · 18 липня 2026.

---

## Коротко про систему

Це єдиний операційний контекст для побудови n8n-системи дослідження товарів. Документ фіксує ціль, послідовність роботи, ролі таблиць, правила цілісності даних і очікуваний фінальний результат.

**Ключовий принцип:** один товар отримує один стабільний `product_id`, який без жорстко прописаних значень проходить через усі гілки дослідження.

## Що ми будуємо

Ми будуємо автоматизовану систему дослідження товарів для дропшипінгу на базі **n8n, Google Sheets, SerpApi, Apify** та зовнішніх джерел даних.

Система повинна прийняти нішу або ключове слово, знайти потенційний товар, перевірити його попит і конкуренцію, створити один запис товару, знайти постачальників і конкурентів, дослідити їхню рекламу та на основі всіх доказів сформувати фінальне рішення щодо тестування товару.

Основні країни дослідження: US, CA, GB, AU, NZ.

## Головна ціль

Для кожного товару система має відповісти на такі питання:

1. Чи є реальний попит на товар?
2. У яких країнах і на яких платформах товар набирає популярність?
3. Чи існує довготривала реклама саме цього товару?
4. Хто зараз продає товар, за якою ціною та з якими оферами?
5. Чи є відповідні постачальники, яка закупівельна та повна landed cost?
6. Які конкуренти рекламуються, що ще вони продають і як довго працюють їхні оголошення?
7. Які рекламні формати, хуки, офери, CTA та посадкові сторінки використовують конкуренти?
8. Чим можна відрізнити нашу пропозицію?
9. Чи варто запускати товар у тест, відкласти його або відхилити?

## Основний порядок роботи

1. Отримати початкову нішу, ключове слово або товар.
2. Зібрати ключові слова для пошуку.
3. Перевірити органічні сигнали на YouTube, Instagram, Facebook, TikTok та інших джерелах.
4. Перевірити Google Shopping у п'яти країнах і вибрати найкращі релевантні товари.
5. Після підтвердження створити один товар у `02_Products` з одним стабільним `product_id`.
6. Знайти актуальні пропозиції продавців через Google Shopping/SerpApi.
7. Розділити продавців на SUPPLIER і COMPETITOR.
8. Записати постачальників у `04_Suppliers`, конкурентів — у `05_Competitors`.
9. Перевірити Meta Ads Library у двох окремих режимах:
   - чи рекламує конкурент саме досліджуваний товар;
   - які оголошення конкурент запускає загалом, що рекламує і як довго.
10. Записати кожне підтверджене оголошення в `09_Ads`.
11. Знайти в соцмережах конкурента публікації саме про досліджуваний товар. Загальні профілі або нерелевантні пости не приймати.
12. Агрегувати рекламу та конкурентні дані в `05_Competitors`.
13. Розрахувати оцінки й фінальне рішення в `07_Shortlist`.

## Важливе розділення рекламних гілок

### 1. Перевірка реклами конкретного товару

**Мета:** визначити, чи рекламує конкретний конкурент саме поточний товар.

**Результат:**
- `relevant_product_ads`;
- `ads_30_plus_days`;
- `longest_ad_days`;
- `advertising_status`;
- `best_ad_url`;
- `best_landing_page_url`.

Якщо магазин має рекламу, але не рекламує цей товар, результат має бути `NO_RELEVANT_ADS`.

### 2. Аналіз усієї реклами конкурента

**Мета:** зрозуміти рекламну стратегію магазину незалежно від того, чи рекламує він поточний товар.

Для кожної реклами збираємо:
- рекламодавця;
- що рекламується;
- текст і заголовок;
- CTA та офер;
- посадкову сторінку;
- формат і платформи;
- creative URL;
- дату запуску, статус і `days_running`;
- рекламні хуки;
- `ad_score`.

**Ці дві гілки не можна змішувати.** Наявність реклами магазину не означає, що він рекламує досліджуваний товар.

## Соцмережі конкурентів

Соцмережі конкурента потрібні не для загальної оцінки популярності профілю. Їх використовуємо, щоб знайти конкретний пост, Reel, TikTok або YouTube-відео саме про досліджуваний товар.

URL приймається тільки коли одночасно підтверджено:
- це сторінка або канал конкретного конкурента;
- матеріал стосується потрібного товару;
- URL веде на конкретний матеріал, а не просто на профіль.

Загальні пости Amazon, Walmart, eBay чи інших маркетплейсів не вважаються доказом для окремого marketplace-продавця.

## Таблиці системи

| Таблиця | Призначення | Основний результат |
|---|---|---|
| `00_Niches` | Активні ніші та категорії | Пріоритет і статус дослідження |
| `01_Inbox` | Вхідні повідомлення та файли | Черга на обробку |
| `02_Products` | Головна сутність товару | Один рядок на `product_id` |
| `06_Keywords` | Ключі для всіх пошукових гілок | Намір, країна, корисність |
| `03_Market_Signals` | Органічні й ринкові докази | Метрики, тренд, `signal_score` |
| `09_Ads` | Одна реклама — один рядок | Креатив, офер, тривалість, `ad_score` |
| `10_Discoveries` | Суміжні знайдені можливості | Нові кандидати та ніші |
| `04_Suppliers` | Постачальники та логістика | Landed cost, склад, ризики |
| `05_Competitors` | Конкуренти й агрегована аналітика | Ціни, офери, реклама, можливості |
| `07_Shortlist` | Фінальне оцінювання | Рішення та `next_action` |
| `99_Lists` | Системні довідники | Допустимі статуси й типи |

**00_Niches** — довідник активних ніш і категорій дослідження. Містить пріоритет, країну, мову та статус дослідження.

**01_Inbox** — вхідна черга повідомлень і вкладень. Зберігає сирий запит, статус обробки, `product_id` та помилки.

**02_Products** — головна таблиця товарів. Один рядок дорівнює одному товару. Тут зберігаються назва, опис, проблема, аудиторія, wow-factor, сезонність і загальний статус.

**06_Keywords** — усі ключові слова для пошуку товару, реклами, трендів, конкурентів і постачальників. Кожен ключ пов'язаний із `product_id` та/або `niche_id`.

**03_Market_Signals** — органічні та ринкові сигнали: YouTube, Instagram, Facebook, TikTok, Google Shopping, рейтинги, перегляди, взаємодії, тренд і `signal_score`.

**09_Ads** — одна реклама — один рядок. Тут зберігаються Meta Ads та інші рекламні сигнали: рекламодавець, текст, формат, офер, CTA, landing page, creative URL, дати, `days_running` і `ad_score`.

**10_Discoveries** — суміжні товари та нові можливості, випадково знайдені під час дослідження. Використовується для створення нового кандидата або оновлення існуючої ніші.

**04_Suppliers** — постачальники товару: платформа, закупівельна ціна, доставка, landed cost, склад, рейтинг, замовлення, варіанти, брендування, медіа, stock status і ризики.

**05_Competitors** — один конкурент — один рядок. Зберігає магазин, товарну сторінку, ціну, офер, доставку, рейтинги, URL реклами та соцмереж, насиченість, сильні й слабкі сторони та можливість для диференціації.

**07_Shortlist** — фінальна таблиця оцінювання товарів. Містить demand, creative, competition, margin, supplier, logistics і risk score, загальний бал, рішення та наступну дію.

**99_Lists** — системні довідники: допустимі статуси, типи, значення та списки для валідації.

## Правила цілісності даних

- `product_id` створюється один раз і передається через усі наступні гілки без жорстко прописаних значень.
- `competitor_id`, `supplier_id`, `signal_id`, `ad_id`, `keyword_id` та інші ID мають бути стабільними й детермінованими.
- Google Sheets працює через **Append or Update Row** із правильною ID-колонкою для зіставлення.
- Порожні або `undefined` значення не повинні стирати вже збережені URL та аналітику.
- Автоматичний mapping не повинен створювати випадкові додаткові колонки.
- Сирі оголошення записуються в `09_Ads`; агрегований висновок про конкурента — в `05_Competitors`.
- Supplier, competitor, market signal, exact-product ad і all-competitor ads є різними типами даних і не змішуються.
- Випадковий результат пошуку не приймається без перевірки імені рекламодавця або домену посадкової сторінки.

## Що хочемо отримати в результаті

Для кожного `product_id` система повинна автоматично сформувати повне досьє:

- підтверджений товар і його ніша;
- набір ключових слів;
- органічні та ринкові сигнали по країнах;
- список активних постачальників і landed cost;
- список реальних конкурентів, ціни та офери;
- статус реклами саме цього товару;
- повний список підтвердженої реклами конкурентів;
- аналіз рекламних форматів, тривалості, хуків, оферів і креативів;
- підтверджені продуктові матеріали в соцмережах конкурентів;
- сильні та слабкі сторони ринку;
- можливість для кращої пропозиції;
- фінальний score, рішення і `next_action`.

Фінальна мета — не просто знайти популярний товар, а отримати **доказове рішення**: чи має товар попит, чи можна його вигідно постачати, наскільки сильна конкуренція, як його краще рекламувати та чи варто запускати тест.

## Поточний етап

Поточна тестова гілка працює з товаром **PRD-1784364546724** і ключем **magnetic drill dust collector**.

Уже виконано:
- знайдено конкурентів через Google Shopping;
- перевірено Meta-рекламу саме товару;
- релевантної реклами саме товару серед перевірених конкурентів не знайдено;
- знайдено 34 підтверджені загальні реклами конкурентів: Miles Kimball — 9, MJS Electrical Products & Supplies — 23, All Preparation Equipment — 2;
- підготовлено нормалізацію цих оголошень для запису в `09_Ads`;
- зібрано Google Shopping по 3 ключах групи × 5 країн (EXACT — 200 оферів,
  CORE — 200, RELATED — 210; разом 610, результати є в усіх 5 країнах);
- підготовлено три вузли гілки Shopping: нормалізація оферів із протягуванням
  контексту (`niche_id`, `niche`, `keyword_id`); агрегація для апдейту
  `06_Keywords` (Append or Update за `keyword_id`, мапиться лише
  `product_id`, трендові поля не чіпаються); створення рядка товару в
  `02_Products` (Append or Update за `product_id`, мапляться тільки заповнені
  поля). Саме в цій гілці створюється стабільний `product_id`
  (`PRD-{timestamp}`, один на запуск); якщо рядки `06_Keywords` уже
  містять `product_id` з попереднього прогону, використовується наявний;
- зафіксовано зміну моделі `06_Keywords` на по-країнну: один ключ проходить
  по 5 країнах, `keyword_id` завжди по-країнний і повністю динамічний
  (`KEY-{niche}-{code}-{COUNTRY}-{LEVEL}`), зіставлення в усіх гілках іде
  за цим ID без зрізання сегмента країни;
- гілка Trends переведена на по-країнну модель і працює: контекст читається
  з вузла `Prepare 5 Countries` (база `keyword_id` без країни й рівня;
  по-країнний ID збирається динамічно, рівень сіда — EXACT), вузол метрик
  обробляє й error-відповіді SerpApi як NO_DATA. Результат прогону EXACT
  від 19.07.2026: US — NO_DATA, CA — SPIKES_ONLY (1 сплеск),
  GB — SPIKES_ONLY (1 сплеск), AU — SPIKES_ONLY (2 сплески), NZ — NO_DATA:
  органічний пошуковий попит на точний ключ слабкий, рішення тягнуть
  Shopping- і рекламні сигнали.

- побудована й перевірена на живих даних гілка **Trends Related**: після
  `Analyze Google Trend` стоїть IF (`trend_direction` ≠ NO_DATA і ≠
  SPIKES_ONLY — related перевіряється лише в країнах з реальним сигналом),
  далі два SerpApi-запити (`RELATED_QUERIES`, `RELATED_TOPICS`, обов'язково
  з `geo`) і два вузли нормалізації: `Analyze Related Queries`
  (TOP → кандидати `06_Keywords` зі статусом NEW, RISING → `10_Discoveries`)
  та `Analyze Related Topics` (компанії з TOP і RISING → бренд-сигнали;
  RISING-теми → `10_Discoveries` тільки після фільтра релевантності:
  назва з 2+ слів або перетин із токенами сід-ключа — однослівні
  абстракції на кшталт Art/Wall/Ceiling відкидаються). ID детерміновані
  (hash від тексту+країни), дедуплікація в межах прогону.
  Живий прогін 19.07.2026 дав чистий вихід: знахідки Thickness planer
  (Breakout US), Drill bit / Hammer drill / Drill Dust Collector (GB)
  і бренд-сигнали Bosch, Makita, Milwaukee Tool. Тест 19.07.2026 на ключі
  `drill dust collector` (US, GB): у топі US — `nail dust collector`
  (суміжна манікюрна ніша, кандидат у Discoveries), підтверджено власний
  RELATED-ключ `hammer drill dust collector` (+60% rising).

**Наступний крок:** прогнати гілку Shopping (протягнути `product_id` у групові рядки `06_Keywords`); записати підтверджені оголошення в `09_Ads`, агрегувати їх за `competitor_id` і оновити рекламний аналіз у `05_Competitors`.

---

## Додаток. Фактична схема спредшита

Google Spreadsheet **«Dropshipping Product Research System»**, 11 вкладок.
Експорт схеми (SCHEMA EXPORT) від 18.07.2026; `last_row` показує наповнення на момент експорту.

### TAB 1 — `00_Niches` (sheet_id: 0, last_row: 7)
```
niche_id, niche, marketplace_category, priority, country, language, active,
research_status, last_researched_at, notes, record_type
```

### TAB 2 — `01_Inbox` (sheet_id: 692944208, last_row: 1)
```
received_at, telegram_message_id, telegram_user_id, telegram_username, input_type,
raw_text, attachment_file_id, processing_status, product_id, error_message
```

### TAB 3 — `02_Products` (sheet_id: 1297735747, last_row: 2)
```
product_id, created_at, niche_id, niche, product_name, product_name_ua, category,
product_description, problem_solved, target_audience, wow_factor, demo_potential,
seasonality, first_found_source, status, notes
```

### TAB 4 — `06_Keywords` (sheet_id: 445875570)
Фактичний порядок колонок (підтверджено 18.07.2026; відрізняється від
початкового експорту — усі Sheets-вузли мусять мапитися за назвами заголовків):
```
keyword_id, niche_id, status, keyword, niche, product_id, keyword_type,
search_platform, country, language, search_intent, date_checked, result_count,
trend_direction, usefulness, notes
```
Модель зберігання — **по-країнна** (рішення від 19.07.2026, замінює
попередню групову модель): один сід-ключ проходить по всіх країнах
довідника (US, CA, GB, AU, NZ), один рядок = ключ × країна. Формат
`keyword_id` — `KEY-{niche}-{code}-{COUNTRY}-{LEVEL}` (наприклад
`KEY-003-MDDC2026-US-EXACT`). Усі значення (`niche_id`, база ID, країни,
рівні, `product_id`) формуються завжди динамічно з контексту сіда та
довідника країн — жодних жорстко прописаних значень у вузлах.
Append or Update у вкладку йде за по-країнним `keyword_id`; зрізати
сегмент країни з ID більше не потрібно ніде в гілці.
Поле `usefulness` — ручна оцінка корисності ключа; автоматика його не
перезаписує (якість даних перевірок фіксується в `notes`).

### TAB 5 — `03_Market_Signals` (sheet_id: 899344591, last_row: 1)
```
signal_id, product_id, source, signal_type, source_url, keyword_used, country,
date_found, content_date, days_running, views, likes, comments, shares, rank,
rating, reviews, trend_direction, signal_score, notes, keyword, date_checked,
saves, CTR
```

### TAB 6 — `09_Ads` (sheet_id: 1415266174, last_row: 1)
```
ad_id, discovery_id, keyword_id, product_id, source, advertiser_name,
advertiser_url, ad_library_url, landing_page_url, country, publisher_platforms,
ad_status, start_date, end_date, days_running, ad_format, ad_text, headline, cta,
offer, price, currency, impressions, reach, creative_url, ad_score, checked_at,
notes
```

### TAB 7 — `10_Discoveries` (sheet_id: 1641343226, last_row: 1)
```
discovery_id, source_product_id, discovered_at, candidate_name, candidate_name_ua,
proposed_niche, source, seed_keyword, raw_ads_count, relevant_ads_count,
unique_advertisers, longest_ad_days, countries, advertisers, store_urls,
confidence_score, status, product_id, notes
```

### TAB 8 — `04_Suppliers` (sheet_id: 1132960998, last_row: 1)
```
supplier_id, product_id, platform, supplier_name, product_url, product_cost,
shipping_cost, landed_cost, currency, delivery_country, delivery_days, warehouse,
supplier_rating, orders, reviews, recent_reviews_quality, variants,
branding_available, media_available, stock_status, red_flags, checked_at
```

### TAB 9 — `05_Competitors` (sheet_id: 1371725819, last_row: 1)
```
competitor_id, product_id, brand_name, store_url, product_url, country,
selling_price, compare_at_price, currency, offer, bundle, free_shipping,
main_hook, target_audience, ad_url, youtube_url, facebook_url, instagram_url,
tiktok_url, product_page_quality, review_count, rating, saturation_score,
strengths, weaknesses, opportunity, checked_at
```

### TAB 10 — `07_Shortlist` (sheet_id: 955741328, last_row: 1)
```
product_id, product_name, niche_id, niche, demand_score, creative_score,
competition_score, margin_score, supplier_score, logistics_score, risk_score,
total_score, decision, next_action, analyzed_at
```

### TAB 11 — `99_Lists` (sheet_id: 215873162, last_row: 51)
```
list_name, list_value, sort_order, active
```

### Нотатки щодо схеми

- У `03_Market_Signals` є дубльовані за змістом пари колонок: `keyword_used`/`keyword`
  і `date_found`/`date_checked`. Для автоматизації слід визначити основну колонку
  в кожній парі, щоб запис ішов в одне місце.
- Поля товарної рекламної гілки (`relevant_product_ads`, `ads_30_plus_days`,
  `longest_ad_days`, `advertising_status`, `best_ad_url`, `best_landing_page_url`)
  на момент експорту відсутні серед колонок `05_Competitors` — агрегати рекламного
  аналізу потрібно або додати колонками, або зберігати в наявних полях
  (`ad_url`, `saturation_score`, `notes`).
