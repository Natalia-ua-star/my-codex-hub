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
- ВАЖЛИВО (виправлення 22.07.2026): IF перед гілкою Related має пропускати
  `SPIKES_ONLY`, а блокувати лише `NO_DATA` — **єдина** умова
  `trend_direction is not equal to NO_DATA`. Інакше для нішевих сідів (де
  тренд усюди NO_DATA/SPIKES_ONLY) IF дає TRUE=0, Related не запускається і
  знахідки не пишуться. На сіді `drill dust collector`: TRUE=3 (US,CA,GB
  SPIKES_ONLY), FALSE=2 (AU,NZ NO_DATA) — Related відпрацьовує коректно.
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
  У гілку додано класифікацію ніш через AI Agent (`Niche Agent`,
  temperature 0) із Google Sheets як інструментом: `Merge Findings`
  (Queries+Topics) → `Niche Agent` → `Apply Niche & Emit Niches` (Code)
  → Switch на 4 виходи. Агент читає `00_Niches` інструментом і співставляє
  кандидата з наявною нішею (nail dust collector → Beauty / Nail Care
  NCH-006, без дублів) або пропонує нову; код детерміновано присвоює новій
  ніші наступний послідовний `NCH-00X` + `priority` і емітить її як
  `record_type: NICHE` → `00_Niches`. Нішу отримують усі типи
  (KEYWORD_CANDIDATE, DISCOVERY, BRAND_SIGNAL); `candidate_name_ua`
  (укр. переклад) — лише DISCOVERY. `discovery_id` уніфіковано до
  name-based (`DSC-{hash(нормалізованої назви)}`) в усіх джерелах, щоб та
  сама знахідка з Trends і Meta зливалась в один рядок.
  Живий прогін 19.07.2026 дав чистий вихід: знахідки Thickness planer
  (Breakout US), Drill bit / Hammer drill / Drill Dust Collector (GB)
  і бренд-сигнали Bosch, Makita, Milwaukee Tool. Запис у вкладки
  підключено й перевірено: кандидати → `06_Keywords` (Append or Update
  за по-країнним `keyword_id` виду `KEY-…-C{hash}-{CC}`; `usefulness`,
  `product_id`, трендові поля не мапляться), знахідки → `10_Discoveries`
  (за `discovery_id`; рекламні колонки, `store_urls`, `product_id`
  лишаються порожніми до пізніших гілок), бренд-сигнали → `11_Brands`
  (Append or Update за `brand_id`, `first_seen` не мапиться; агрегація
  перевірена живим прогоном: Robert Bosch — US, Milwaukee Tool і
  Makita — US,GB, згадки по країнах/списках у notes).
  Тестові рядки від сіда `drill dust collector` підлягають видаленню
  перед бойовим прогоном. Звіт у Telegram-канал підключено:
  `Analyze Related Queries` + `Analyze Related Topics` →
  `Merge Related Results` (Append) → `Build Related Report` →
  `Send Related Report` (статистика кандидатів/знахідок/брендів і
  наступні кроки; запис у таби йде паралельною гілкою через Switch). Тест 19.07.2026 на ключі
  `drill dust collector` (US, GB): у топі US — `nail dust collector`
  (суміжна манікюрна ніша, кандидат у Discoveries), підтверджено власний
  RELATED-ключ `hammer drill dust collector` (+60% rising).

## Незакрите завдання: дозаповнення полів кандидатів `06_Keywords`

Кандидати-ключі з Related (`KEY-REL-…`) пишуться зі статусом **NEW** і
заповненими лише полями відкриття (`keyword`, `niche`, `niche_id`,
`marketplace_category`, `country`, `top_position/value`, `notes`). Поля
`result_count`, `trend_direction`, `usefulness`, `date_checked→CHECKED`
**свідомо порожні** — вони наповнюються ПІЗНІШЕ, коли кандидат сам іде в
перевірку тією ж гілкою Trends (метрики) / Shopping, що й початковий сід.
Тобто потрібен окремий крок «взяти NEW-кандидатів з `06_Keywords` →
прогнати через `Prepare 5 Countries` → Trends-метрики → оновити рядок,
status → CHECKED». Це і є черга на перевірку; поки не побудовано.

## Незакрите завдання: зшивання знахідок із рекламою (`Enrich Discoveries with Ads`)

Колонки `10_Discoveries` `raw_ads_count`, `relevant_ads_count`,
`unique_advertisers`, `longest_ad_days`, `advertisers`, `store_urls`
порожні — вони чекають на докази реклами по знахідці. Зв'язок робиться
за **нормалізованою назвою**: `discovery_id = DSC-{hash(normName(назви))}`,
той самий хеш рахується з тексту/назви реклами. Окремий крок:
вхід — знахідки (`10_Discoveries`) + реклама (Meta results / `09_Ads`);
зіставлення по `normName(назви)`; вихід — оновлені рекламні колонки
знахідки (Append or Update за `discovery_id`). Так знахідка стає
дводжерельною («росте в Trends І рекламується в Meta»). `source_product_id`
знахідки = `product_id` сіда, з якого її знайдено (у тесті порожній, у
проді заповнюється). Будувати ПІСЛЯ стабільної Meta-гілки.

## Статус (послідовність)

Готово й перевірено на живих даних:
- Trends (метрики по країнах, звіт);
- Trends Related (queries/topics → кандидати, знахідки, бренди);
- класифікація ніш (Niche Agent + Apply Niche, автon-реєстрація `00_Niches`);
- уніфікований name-based `discovery_id`;
- Shopping (нормалізація → `product_id` → `02_Products` з AI-карткою →
  `06_Keywords`; Market Signals → `03_Market_Signals`);
- продавці: Split Sellers → `04_Suppliers` / `05_Competitors` (+ landed_cost,
  клікабельні URL через HYPERLINK);
- звіти в Telegram: продукт, Trends, Related, Shopping (об'єднаний ринок +
  продавці — `Build Shopping Report`). `trend_direction` формує вузол
  `Analyze Google Trend` (метрики), а не `Prepare 5 Countries` — IF перед
  Related і будь-які фільтри за трендом читають саме з `Analyze Google Trend`;
- Meta через Metapi: пайплайн Create→Poll→Results працює, Classify Ads
  фільтрує «наш товар» проти суміжних ніш.

Готово додатково (21.07.2026):
- **Enrich Discoveries with Ads** (розширена Meta-гілка): Metapi (q=`drill
  dust collector`) → `Get Discoveries` → `Enrich` (Code) → `10_Discoveries`.
  Знахідка × реклама зіставляється за **виразними словами назви як цілими
  словами** (regex `\b`, не substring — інакше `bit`↔`orbit`, `dust`↔`stardust`);
  беруться лише знахідки з ≥2 виразних (не загальних drill/dust/tool/bit)
  слів, решта пропускається й **очищає** старі рекламні колонки (self-heal).
  Оновлюються тільки рекламні поля (`raw_ads_count`, `relevant_ads_count`,
  `unique_advertisers`, `longest_ad_days`, `advertisers`, `store_urls`,
  `advertising_status`, `notes_ads`) — Trends-поля (`status`, `notes`,
  `candidate_name`, `niche`, `confidence`) не чіпаються. Результат: реальну
  рекламу має лише `nail dust collector` (68 оголошень, 9 продавців, 28 дн) —
  дводжерельна знахідка (Trends +170% + жива Meta-реклама).

Готово додатково (точна Meta-гілка, 21.07.2026):
- **Classify Ads (точний)**: Metapi (розширений q=`drill dust collector`) →
  `Classify Ads` фільтрує рекламу **саме товару** за **суцільною фразою**
  «drill dust collector» (`hay.includes(PHRASE)`), + стоп-ніші
  (nail/manicure/pedicure/beauty) + відсів Marketplace-перепродажу
  (`landing` містить `facebook.com/marketplace`) + дедуплікація за `ad_id`.
  Кожне оголошення → `09_Ads` (Append or Update за `ad_id`; `advertiser_url` =
  `facebook.com/{page_id}`; `offer/price/currency` порожні — Meta не дає з
  тексту; `impressions/reach` недоступні для комерційної реклами назавжди;
  `ad_format`/`ad_score` — пізніше). Живий тест: 4 оголошення товару від
  3 прямих конкурентів (BeauAlori, Flourtish, Emtphasis), усі INACTIVE у
  запінених даних. Звіт `Build Ad Report` → `Send Ad Report` (кількість,
  активні/зупинені, конкуренти, попередження якщо все зупинено).
- **Meta-конкуренти НЕ дублюються в `05_Competitors`** окремим записом:
  реклама вже в `09_Ads` з `product_id`/`keyword_id`, тож прямих
  конкурентів-рекламодавців зведемо в `05_Competitors` на кроці скорингу
  `07_Shortlist` (групування `09_Ads` за рекламодавцем).

ПОВНИЙ ЧИСТИЙ ТЕСТ (22.07.2026, сід `drill dust collector`): пройдено
наскрізь на живих даних — Trends (метрики + IF пропускає SPIKES_ONLY) →
Related → Niche Agent (динамічні ніші) → Switch у 4 таби → Shopping
(товар `PRD-1784709475726` + AI-картка + `product_id` протягнуто в
`06_Keywords` через Remove Duplicates + Sheets) → Market Signals →
Split Sellers (`04_Suppliers`/`05_Competitors`) → Meta точна (4 оголошення
в `09_Ads`) → Meta розширена (Enrich оновив `10_Discoveries`:
nail dust collector 81 оголошення/9 рекламодавців/30 дн, name-based
`DSC-1G6HE0Q` зв'язав Trends+Meta). Уся дослідницька частина валідована.

Незакрито (борги, окремі кроки):
1. **Re-check NEW-кандидатів** `06_Keywords` через Trends-метрики (дозаповнити
   `result_count`/`trend_direction`/`usefulness`, status→CHECKED);
2. **Meta Spy** (топ за тривалістю 30+ днів) як окремий discovery-потік;
3. **Фінальний скоринг** `07_Shortlist` (demand/creative/competition/margin/
   supplier/logistics/risk → рішення + `next_action`; тут же зведення
   Meta-конкурентів у `05_Competitors` з `09_Ads`).

**Наступний крок:** записати підтверджені оголошення в `09_Ads`, агрегувати їх за `competitor_id` і оновити рекламний аналіз у `05_Competitors`.

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

### TAB 5 — `03_Market_Signals` (sheet_id: 899344591)
```
signal_id, product_id, source, signal_type, source_url, keyword_used, country,
date_found, content_date, days_running, views, likes, comments, shares, rank,
rating, reviews, trend_direction, signal_score, notes, keyword, date_checked,
saves, CTR
```
Додано 20.07.2026 для сигналів Google Shopping (числові агрегати по країні,
щоб не витягати їх із `notes` на етапі скорингу):
```
niche_id, keyword_id, offers_total, stores_total, price_min, price_max,
price_median, free_delivery_count, discounted_offers
```
Shopping-сигнал: `signal_type = SHOPPING_OFFERS`, один рядок = товар × країна,
`signal_id = SIG-{hash(product_id|shopping|країна)}`, Append or Update за
`signal_id`.

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

### TAB 12 — `11_Brands` (додано 19.07.2026)
```
brand_id, brand_name, brand_type, topic_mid, niche_id, seed_keyword,
countries, list, best_position, top_value, source, first_seen, last_seen,
status, notes
```
Бренди з Related Topics (компанії з TOP і RISING). Один рядок = один бренд
(`brand_id` = `BRD-{hash(назви)}`), країни списком через кому, згадки по
країнах/списках — у `notes`. Append or Update за `brand_id`; `first_seen`
не мапиться (зберігає дату першої появи). Використання: оцінка насиченості
ніші (`saturation_score`/`competition_score`), черга перевірки Meta Ads,
фільтр брендових ключів серед кандидатів.

### TAB 13 — `08_Semantic_Core` (додано 22.07.2026)
Семантичне ядро: pain-first пошук ключів через DataForSEO, з частотністю,
трендом, бренд-тегами й прапорцем прогалини. Вхідна воронка, що генерує ключі
(`status = NEW`) для пайплайну перевірки. Порядок колонок:
```
keyword_id, niche_id, product_id, keyword, keyword_norm, search_volume, cpc,
competition_index, trend_direction, is_brand, brand_name, is_diy, cluster,
use_for, gap_score, pain_confirmed, source, country, status, created_at
```
`keyword_id = SEM-{hash(keyword_norm)}`. Модель по-країнна, усі значення
динамічні. Append or Update за `keyword_id`. Деталі логіки (кластери, gap_score,
PAIN, соцтренд) — у розділі «Методологія семантичного ядра» вище.

**Побудовано й протестовано 22.07.2026** (пілот drill, US). Ланцюг воркфлоу з 4 нод:
1. **Manual Trigger**
2. **DataForSEO** (офіційна нода) → Resource `Google Ads` → Operation
   `Get Live Google Keywords for Keywords`; Input Mode Manual, 5 сідів,
   Location `United States`, Language `English`. Вихід — `tasks[0].result[]`
   (133 ключі, $0.09).
3. **Parse Semantic Core** (Code, Run Once for All Items) — збирає keyword-обʼєкти
   рекурсивно (незалежно від обгортки), рахує 20 колонок: тренд із `monthly_searches`
   (сер. 3 нових vs 3 старих → RISING/STABLE/FALLING), бренд/DIY-теги, `cluster`
   (BRAND→DIY→PROBLEM→USE-CASE→ATTRIBUTE→CORE), `gap_score = volNorm×compOpen×100`
   (0 для брендів/DIY/насичених), `pain_confirmed`, `keyword_id = SEM-{hash}`.
   Пороги: VOL_REF=100, GAP_MIN_VOL=20, PAIN_MIN=20. Дедуп за `keyword_norm`.
   NICHE_ID/PRODUCT_ID поки в CONFIG (тест); далі підтягнемо з сіда.
4. **Google Sheets** Append or Update у `08_Semantic_Core`, match on `keyword_id`,
   Map Automatically. Записано 131 рядок.

Результат drill підтвердив попередній вердикт: топ-прогалини `dust drill`(gap 57),
`drill machine dust collector`, `drilling machine with dust collection`; ядро
`drill dust collector` gap 0 (competition 100, насичено); бренди gap 0.

Далі: подача сідів із `06_Keywords` (замість ручного вводу) + прогін нейла;
потім AI-enrichment (болі → рекламні кути) і соцтренд-гілки.

### Конвеєр пошуку сідів (seed discovery) — верхівка воронки

Проблема: система стартувала з ключа, вписаного руками. Бракує шару, що САМ
знаходить, що досліджувати. Дві філософії: **згори-вниз** (від категорій `00_Niches`)
і **знизу-вгору** (від того, що вже трендить/продається). Для дропшипінгу головний —
знизу-вгору (свіжий вірал = гроші).

Архітектура (нічого не переробляємо, лише додаємо гілки-джерела):
```
ДЖЕРЕЛА → 01_Inbox (сирі кандидати, дедуп, NEW) → тріаж → 06_Keywords (NEW)
        → 08_Semantic_Core → машина перевірки
```
`01_Inbox` (порожня вкладка) = бункер сирих знахідок. `10_Discoveries` (Meta) —
уже одна гілка цього конвеєра.

Джерела (мапа під наявні інструменти):
| Джерело | Що дає | Готовність |
|---|---|---|
| **DataForSEO Merchant** (Amazon/Shopping bestsellers) | що реально продається | 🟢 готове — **обрано першим (22.07.2026)** |
| DataForSEO / Google Trends (rising) | що зростає в пошуку | 🟢 готове |
| Meta Ads (Metapi) розширений | що рекламують | ✅ частково (`10_Discoveries`) |
| TikTok Creative Center | вірусні товари | 🆕 скрапер |
| AliExpress / Amazon Movers | «гарячі» товари | 🟡 |
| Ручний | ідеї | ✅ |

Перша гілка: **DataForSEO Merchant** — `Google Shopping → Get Products Advanced` за
широкою категорією → назви товарів (брендові, напр. «OTOTO Magic Mushroom Funnel»)
→ **AI-нормалізація** до generic-типу («mushroom funnel») → бункер сідів.

⚠️ `01_Inbox` зайнятий Telegram-ботом — **не чіпаємо**. Бункер конвеєра — нова
вкладка **`12_Seed_Inbox`** (спільна для Merchant і Trending Now та майбутніх джерел).

Вибір інструмента для Google Shopping: і DataForSEO Merchant, і SerpApi тягнуть ті
самі товари. Розподіл, щоб не дублювати: **Merchant** — харвест сідів (дешевше на
обсязі); **SerpApi** — бережемо під **Trending Now** (його унікальна фішка, trend-up).

### TAB 14 — `12_Seed_Inbox` (додано 22.07.2026)
Бункер сирих сідів із конвеєра пошуку (Merchant, Trending Now, далі TikTok/Meta/
YouTube). Колонки спільні для всіх джерел:
```
inbox_id, source, source_detail, raw_title, generic_seed, price, currency, rating,
rating_count, traffic, product_url, source_id, country, status, discovered_at
```
`inbox_id = INB-{hash}`. Merchant заповнює price/rating/rating_count/url; Trending
Now — traffic; спільні — raw_title, generic_seed (AI), source, country, status(NEW).
Потік: `12_Seed_Inbox → тріаж → 06_Keywords(NEW) → 08_Semantic_Core`.

### Стан discovery-конвеєра (23.07.2026) + уніфікований план

**Побудовані джерела товарів (усі пишуть у `12_Seed_Inbox`):**
- **Merchant Google Shopping** (DataForSEO `Get Products Advanced`) — categoryʼю → товари.
  Parse Merchant Products: бренд-блоклист, фікс рейтингу, AI-нормалізація назв → `generic_seed`.
- **Trending Now** (SerpApi `google_trends_trending_now`) — товарна гілка: Parse → AI
  (is_product) → Merge (не фільтрує, позначає NEW/NOT_PRODUCT) → Filter(NEW) → inbox.
  Низький врожай (новинно-важке) — очікувано.
- **TikTok** (ScrapeCreators `Search by hashtag`) — вірусні відео: Parse TikTok
  (desc, `play_count`=перегляди) → AI Extract TikTok (is_product+generic_seed+category+fit)
  → Merge (групує по товару, сумує перегляди) → Filter(NEW) → inbox. Дає найсильніший вірал.

**Контент-гілка (окремо від товарів):** Trending Now → Build Digest Input → OpenAI
(дайджест по напрямках: політика/спорт/культура/фінанси/здоров'я/тех + як використати)
→ Extract Digest (markdown→Telegram HTML, нарізка 3800) → Telegram. Заголовок
«📊 GOOGLE TRENDS NOW» додається кодом.

**Ціни/маржа (валідація, код без AI):** Merchant (keyword=товар) → Parse Prices & Margin —
розділяє офери на постачальників (aliexpress/temu/dhgate/banggood/…) vs роздріб,
рахує `retail_price`(медіана), `supplier_cost`(min або 10-й перцентиль-оцінка),
`margin_ratio`, `margin_verdict`. Якщо постачальника у видачі нема — маржа позначається
«(ОЦІНКА)». Точна собівартість — пізніше через AliExpress-скрапер (Apify/RapidAPI).

**Уніфікований план конвеєра (рефактор — один AI замість по-джерельних):**
```
Джерело1 → Parse ┐
Джерело2 → Parse ┤
CreativeCtr → Parse ├→ COMBINE → Code-сито(ДО AI: дедуп + топ-N за engagement)
Instagram → Parse ┤              → AI(товар+категорія+fit)
Facebook → Parse ┘              → Code-фільтр(ПІСЛЯ AI: HARD_EXCLUDE + категорії + дедуп/сума)
                                → 12_Seed_Inbox
```
- Кожне джерело → свій Parse, що зводить до спільної форми
  (`source, source_detail, raw_title, traffic, product_url, region`).
- Код працює ДВІЧІ: до AI (обрізати обсяг → економія), після AI (точний фільтр).
- **Фільтр категорій:** AI повертає `category` (gadget/tool/home/kitchen/pet/beauty_device/
  apparel/topical_cosmetic/supplement/other); Merge має `EXCLUDE=[topical_cosmetic,supplement]`
  + код-словник `HARD_EXCLUDE` (cream/serum/lotion/supplement/vitamin/…) як страхувальна
  сітка (AI ~90-95%, не 100%). beauty_device (LED-маска) лишаємо, креми/добавки — геть.
- **Схема «топ спочатку»:** в inbox пишемо ВСЕ (банк), а дорогу перевірку
  (Merchant+DataForSEO) робимо лише на **топ-N за переглядами**; решта чекають у черзі.

**Джерела вірал-скрапінгу:** обрано **ScrapeCreators** (один API: TikTok, IG, FB, FB Ads
Library, Pinterest, Reddit, Twitter/Threads/Snapchat; 100 free кредитів) — замінює
Apify+Metapi. Meta-гілка (пізніше) = FB Ads Library, **лише ТОП (довгограючі оголошення)**.

**TikTok discovery-хештеги (для `Search by hashtag`):**
`tiktokmademebuyit, amazonfinds, tiktokshopfinds, amazonmusthaves, cleantok,
kitchengadgets, gadgetsoftiktok, tiktokfinds, homefinds, petsoftiktok,
caraccessories, organizationtiktok, babymusthaves, coolgadgets, viralproducts`.

### Нотатки щодо схеми

- У `03_Market_Signals` є дубльовані за змістом пари колонок: `keyword_used`/`keyword`
  і `date_found`/`date_checked`. Для автоматизації слід визначити основну колонку
  в кожній парі, щоб запис ішов в одне місце.
- Поля товарної рекламної гілки (`relevant_product_ads`, `ads_30_plus_days`,
  `longest_ad_days`, `advertising_status`, `best_ad_url`, `best_landing_page_url`)
  на момент експорту відсутні серед колонок `05_Competitors` — агрегати рекламного
  аналізу потрібно або додати колонками, або зберігати в наявних полях
  (`ad_url`, `saturation_score`, `notes`).

---

## Методологія семантичного ядра (конспект відео + адаптація під нас)

Джерело: відео Ігоря Бурдукова «SEO 2026» (10-річний досвід SEO). Взяли як
готову методологію семантики. Нижче — суть і що з цього НАШЕ.

### Суть: 6 блоків SEO

1. **Спрос (попит).** SEO працює лише там, де є попит. Головне правило —
   **1 запит = 1 інтент = 1 сторінка**. Інтент = реальне намірення користувача
   за запитом (не слова, а що людина хоче отримати). Весь попит ніші збирають в
   окремий документ — **семантичне ядро**: таблиця, де записаний весь попит.
   Три колонки: **кластер** (= сторінка), **ключові слова** (запити під цей
   кластер), **частотність** (скільки шукають/місяць). Семантика — фундамент;
   без неї не побудувати ні структуру, ні контент.
2. **Структура під попит.** Кожна група запитів (кластер) = окрема посадкова
   сторінка в ієрархії (розділ → підрозділ). Зі списку кластерів будують
   майнд-мапу структури сайту.
3. **Технічне здоров'я.** Швидкість (Core Web Vitals), індексація, title/description,
   ієрархія H1, canonical, мікророзмітка, мобільна версія. Інструменти:
   Screaming Frog, перевірка індексації Rush Analytics, SEO Meta in 1 Click, Ahrefs.
4. **Контент, який вирішує задачу.** Відповідати по суті: реальна ціна, точні
   терміни доставки, реальні фото (не сток / не генерація). AI — як конструктор
   скелета, не для набивання ключами.
5. **EEAT + комерційні фактори.** Сигнали довіри: досвід, експертиза,
   авторитетність, надійність. Автор контенту, фото команди, ліцензії, телефон/
   адреса, відгуки, сертифікати.
6. **Зовнішня оптимізація.** Посилальний профіль: DR, беклінки, реферальні
   домени, анкори (Ahrefs). Слідкувати за сплесками спам-посилань.

**Кому SEO НЕ потрібне (4 випадки):** немає пошукового попиту; сезонний/короткий
горизонт; **імпульсні, емоційні покупки** (прикраси, одяг, дизайнерські дрібнички
— там таргет дає в рази більше, ніж SEO); немає ресурсу на рік роботи.

**2026:** пошук роздробився — зверху AI-відповіді (ChatGPT, Perplexity, Alice) +
пара посилань-джерел. Мета — щоб рекомендували скрізь, де клієнт ухвалює рішення
про покупку.

### Що з цього НАШЕ (адаптація під дропшипінг)

**Головний чесний висновок:** дропшипінг = імпульсні покупки з соцстрічок → за
логікою самого відео наш **основний канал — таргет (Meta), а не органічний
SEO-трафік**. Тому семантичне ядро в нас працює НЕ на органіку, а на **3 задачі**:
структура (колекції/картки товарів), таргет реклами, discovery під-ніш. Не
чекаємо від ядра пошукового трафіку — воно інструмент структурування й таргету.

Мапа 6 блоків на нашу систему:

| Блок з відео | Наш еквівалент | Статус |
|---|---|---|
| 1. Попит (Wordstat, частотність) | **Google Trends** — перевірка попиту/напрямку по 5 країнах | ✅ вже є |
| 1. Семантичне ядро | вкладка **`08_Semantic_Core`** (будуємо зараз) | 🔨 в роботі |
| 2. Структура під попит | кластер = колекція / ad-set / варіант товару | планово |
| 4. Контент, що вирішує | наш **AI product card** (картка товару) | ✅ є |
| 5. EEAT / комерц. фактори | елементи довіри магазину (відгуки, політики, контакти) | майбутнє |
| 6. Зовнішня оптимізація | здебільшого НЕ наш кейс (імпульс); лише для контент-SEO | пропускаємо |
| 2026: AI-пошук | товар/магазин має бути цитованим AI-асистентами покупок | врахувати |

### Уточнення моделі `08_Semantic_Core` під впливом відео

Відео змінює акцент: не просто **тегувати** кожен ключ інтентом, а **групувати**
ключі в кластери. Трирівнева модель (як у відео):

- **КЛАСТЕР** = 1 інтент = 1 майбутня сторінка/колекція/ad-set (напр. «nail dust
  collector portable», «nail dust collector for salon»).
- **КЛЮЧІ** = запити, що ведуть на цей кластер.
- **ЧАСТОТНІСТЬ** = trend/volume на ключ — щоб пріоритизувати кластери за реальним
  попитом (кластер без попиту = мусорна сторінка, не робимо).

Правило **«1 запит = 1 інтент = 1 сторінка»** тепер визначає ГРУПУВАННЯ ключів у
`08_Semantic_Core`, а не лише колонку `cluster`. `use_for` (DISCOVERY / ADS / SEO)
лишається як похідне від типу інтенту.

### Двигун ядра — DataForSEO (рішення 22.07.2026), не SerpApi

Причина: семантика вимагає **частотності** (колонка 3 у відео). SerpApi/Trends
дає лише відносний інтерес (0-100), НЕ реальні покази. **DataForSEO дає реальний
`search_volume`, `cpc`, `competition` на кожен ключ + готове поле `search_intent`**
(informational / commercial / transactional / navigational). Тобто:

- частотність — з коробки;
- кластер (намір) — з коробки, **без правил і без AI** (це знімає попереднє
  рішення «клеїти кластери marker-словами»).

Ендпоінти (DataForSEO Labs) на кожен head-термін:
1. **Keyword Suggestions** — лонг-тейли з фразою → ATTRIBUTE / AUDIENCE / TRANSACTIONAL.
2. **Keyword Ideas** — суміжні ключі теми → джерело **discovery** під-ніш.
3. **Questions / Related Keywords** (опц.) — питальні та «searches related to».

SerpApi лишається **необов'язковим доповненням** (PAA/related searches), для ядра
не потрібен. Бюджет: у DataForSEO ~$50 кредиту; Labs-виклики дешеві, але їх треба
батчити (обмежувати к-сть head-термінів × ендпоінтів за прогін), щоб не палити кредит.

### PAIN/PROBLEM — пріоритетний кластер (ядро дропшипінг-стратегії)

Головна цінність ядра для нас — **підтверджені статистикою болі/проблеми**.
Проблемний запит із реальним обсягом дає одразу три речі:
1. **валідацію попиту** (біль реальний, його гуглять — не здогадка);
2. **кут реклами (hook)** — сам запит = текст креативу («how to stop nail dust»);
3. **тему контенту/SEO** — стаття «як позбутися X».
Плюс **discovery**: шуканий біль без доброго товару = діра ринку, нова ідея товару.

Механіка: у `08_Semantic_Core` кластер **PROBLEM** виділяємо за
`search_intent = informational` + маркер болю (`how to remove / stop / prevent /
get rid of / without / fix / problem`). Прапорець **`pain_confirmed = TRUE`**, коли
`search_volume ≥ поріг`. Такі рядки — найвищий пріоритет; вони живлять банк
рекламних кутів, вибір товару (чи наш товар вирішує шуканий біль) і контент.

### Багатоцільове використання (одна збірка — багато вжитків)

Ядро будуємо один раз, дані працюють на кілька фронтів у часі:
- **зараз (дропшипінг):** болі → рекламні кути + вибір/валідація товару + discovery;
- **потім:** структура сайту (кластер = колекція), SEO-сторінки, теми контенту.
Тому $50 на DataForSEO — це інвестиція в актив, а не разова витрата.

### Прогалини (gap) — головна мета пошуку, і потік «core → пайплайн»

Мета семантичного ядра для нас — **знаходити прогалини**: де попит є, а
пропозиція/конкуренція слабка, тобто те, що люди потребують, а ми можемо закрити.

Дві форми прогалини:
1. **Keyword-gap** — конкретний запит із попитом і слабкою конкуренцією (швидкий
   вхід сторінкою/рекламою).
2. **Need/product-gap** — біль, який люди пишуть, а доброго товару під нього нема →
   **ідея нового товару** (глибше золото дропшипінгу; перетинається з кластером PAIN).

**`gap_score` / `opportunity`** у `08_Semantic_Core` високий, коли одночасно:
- `search_volume ≥ поріг` (попит підтверджений), **І**
- `competition_index` низький (мало продавців/рекламодавців), **І**
- НЕ бренд (`concepts.type != BRAND/OTHER_BRANDS`), **І**
- НЕ DIY (немає `diy / homemade / how to make / build`).

Чесний нюанс: низька competition = **сигнал перевірити, не гарантія** (може бути
незайнята ніша АБО ніша, де ніхто не заробляє). Тому прогалина не є фінальним
рішенням — вона йде далі в пайплайн на перевірку.

**Потік замикається** (ядро = вхідна воронка, стара система = машина перевірки):
```
08_Semantic_Core (болі + прогалини, gap_score, status=NEW)
      ↓  ключі зі status = NEW
Trends (попит) → 05_Competitors → 09_Ads/Meta → 04_Suppliers → 07_Shortlist
```
Тобто ми не переробляємо стару систему, а **добудовуємо їй голову**, яка сама
знаходить, що перевіряти.

### Реальний ендпоінт і фінальні колонки `08_Semantic_Core`

Пілотний прогін (22.07.2026, seed «drill dust collector», US) робили через
`keywords_data / google_ads / keywords_for_keywords / live` — 133 ключі, $0.09.
Цей ендпоінт дає `search_volume`, `cpc`, `competition`/`competition_index`,
12 міс. історії (`monthly_searches` → тренд) і **`keyword_annotations.concepts`**
(автотеги BRAND / OTHER_BRANDS / Tool / Non-Brands — бренди відсіюються безкоштовно).
Обмеження: цей ендпоінт **не дає `search_intent`** — за потреби готового наміру
беремо Labs `keyword_ideas`. Синоніми Google групує в одну частотність
(«drill dust collector» і «drilling dust catcher» = ті самі 480) — **не сумуємо**.

Колонки:
```
keyword_id, niche_id, product_id, keyword, keyword_norm, search_volume,
cpc, competition_index, trend_direction, is_brand, brand_name, is_diy,
cluster, use_for, gap_score, pain_confirmed, source, country, status, created_at
```
- `keyword_id = SEM-{hash(keyword_norm)}` (детермінований, без дублів між прогонами).
- `trend_direction` — RISING / STABLE / FALLING з порівняння середніх останніх 3 vs
  попередніх 3 місяців `monthly_searches`.
- `cluster` — CORE / ATTRIBUTE / USE-CASE / BRAND / DIY / PROBLEM (правила + concepts).
- `use_for` — DISCOVERY / ADS / SEO (похідне від cluster).
- `status` — NEW (підхоплюється пайплайном) / USED / IGNORED.
Модель — по-країнна (як `06_Keywords`); усі ID та значення завжди динамічні.

### Соцтренд-верифікація (рішення 22.07.2026: додаємо всі)

Ключова ідея: **два різні сигнали попиту**.
- **Пошуковий попит (DataForSEO)** — люди вже шукають → evergreen/проблемні товари, SEO.
- **Соцтренд (TikTok/Reels/YouTube/Pinterest)** — попит, що народжується з віральних
  відео → класична дропшип-ракета. Імпульсний товар часто має **низький пошуковий
  обсяг, але вибух у соцмережах** — і саме він продається. Для наших імпульсних
  товарів соцтренд може важити **більше**, ніж Google-обсяг. Найкращий товар світиться
  в обох сигналах або сильно в одному.

Перевіряємо кожен ключ ядра по платформах (обрано «усі»):

| Платформа | Що каже | Чим | Статус |
|---|---|---|---|
| **TikTok** | віральність, чи «злетів» товар | скрапер (Apify / TikTok Creative Center) | 🆕 нова інтеграція, є витрати |
| **Google Trends — YouTube property** | інтерес у YouTube-пошуку | наявний Trends-движок (`gprop=youtube` — параметр уточнити при збірці) | 🟢 легко |
| **Pinterest Trends** | візуальні/проблемні товари, сезонність | Pinterest Trends / скрапер | 🆕 треба доступ |
| **Instagram — органіка** | віральні Reels/пости, хештег-обсяг | скрапер (Apify) | 🆕 нова інтеграція |
| **Facebook — органіка** | віральні пости/групи, згадки | скрапер (Apify) | 🆕 нова інтеграція |
| **Meta Ads Library** | **реклама** у FB/IG (платний сигнал) | Metapi | ✅ уже є |

Важливо не плутати: **Meta Ads Library = реклама FB/IG** (хто платить за покази) —
це вже маємо. **Instagram/Facebook органіка = віральність контенту** (Reels-перегляди,
хештеги, пости) — це окремий, новий сигнал зі скрапером.

Зберігання: `03_Market_Signals`, `signal_type = TIKTOK_TREND / YOUTUBE_TREND /
PINTEREST_TREND / INSTAGRAM_TREND / FACEBOOK_TREND` (один рядок = ключ × платформа ×
країна). У скорингу — вимір **`social_score`** (розширює нинішній creative_score, що
зараз тримається лише на Meta Ads).

Потік із соцсигналом:
```
08_Semantic_Core → Trends + СОЦТРЕНД (TikTok/YouTube/Pinterest) + Meta Ads
      → 05_Competitors → 04_Suppliers → 07_Shortlist(+social_score)
```

Чесний нюанс: **TikTok, Instagram, Facebook (органіка) і Pinterest не мають
безкоштовного офіційного API** — це окремі скрапер-інтеграції (як Metapi для Meta),
з витратами. YouTube-через-Trends — дешевий/готовий. Тому порядок збірки: спершу
YouTube(Trends), далі TikTok, потім Instagram/Facebook органіка, потім Pinterest —
щоб кожну гілку відпрацювати окремо.

---

## ✅ МАШИНА 1 (TikTok Shop discovery) — ЗАВЕРШЕНО (24.07.2026)

Багато-нішевий конвеєр працює end-to-end і **налаштований**. Перший повний прогін
(6 ніш × топ-3 = 17 сідів після дедупу) дав чисту карту ринку з авто-вердиктами.
Підтверджено на практиці:
- **AI-фільтр ніш працює** — Beauty Gadgets = лише пристрої (ендоскоп, іригатор, пилка),
  жодного крему/добавки.
- **Вердикт `momentum` відсіює «вчорашні хіти»** — напр. `pet ball toy` (100K продано,
  80M переглядів за весь час, АЛЕ 0 свіжих відео 2026 + rating 4.0) → 💀 SATURATED,
  тоді як `pet grooming brush` (27K продано, 47% свіжа, ⭐4.4) → 🔥 RISING. Система
  вибирає «хто живий зараз», а не «хто продав більше».
- **STOP-фільтр хештегів очищено** (спільноти/свята/знижки/шум) — лишаються продуктові.
- **Моніторинг Рівня 2 живий** — `check_count` росте, `trend`/`organic_prev` рахуються,
  `discovered_at` заморожено.

Врожай першого прогону (🔥 RISING): caulk tape (100%, 17 відео — найраніший вхід),
plant pots (64%), pet grooming brush (47%), fishing lure (35%), vegetable seeds (22%),
jump starter (21%).

**Наступний крок:** Filter `momentum=🔥 RISING` → Машина 2 (DataForSEO → Semantic Core
→ маржа → TEST → 06_Keywords → 5-country validation).

---

## ✅ МАШИНА 2 (валідація + семантичне ядро) — БАЗОВО ГОТОВО (24.07.2026)

Сценарій `05_DPRS_Semantic Core validation`. Замикає воронку: RISING-сіди з inbox →
перевірка попиту по 5 країнах → семантичне ядро для чемпіонів. Прогнано: 8 RISING →
валідація (5 країн) → 6 STRONG → 1200 рядків ядра в `08_Semantic_Core`.

**Потік:**
```
Manual Trigger → Read Inbox (12_Seed_Inbox) → Filter RISING (NEW + momentum RISING + price≥14)
→ Build Country Batches (5 англ. країн) → DataForSEO Search Volume (HTTP, google_ads/search_volume)
→ Parse Validation (матриця сід×країна + demand_verdict) → Filter STRONG (demand_verdict STRONG)
→ DataForSEO Keywords Core (офіційна Labs нода: keyword_suggestions) → Parse Semantic Core
→ Google Sheets: 08_Semantic_Core (Append/Update, match keyword_id)
```

| Нода | Роль |
|---|---|
| `Read Inbox` | Google Sheets Get Rows з `12_Seed_Inbox` |
| `Filter RISING` | Code: `status=NEW` + `momentum RISING` + `price≥14`; готує `keywords` список |
| `Build Country Batches` | Code: 5 англ. країн (US/UK/CA/AU/NZ), `location_name`+`location_code` |
| `DataForSEO Search Volume` | HTTP POST `keywords_data/google_ads/search_volume/live`; Raw body з коду; batched (5 викликів) |
| `Parse Validation` | Code: матриця сід×країна, `vol_total`, `trend_US`, `demand_verdict` (STRONG/MEDIUM/LOW) |
| `Filter STRONG` | Code: тільки `demand_verdict=STRONG` → на ядро |
| `DataForSEO Keywords Core` | **офіційна Labs нода**, Operation `Keyword Suggestions`, keyword=рядок, location=«United States», language=«English», limit 300 |
| `Parse Semantic Core` | Code: `result[0].items[]` → 20 колонок; кластер з `search_intent_info.main_intent`; gap_score; pain_confirmed |

**Ключові уроки Машини 2:**
- **Валідація vs ядро — різні ендпоінти.** `search_volume` (Google Ads) = точний обсяг по країнах,
  batched списком (дешево, 5 викликів). `keyword_suggestions` (Labs) = лонг-тейли фрази (болі),
  точково по сіду. **`keyword_ideas` НЕ юзати** — категорійне сміття («jump starter»→«doodle jump»/пісні).
- **Дворівнево:** широка дешева валідація (5 країн) → глибоке ядро тільки для STRONG у US.
- **Мова/локація — НАЗВАМИ** для дедикованої/Labs ноди («United States», «English»), не кодами.
- **HTTP body** для DataForSEO: Raw + `JSON.stringify(...)` з коду (JSON-режим n8n глючить на масивах/локації).
- **5 країн — усі англомовні** (US/UK/CA/AU/NZ) → переклад не потрібен. US-ядро універсальне для всіх.
- **Подвійний сигнал:** TikTok momentum × Google trend. Напр. `vegetable seeds` 🔥 на TikTok, але
  ↓FALLING у Google (сезон) → впав зі STRONG на MEDIUM. Один сигнал брехав би.
- **DataForSEO — pay-as-you-go** ($50 депозит тягнеться довго; виклик ~$0.05-0.09); дешевше за SerpApi
  підписку і дає абсолютний обсяг + intent (чого SerpApi не має). SerpApi лишити лише для Trends.

**Використання `08_Semantic_Core`:** фільтр `pain_confirmed=TRUE` → рекламні хуки; `gap_score`↑ →
прогалини (попит+низька конкуренція); `cluster=PROBLEM/COMPARISON` → теми креативів.

**Idea Verdict (капстоун Машини 2):** групує ядро по `product_id`, дає 1 картку рішення на товар —
`вердикт` (ТЕСТ/ПОДИВИТИСЬ/ПРОПУСТИТИ) + причина + попит + тренд + конкуренція + прогалини + болі.
Пише в `13_Verdicts` (match `verdict_id`=VRD-{product_id}) + Telegram (`Build Verdict Report`).
Перший прогін: 4 ТЕСТ (fishing lure, plant pots — обидва 🔥росте; jump starter, litter box — ↓спадає),
2 ПОДИВИТИСЬ (mini chainsaw, fishing rod combo).

### ✅ ВЕРДИКТ v2 — 4-сигнальний (з Meta Ads) — ГОТОВО (24.07.2026)
Додано 4-й, найкомерційніший сигнал: **чи конкуренти прибутково крутять рекламу зараз.**
Реклама 30+ днів = ринок точно прибутковий (ніхто не ллє в збиток місяць).

**Гілка Meta (у Машині 2, паралельно з семантикою):**
```
Filter STRONG ┬→ DataForSEO Keywords Core → Parse Semantic Core → Merge(1)
              └→ Search Ads (ScrapeCreators FB Ad Library) → Parse Meta Ads → Merge(2)
Merge → Idea Verdict v2 → 13_Verdicts + Build Verdict Report → Telegram
```
- **`Search Ads`** (ScrapeCreators, Resource `Facebook Ad Library`, Op `Search Ads`): Query=`{{ $json.generic_seed }}`,
  Run Once for Each Item, Limit 50. НЕ Metapi (той ключ витік).
- **`Parse Meta Ads`** (Code): пара `$("Filter STRONG")`+`$input` по індексу; поля `start_date`/`end_date`/
  `is_active`/`collation_count`; рахує `ad_count`, `ads_30plus`, `longest_days`, `avg_days`, `variations`,
  `ad_verdict` (🟢 PROVEN ≥1 реклама 30+дн / 🟡 TESTING / ⚪ NO ADS).
- **`Merge`** тримає `Idea Verdict`, поки обидві гілки (ядро+реклама) не готові.
- **`Idea Verdict` v2**: читає `$("Parse Semantic Core")` + `$("Filter RISING")` (product_id↔generic_seed)
  + `$("Parse Meta Ads")` (generic_seed↔ad-дані). Вердикт: coreMax<30→ПРОПУСТИТИ;
  proven+кут→ТЕСТ; proven(без кута)→ТЕСТ (диференціація); кут(без реклами)→ПОДИВИТИСЬ; інакше ПОДИВИТИСЬ.
  Додано колонки `реклама`, `реклам_30дн`, `найдовше_дн`.

**Перший прогін v2:** усі 6 → 🟢 PROVEN (конкуренти рекламують роками — fishing lure 1015дн,
mini chainsaw 930дн). Тобто всі 6 ринків підтверджені грошима → усі ТЕСТ; ранг по тренду+довговічності
реклами (fishing lure/plant pots попереду — тренд росте + реклама роками). Ad-сигнал ПІДВИЩив
2 колишні «ПОДИВИТИСЬ» (mini chainsaw, fishing rod) — «тісно, БО прибутково».

**Система тепер 4-сигнальна:** соц (TikTok) × пошук (Google 5 країн) × болі (ядро) × реклама (FB Ads).

---

## РЕЄСТР СЦЕНАРІЇВ (n8n workflows) + СИСТЕМА ТЕГІВ

**Конвенція назв:** `NN_DPRS_<опис>` (номер + код проєкту DPRS + опис).

| № | Назва сценарію | Теги |
|---|---|---|
**Реальна нумерація n8n (джерело правди — станом на 27.07.2026):**
| 01 | `01_DPRS_TikTok Shop discovery` | `M1-discovery · src-tiktok · fn-report · fn-monitor · status-active` |
| 02 | `02_DPRS_Semantic Core validation` | `M2-validation · src-dataforseo · fn-core · status-wip` |
| 03 | `03_DPRS_Prices & Margin` | `M2-validation · src-apify · fn-supplier · fn-verdict · status-active` |
| 04 | `04_DPRS_Shortlist` | `M3-shortlist · fn-report · status-active` |
| 05 | `05_DPRS_Trends Digest` | `M1-discovery · src-trends · fn-report · status-active` |
| 06 | `06_DPRS_Trends Related` | `M1-discovery · src-trends · status-wip` |
| 07 | `07_DPRS_Instagram discovery` | `M1-discovery · src-instagram · status-active` |
| 08 | `08_DPRS_Facebook discovery` | `status-skipped` (Ad Library покриває M2; Marketplace = вживані, слабкий сигнал) |
| 09 | `09_DPRS_YouTube Shorts discovery` | `M1-discovery · src-youtube · status-active` |

(Примітка: аркуші зберегли історичні назви — `06_Margin`, `07_Test_Products` — вони НЕ залежать від номера воркфлоу.)

**Система тегів (4 виміри), вішати по кілька на сценарій:**
- **Етап:** `M1-discovery` (пошук) · `M2-validation` (перевірка) · `M3-shortlist` (фінал/тест)
- **Джерело:** `src-tiktok` · `src-dataforseo` · `src-trends` · `src-merchant` · `src-meta` · `src-apify`
- **Функція:** `fn-report` (Telegram) · `fn-supplier` · `fn-monitor` · `fn-core` · `fn-verdict`
- **Статус:** `status-active` (працює) · `status-wip` (будується) · `status-off` (вимкнено)

Фільтрація в n8n: за тегом показуєш усі `M1-discovery`, усі `status-wip`, усе `src-tiktok`.

---

## РЕЄСТР НАЗВ НОД (n8n) — джерело правди

**Правило:** назви нод у коді (`$("Ім'я")`) мають ТОЧНО збігатися з цим реєстром.
Якщо в n8n перейменували ноду — оновити і тут, і в усіх посиланнях у коді.

### Конвеєр TikTok Shop (discovery за нішею → товари + хештеги)

Потік (з моніторингом — Рівень 2):
```
[ScrapeCreators TikTok Shop Search]  → Parse TikTok Shop
Parse TikTok Shop → [ScrapeCreators Product Details]  (URL динамічний: {{ $json.product_url }})
[Product Details] → Parse Enrichment
Parse Enrichment → AI Extract → Build Seed Inbox → Read Inbox → Merge History → Filter (NEW)
Filter (NEW) ├─→ Google Sheets: 12_Seed_Inbox      (Append or Update, match inbox_id)
             ├─→ Explode Hashtags → Google Sheets: Hashtag_Stats  (Append or Update, match stat_id)
             └─→ Build TikTok Report → Telegram
```

| Назва ноди | Тип | Роль |
|---|---|---|
| `Parse TikTok Shop` | Code (All Items) | з Shop Search → рядки товарів, `traffic=sold_count`, `product_url`=seo_url.canonical_url, `video_url` з video/author, MIN_SOLD, `TOP_N` (сорт по продажах) |
| `Product Details` | ScrapeCreators HTTP | по `product_url` → `product_info` + `related_videos`; **Run Once for Each Item**, URL = `{{ $json.product_url }}` |
| `Parse Enrichment` | Code (All Items) | пара `$("Parse TikTok Shop")` + `$input` по індексу; органіка з `related_videos`, CUTOFF=2026-01-01, `videos_since_2026`, `money_hashtags`, `video_url` (топове related) |
| `AI Extract` | OpenAI Message (JSON, Each Item) | брудний `raw_title` → `generic_seed`+`niche`+`confident` (без is_product — у Shop усе товари) |
| `Build Seed Inbox` | Code (All Items) | merge `$("Parse Enrichment")`+`$input`(AI) по індексу → рядки inbox; `inbox_id=SIG-hash(source_id)`, статус; **дедуп по generic_seed** (`seller_count`,`total_sold`); **`momentum` код-вердикт** |
| `Read Inbox` | Google Sheets (Get Rows) | читає поточний `12_Seed_Inbox` для порівняння з новими даними |
| `Merge History` | Code (All Items) | `$("Build Seed Inbox")` + `$input`(Read Inbox) по `inbox_id`: зберігає `discovered_at` (first-seen), рахує `organic_prev`/`trend`/`momentum_prev`/`check_count`/`checked_at` |
| `Filter (NEW)` | Filter | `{{ $json.status }}` == `NEW` |
| `Explode Hashtags` | Code (All Items) | `source_detail` → 1 хештег = 1 рядок під `Hashtag_Stats`, `stat_id=HSH-hash(tag+product)`, `product_id`=source_id |
| `Build TikTok Report` | Code (All Items) | звіт по товарах → `text` (HTML, 3800); авто-вердикт моментуму + research + постачальники |

**Рівень 2 моніторинг (пам'ять між прогонами):** `Read Inbox`→`Merge History` перед Filter.
Детермінований `inbox_id` + Google Sheets `Append or Update` = той самий товар **оновлюється
на місці** (не дублюється). `Merge History` порівнює нове зі старим по `inbox_id`:
`discovered_at` заморожується (перша поява), `trend` = ↑UP/↓DOWN/→FLAT/🆕NEW за рухом
`organic_views`, `momentum_prev` показує зміну вердикту (напр. ⚡SPIKE→🔥RISING). Автозапуск —
Schedule Trigger. **Пастка Sheets:** значення НЕ починати з `=` (інакше формула `#NAME?`) —
тому `→ FLAT`, не `= FLAT`.

**Звіт Telegram — структура на товар:** назва/ніша, ціна/рейтинг, продано, органіка
(свіжа 2026 / вся), **авто-вердикт `momentum()`**, money_hashtags, 🔒US-лінки(VPN),
research(TikTok/Google), 🏭постачальники(AliExpress/1688/Taobao/CJ/Zendrop за `generic_seed`).

**`momentum(j)` — авто-діагноз по товару** (свіжа органіка vs вся + к-сть свіжих відео):
- `organic_views==0` → 💀 насичено (немає свіжих відео 2026);
- `videos_since_2026<=1` → ⚡ спалах 1 ролика (НЕ тренд — один залетів);
- свіжа ≥20% → 🔥 на підйомі; ≥5% → ⚠️ холоне; <5% → 💀 майже насичено.
Потребує поля `videos_since_2026` — протягнуте через `Build Seed Inbox` (бонус-поля).

**Гео-обмеження TikTok Shop US (важливо):** прямі лінки `shop/pdp/...` (product_url) і
US-відео (`related_videos[].url`) **гео-замкнені на США** — з України віддають
«Product ID is invalid» / «Відео недоступне». Тому в Telegram-звіті лінк — це
**region-neutral пошук** `https://www.tiktok.com/search?q={generic_seed}` (відкривається
всюди, показує доступні відео товару). `product_url`/`video_url` все одно зберігаються
в `12_Seed_Inbox` (довідка / перегляд під VPN). `video_url` тягнеться в `Parse
Enrichment` з топового свіжого `related_videos` (поле `url`, або будується з
`author_id`+`item_id`).

**Ключові правила з'єднань (щоб пари по індексу не з'їхали):**
- `Build Seed Inbox` бере стрілку **з `AI Extract`** (не з Parse Enrichment) — інакше `$input`
  не той, `generic_seed` порожній, статус зривається в REVIEW.
- `AI Extract` і `Product Details` — режим **Run Once for Each Item** (не Execute Once).
- Пари складаються **в коді по індексу** — фізична Merge-нода НЕ потрібна, ланцюг «в рядок».

### Схема `12_Seed_Inbox` (28 колонок — з моніторингом Рівня 2)
```
inbox_id	source	source_detail	raw_title	generic_seed	price	currency	rating	rating_count	traffic	product_url	source_id	country	status	discovered_at	niche	organic_views	organic_views_all	videos_since_2026	video_url	momentum	seller_count	total_sold	organic_prev	trend	momentum_prev	checked_at	check_count
```
Google Sheets node мапить **за назвою** колонки, не за позицією — фізичний порядок у аркуші
може відрізнятись. Заповнюється лише TikTok Shop; для інших джерел частина порожня.
- `momentum` — код-вердикт (🔥 RISING / ⚠️ COOLING / 💀 SATURATED / ⚡ SPIKE / ❔ NO_DATA).
- `seller_count` / `total_sold` — з дедупу по `generic_seed` (конкуренція + розмір ринку).
- `organic_prev` / `trend` / `momentum_prev` / `check_count` / `checked_at` — моніторинг руху.
- **Використання:** фільтр `status=NEW AND momentum=🔥 RISING` → черга в Машину 2
  (DataForSEO → семантика → маржа → тест). RISING = «варто перевірити», не «точно бери».

### `Hashtag_Stats` (12 колонок; +product_id) — банк грошових хештегів
```
stat_id	source	hashtag	niche	videos_total	products_found	product_rate	avg_views	total_views	product_id	top_products	checked_at
```
З TikTok Shop: `videos_total`=згадки хештега у related_videos, `products_found`=1, `total_views`=organic_views товару,
`product_id`=source_id (склейка з інбоксом), `top_products`=generic_seed.
- **`avg_views`** = `organic_views / mentions` (рахується в `Explode Hashtags`).
- **`product_rate`** — порожнє, заповниться зворотною гілкою.
- STOP-фільтр хештегів (у `Parse Enrichment`): regex сміття + відсів тегів коротших за 3 літери (#de/#la/#el).
- 🔜 **Відкладено — чистка хештегів через `product_id`:** оскільки кожен рядок має `product_id`,
  пізніше можна почистити/зв'язати хештеги (видалити сирітські від старих товарів, згрупувати
  за товаром, перерахувати стату) — усе по ключу `product_id`. Робимо потім, не зараз.

### 🔜 ВІДКЛАДЕНО: зворотна гілка (хештег → нові товари) — 24.07.2026
Замикає цикл «вчимо хештеги → шукаємо нові товари по них». Потік:
```
Hashtag_Stats (топ за avg_views) → TikTok Hashtag Search (1 кредит/хештег)
   → рахуємо product_rate = відео з товаром / усі відео
   → товари → Product Details → дедуп проти inbox → нові сіди
   → оновлюємо product_rate у Hashtag_Stats
```
**Що потрібно перед побудовою:** перевірити, чи ScrapeCreators TikTok Hashtag Search віддає
**product/shop-anchor** у кожному `aweme_list[]` (без цього товари з хештег-відео не витягти —
гілка міряла б лише хайп хештега). Тест = 1 кредит: прогнати 1 хештег, глянути `aweme_list[0]`.
**Причина відкладення:** економія безкоштовних кредитів ScrapeCreators; будувати на платному плані.

### Робочі домовленості (формат відповідей)
- **Заголовки колонок — завжди через Tab** (одразу вставляються по колонках у Sheets).
- **Завжди повний код**, не сніпети.
- Ключі API — лише в n8n Credentials, ніколи в чат.
- Метод створення шапки в локалі користувача: `=SPLIT("a,b,c";",")` (роздільник аргументів `;`).

---

## MACHINE 2 → ФІНАЛ: MARGIN (5-й сигнал) + SHORTLIST — побудовано 25.07.2026

### 5-сигнальна модель рішення (фінал воронки)
`TikTok momentum × Google попит (5 країн) × болі/прогалини (семантика) × Meta реклама (вік) × **МАРЖА (собівартість постачальника)**`

Маржа — 5-й і вирішальний сигнал: товар може пройти 4 сигнали (попит+реклама), але **тонка маржа його вбиває** (напр. automatic litter box: 🟢 PROVEN, попит 90k/міс, але собівартість $91 при роздрібі $139 → маржа 1.52x → 🔴 СТОП-МАРЖА).

### Сценарій `03_DPRS_Prices & Margin` (status-active, AliExpress-гілка готова)
Ланцюг:
```
Manual → 13_Verdicts (read) → 12_Seed_Inbox (read, join роздрібної ціни по inbox_id)
  ├─ AliExpress: fetch_cat/aliexpress-products-scraper → Parse MarginAliExpress ─┐
  └─ 1688: Build CN Query → devcake/1688-com-products-scraper → Parse Margin 1688 │
           → Translate 1688 (OpenAI) → Apply Translation ──────────────────────┤
                                                                    → Merge (Append)
                                                                          ├─► Google Sheets 06_Margin (match margin_id)
                                                                          └─► Final Verdict → Google Sheets 13_Verdicts (match product_id)
```

**Логіка Parse Margin (універсальна, авто-визначення платформи):**
- `PLATFORM` авто-визначається по полях товару (`offer_id`/`price_cny`/`booked_count`/`member_id` → "1688", інакше "AliExpress"). Раніше руками — забувалось, тому авто.
- Надійність постачальника: `rating≥4.3 AND orders≥100` (де є рейтинг) АБО `repurchase≥15%` / verified/factory (1688, де рейтингу нема). Fallback-поля через `pick()` — читає fetch_cat + devcake ali + devcake 1688.
- **Floor «той самий товар»:** `floor = роздрібна / MAX_MARGIN(4)`. Постачальники дешевші за floor = аксесуар/1шт → відсіюються (`відсіяно_дешевих`). Виправляє фейкові маржі (напр. fishing lure з 57x на реальні 4x).
- Собівартість = найдешевший НАДІЙНИЙ ≥ floor. Топ-3 для резерву. `RATE` конвертує в USD (devcake дає `price_usd` → RATE=1).
- Вердикт: 🟢 GO (≥3x) · 🟡 ТІСНО (2-3x) · 🔴 СЛАБКО (<2x) · 🟠 ТІЛЬКИ ДЕШЕВІ (нема ≥floor, перевір).

**Final Verdict (v3):** бере МАКС маржу по товару серед платформ, **ігнорує 🟠-сміття** (не дає фейку 631x перебити чесну маржу). Комбінує з базовим вердиктом: `ТЕСТ + маржа<2 → 🔴 СТОП-МАРЖА`; `<3 → 🟡 ТЕСТ (тісна)`; `≥3 → 🟢 ТЕСТ`. Дозаписує в `13_Verdicts` (Append-or-Update по product_id).

**Актори (Apify):** AliExpress = `fetch_cat/aliexpress-products-scraper` (або `devcake/aliexpress-products-scraper` — ширше покриття). 1688 = `devcake/1688-com-products-scraper` (`price_usd` готовий, `composite_score` рейтинг, ехо `query`). CJ/GlobalSources — НЕ підходять (URL-only / MOQ-опт, без keyword-пошуку).

**1688 — китайський пошук (щоб не було сміття):** `Seed→CN` (OpenAI: англ seed → кит keyword) → `Build CN Query` → devcake/1688 (queries=keyword_cn) → Parse Margin 1688 (qmap зводить кит-`query` назад до англ seed для join роздрібної) → `Translate 1688` (OpenAI: кит назви → укр) → `Apply Translation`. **Статус: налаштовано, дозапуск завтра.**

### Аркуш `06_Margin` (універсальний, усі маркетплейси)
Один рядок = товар × платформа. `margin_id = MRG-{product_id}-{PCODE}` (ALI/1688) — унікальний, без колізій.
```
margin_id	product_id	товар	ніша	платформа	роздрібна	собівартість	маржа	маржа_вердикт	надійних_знайдено	відсіяно_дешевих	пошук_лінк	постачальник_1	лінк_1	постачальник_2	лінк_2	постачальник_3	лінк_3	created_at
```

### Сценарій `04_DPRS_Shortlist` (status-active) — відбір кандидатів + звіт
Окремий флоу (читає ВЖЕ оновлений `13_Verdicts`):
```
Manual → 13_Verdicts (read) → 12_Seed_Inbox (read, ВЕСЬ аркуш) → Build 07_Test_Products
  ├─► Google Sheets 07_Test_Products (match product_id)
  ├─► Build Report      → Telegram   (вітання+дата, 1 товар = 1 повідомлення)
  └─► Build Watch Report → Telegram   (⚡ SPIKE детально + 🧊 COOLING підсумок)
```
- **Кандидати на тест:** `фінальний_вердикт` містить 🟢 або 🟡 (🔴/ПОДИВИТИСЬ/ПРОПУСТИТИ — ні). Сорт: 🟢 спершу, далі по маржі.
- **Логіка momentum:** 🔥 RISING → тест (через пайплайн); ⚡ SPIKE → нагляд (сплеск від 1 ролика); ⚠️ COOLING → нагляд (підсумок); 💀 SATURATED → пропуск; → FLAT → низький пріоритет.
- `Build 07_Test_Products` читає вердикти І інбокс **по імені** (`$("13_Verdicts")`, `$("12_Seed_Inbox")`) — порядок нод не ламає $input. Join: `product_id (вердикт) = inbox_id (інбокс)`.
- Дотягує з інбоксу: `тік_ток_товар` (product_url = продукт конкурента), `тік_ток_відео` (video_url), `тік_ток_продано` (total_sold).
- Будує лінки: `реклама_бібліотека` (Meta Ad Library по товару — показує рекламу конкурентів), `пошук_ali`, `пошук_1688`.

**Звіт Telegram (Build Report):** parse_mode HTML, 1 item = 1 повідомлення. Вступ (🎉 Вітаю + дата + к-сть). По товару: ВЕЛИКА ЖИРНА назва, вердикт, маржа ($cost→$retail), попит, реклама 30+дн, постачальник (лінк), блок «Конкурент і джерела» (🏪 продукт конкурента · 🎬 відео · 📣 реклама конкурентів · 🔎 AliExpress/1688), кут (прогалини) + болі.
- **Критично:** усі URL у href обгортати `href(u)=u.replace(/&/g,"&amp;")` — інакше Telegram HTML ламає багатопараметрові лінки (Facebook Ad Library з 5×`&` не відкривався).

### Аркуш `07_Test_Products`
```
shortlist_id	product_id	товар	ніша	фінальний_вердикт	маржа	собівартість	роздрібна	постачальник_топ	пошук_ali	пошук_1688	тік_ток_товар	тік_ток_відео	тік_ток_продано	реклама_бібліотека	реклам_30дн	найдовше_дн	топ_обсяг	прогалини	болі	доданий
```

### Назви нод (реєстр, 06+07)
`Parse MarginAliExpress` (AliExpress), `Parse Margin 1688` (1688), `Merge`, `Final Verdict`, `update 13_Verdicts`, `Seed→CN`, `Build CN Query`, `Translate 1688`, `Apply Translation`, `Build 07_Test_Products`, `Build Report`, `Build Watch Report`.

### 🔜 ВІДКЛАДЕНО
1. **1688-гілка** — дозапуск (кит-пошук + переклад готові, лишилось прогнати й влити в Merge).
2. **Дублікати в `12_Seed_Inbox`** (×6 на товар) — баг запису Machine 1: `Build Seed Inbox → Google Sheets` робить Append замість Update. Полагодити match по `inbox_id`. Тимчасово watch-звіт дедуплить у коді.
3. Числова scoring-модель (стара `Decision`-таба) — на пенсії, замінена вердиктною + Shortlist.

---

## МУЛЬТИ-ДЖЕРЕЛЬНИЙ ІНБОКС + `05_DPRS_Trends Digest` — побудовано 27.07.2026

### Архітектурний принцип: Machine 2 джерело-агностична
`12_Seed_Inbox` = єдиний стик (junction). Усі джерела відкриття пишуть стандартний сід туди, Machine 2 читає звідти — байдуже TikTok / Trends / Instagram / YouTube.
```
TikTok Shop   ─┐
Google Trends ─┤
Instagram     ─┼─► 12_Seed_Inbox (status=NEW) ─► Machine 2 (валідація) ─► вердикт
YouTube Shorts─┘
```
- **Кожне джерело саме пре-фільтрує** і пише `status=NEW` тільки для вартісних (TikTok: RISING; SPIKE/COOLING → WATCH; Trends: товарний потенціал; Insta/YT: віральні з товаром).
- **Стандартний сід (мінімум для Machine 2):** `inbox_id · generic_seed · niche · source · status · country · discovered_at`. Решта (momentum/views/hashtags) — джерело-специфічна начинка, Machine 2 бере лише `generic_seed`.
- **`inbox_id = SIG-djb2(generic_seed)`** — детермінований → крос-джерельний дедуп (TikTok і Trends знайшли «power bank» → один рядок). Append-or-Update по `inbox_id`.
- **Оновлення вже знайденого — автоматичне:** та сама формула id + Append-or-Update оновлює наявний рядок; оновлюються ТІЛЬКИ колонки, що нода віддає (решта не чіпається).

### Сценарій `05_DPRS_Trends Digest` (status-active) — Google Trends як 2-е джерело
```
Schedule Trigger (щодня 08:00 America/New_York)
  → Countries (5: US/GB/CA/AU/NZ) → Trending Now (SerpApi google_trends_trending_now, Run Once Each Item)
  → Build Digest Input (топ-10 трендів × країна → текст)
     ├─► OpenAI (дайджест-текст) → Extract Digest (md→TG HTML, нарізка 3800) → Telegram   [людині]
     └─► OpenAI Seeds (JSON) → Parse Seeds → Google Shopping (SerpApi, ціна) → Build Inbox Seed (SOURCE=google_trends) → Google Sheets 12_Seed_Inbox   [у Machine 2]
```
- **Дайджест-гілка:** 7 напрямків (політика/спорт/культура/фінанси/здоров'я/тех/інше) + 🔁 спільні тренди (2+ країн) + **🛒 Товарний потенціал** (фільтрує новини, шукає товари/ніші) + 💡 як використати. Заголовок «📊 GOOGLE TRENDS NOW» + дата.
- **Сід-гілка (з ціною):** `OpenAI Seeds` (JSON, до 8 товарів `{seed, niche(англ фікс-список), country, reason}`, ігнорує новини) → `Parse Seeds` (розбиває масив на items + мапить `location` повною назвою країни для SerpApi) → **`Google Shopping`** (SerpApi `google_shopping`, `q=generic_seed`, `location=назва`, Run Once Each Item) → `Build Inbox Seed`. Google Shopping ЗАКРИВАЄ дірку: trend-сіди не мають роздрібної ціни (не з TikTok Shop), а Shopping дає `price` (медіана `extracted_price`), `rating` (сер.), `rating_count` (сума reviews), `seller_count` (унік. sources), `raw_title` (реальна назва), `product_url` (`encodeURI` — інакше пробіли ламають лінк). Тепер trend-сід повноцінний → margin-флоу рахує маржу так само, як для TikTok. Приклад: emergency radio $40.90 (ausalert), heated blanket $70.99 (NZ морози), pill organizer box $11.99 (dementia).
- **Поля інбоксу:** Build Inbox Seed віддає всі 28 колонок — Trends+Shopping заповнюють (inbox_id, niche, generic_seed, status=NEW, source, price, currency, rating, rating_count, seller_count, source_detail=тренд, raw_title, product_url, country, discovered_at); TikTok-only (organic_views, video_url, momentum, trend, total_sold…) — порожні (Machine 2 їх не читає); checked_at/check_count — заповнить Level-2 моніторинг пізніше.
- **SerpApi поля:** `trending_searches[]` → `query`, `search_volume`, `categories[].name`. Гео через `geo` param.
- **Telegram HTML:** усі URL у href обгортати `&`→`&amp;` (інакше багатопараметрові лінки, напр. FB Ad Library, не відкриваються).

### Сценарій `06_DPRS_Trends Related` (status-wip) — Google Trends related як 3-є джерело
Окремий воркфлоу. Розкрутка **широких ніш** через Google Trends RELATED_QUERIES (rising) → зростаючі товарні запити.
```
Manual → Niches → Trends Related → Parse Related → Filter Products → Parse Seeds → Google Shopping → Build Inbox Seed → 12_Seed_Inbox
```
- **`Niches`** — 8 широких термінів × країни (`car accessories`, `pet products`, `kitchen gadgets`…). Multi-country: niche × geo (US/GB/CA/AU/NZ) = 40 запитів/прогін (SerpApi квота!). Можна звузити geos.
- **`Trends Related`** — SerpApi `engine=google_trends`, `data_type=RELATED_QUERIES`, `q=term`, `geo`. Вертає `related_queries.rising[]` `{query, value(Breakout/+%), extracted_value}`.
- **`Parse Related`** — збирає rising по «ніша — країна» в текст (заголовок блоку тримає країну).
- **`Filter Products`** — OpenAI (JSON Schema strict, потрібен `additionalProperties:false` у КОЖНОМУ об'єкті!) чистить шум: прибирає бренди/моделі (dyson, chery arrizo), не-товари (ai agents, k-pop, news), модифікатори (best/near me) → generic-товари. Country бере з заголовка блоку.
- далі **та сама price-частина**, що в Trends Digest (Parse Seeds → Google Shopping → Build Inbox Seed), лише `source=google_trends_related`.
- **Урок:** RELATED_QUERIES по ШИРОКИХ нішах працює (rising є), по ВУЗЬКИХ товарах — порожньо. Тому related годуємо нішами, а не готовими товарами. Дані шумні → OpenAI-фільтр обов'язковий.
- **Розклад:** 1-2×/тиждень (related рухається повільніше за новини).

### Сценарій `07_DPRS_Instagram discovery` (status-active) — Instagram як 4-е джерело
Скрапер — **ScrapeCreators** (не Apify, бо вже є кредити). Механізм: віральні Reels по продуктових хештегах → AI витягує товар → Shopping-ціна → інбокс.
```
Manual → Hashtags → Instagram Search → Parse Reels → Filter Products → Parse Seeds → Google Shopping → Build Inbox Seed → 12_Seed_Inbox
```
- **`Hashtags`** — 1 хештег = 1 item (`tiktokmademebuyit`, `amazonfinds`, `gadgets`, `coolgadgets`, `kitchengadgets`, `cargadgets`, `petgadgets`, `homegadgets`).
- **`Instagram Search`** — HTTP GET `https://api.scrapecreators.com/v1/instagram/search/hashtag`, header `x-api-key`, query `hashtag` (**БЕЗ `#` — # ламає URL як fragment!**), `media_type=all`, `date_posted=last-week`. **Run Once Each Item + Settings→On Error: Continue (regular output)** (порожні хештеги 404-ять «No posts found» → пропускаємо). `date_posted=last-day` часто порожній (Google-індекс лагає) — тому `last-week` + розклад пн+чт.
- **`Parse Reels`** — фільтр віральних (`video_play_count ≥ 100k` АБО `like_count ≥ 10k`), дедуп по shortcode, віддає `reels_input` (текст для AI) + `reels[]` (структура для matchReel).
- **`Filter Products`** — OpenAI (JSON Schema strict) витягує generic-товари з підписів.
- **price-хвіст** — Parse Seeds → Google Shopping → Build Inbox Seed (`source=instagram`).
- **Enrichment:** Build Inbox Seed через `matchReel` (збіг seed↔caption по словах) заповнює `organic_views` (перегляди Reels) + `video_url` (лінк на Reels) — IG-сід стає багатим як TikTok (ціна + рейтинг + перегляди + лінк).
- **Урок:** Instagram флакі (той самий хештег дає різну к-сть по прогонах); дедуп по inbox_id це прощає.

### Сценарій `09_DPRS_YouTube Shorts discovery` (status-active) — 5-е джерело
Скрапер — **офіційний YouTube Data API v3** (Google-акаунт, не ScrapeCreators; безкоштовно в межах квоти).
```
Manual → Keywords → YouTube Search → Parse Shorts → Filter Products → Parse Seeds → Google Shopping → Build Inbox Seed (source=youtube_shorts) → 12_Seed_Inbox
```
- **`Keywords`** — keyword × країна (8 запитів × 5 країн = 40): `tiktok made me buy it`, `amazon must haves`, `cool gadgets`, `kitchen gadgets`, `car gadgets`, `pet gadgets`, `amazon finds`, `tiktok finds`.
- **`YouTube Search`** — GET `https://www.googleapis.com/youtube/v3/search`, params `part=snippet, q, type=video, videoDuration=short, order=viewCount, regionCode={{region}}, relevanceLanguage=en, maxResults=25, key`. ⚠️ **`regionCode` обов'язково** (без нього дефолт може бути DE!). **Квота: search=100 юнітів/запит × 40 = 4000/прогін** (денна 10 000 → макс ~2 прогони/день). `search.list` НЕ віддає переглядів (тому organic_views порожній; video_url — з matchShort по назві Short).
- **`Parse Shorts`** — тримає країну в блоці `### US`, віддає `shorts_input` (текст) + `shorts[]` (для matchShort).
- **`Filter Products`** — OpenAI (JSON Schema strict), country з заголовка блоку.
- **price-хвіст** — Parse Seeds → Google Shopping → Build Inbox Seed (`source=youtube_shorts`), парент по q+індекс (fallback), matchShort → `video_url`.
- Мультикантрі: сіди з US/GB/CA/AU/NZ, `country` тече в Google Shopping location.

### 🎯 СИСТЕМА: 5 ДЖЕРЕЛ ВІДКРИТТЯ (станом на 27.07.2026)
```
01 TikTok Shop  ─┐
05 Trends Digest ─┤
06 Trends Related─┼─► 12_Seed_Inbox (status=NEW, source=...) ─► Machine 2 (валідація)
07 Instagram    ─┤        inbox_id=SIG-djb2(seed) = крос-джерельний дедуп
09 YouTube Shorts┘
```
Спільний патерн джерела: **[скрапер] → Parse → Filter Products (OpenAI) → Parse Seeds → Google Shopping (ціна) → Build Inbox Seed (свій source) → інбокс**. Facebook (08) пропущено (Ad Library у M2, Marketplace слабкий). Instagram/YouTube — matchReel/matchShort заповнюють organic_views/video_url.

### 🔜 ВІДКЛАДЕНО (фіксимо коли дійдемо)
1. **Machine 2 вхід** — замінити `Filter RISING` на `Filter Entry` (Code): `status===NEW AND (source===tiktok_shop ? momentum~RISING : true)`. Тобто TikTok — лише RISING, інші джерела — всі NEW. (SPIKE у TikTok щодня → лишається WATCH, не валідується.)
2. **Захист статусу при перезнаходженні** — Build Inbox Seed пише `status=NEW`, що скидає вже `VALIDATED` товари назад у валідацію (зайві витрати). Фікс: при перезнаходженні не віддавати `status` (не чіпати колонку) АБО перевіряти наявний статус. Для першого запуску (порожня таблиця) — неактуально.
3. **Instagram / YouTube Shorts** — додати як джерела за тим самим патерном (пре-фільтр → Build Inbox Seed зі своїм SOURCE → інбокс).
4. **Дублікати в `12_Seed_Inbox`** (×6 на товар з TikTok) — баг Append→Update у Machine 1, match по `inbox_id`.

---

## 🏁 ПОВНА ВОРОНКА END-TO-END (31.07.2026) — 4 сцени + статус-цикл

Система доведена від інбоксу до готового шортлісту. Перший товар пройшов усі етапи: **jump starter → 🟡 ТЕСТ (тісна) (1688 2.57x) → 07_Test_Products**.

### Архітектура (4 окремі сценарії + Машина 1)
```
Машина 1 (5 джерел) → 12_Seed_Inbox (статуси при записі)
Сцена 1 (валідація)  → Idea Verdict → 13_Verdicts        (status NEW→VALIDATED)
Сцена 2 (маржа)      → CJ+Ali+1688 → 06_Margin           (status VALIDATED→MARGIN)
Сцена 3 (фінал)      → Final Verdict → 13_Verdicts        (status MARGIN→CHECKED)
Сцена 4 (шортліст)   → Build Shortlist → 07_Test_Products (переможці 🟢/🟡)
```
Кожна сцена — окремий n8n-сценарій, розклад `*/5`–`*/15`. Наскрізний ключ: **`product_id` (13_Verdicts) = `inbox_id` (інбокс/маржа) = `SIG-...`**. `verdict_id = VRD-{product_id}`.

### Статус-цикл (дедуп без зайвих читань)
```
NEW → VALIDATED → MARGIN → CHECKED     (+ WATCH = не годний)
```
- **Статуси проставляються ПРИ ЗАПИСІ в інбокс** (Машина 1), функція `statusFor(source, momentum, price)` у Build Inbox Seed кожного з 5 джерел:
  - `price < 15` → `WATCH` (усі)
  - TikTok: ще й потрібен `RISING` (інакше WATCH)
  - інші джерела з ціною ≥15 → `NEW`
  - (TikTok — у ноді `Merge History`; решта — у Build Inbox Seed; `VALIDATION`/`VALIDATED` не скидаються)
- Кожна сцена бере свій вхідний статус і **просуває** його → 5-хв цикл не палить API на повторах.

### Сцена 1 (валідація) — база вердикту (4-сигнальна)
`Filter RISING` спрощено до **`status===NEW`** (momentum/ціна вже в статусі; прибрано стару перевірку RISING, бо вона відсікала не-TikTok джерела). Далі: Google search volume (DataForSEO) + FB Ad Library (ScrapeCreators) + семантика → **Idea Verdict**: `ПРОПУСТИТИ / ПОДИВИТИСЬ / ТЕСТ` (соц×пошук×болі×реклама). Idea Verdict тепер віддає ще `inbox_id`, `generic_seed`, `price`. У кінці — Update інбоксу `status=VALIDATED`. Реклама-агрегат (`реклама`, `реклам_30дн`, `найдовше_дн`) живе в 13_Verdicts (деталі не збираємо — досить агрегату для рішення).

### Сцена 2 (маржа) — 3 платформи, вхід з 13_Verdicts
`Filter Entry` бере з **`$('13_Verdicts')`** (не $input — інакше читає попередню ноду!): `вердикт===ТЕСТ` + ціна>15 (з інбоксу по id) + дедуп. Розгалуження на 3 гілки від Filter Entry:
- **CJ** (API, безкоштовний): auth → search → details → inventory → reviews → freightCalculate → Parse CJ. Реальна доставка, склади (🇺🇸/🇨🇳), прапорці (батарея/сток/відгуки).
- **AliExpress** (Apify `fetch_cat/aliexpress`): Parse Ali — floor + гейт надійності (рейтинг≥4.5, продажі≥30), `priceCurrentMin`, `ratingValue`, `soldCount`, строк з `tags`.
- **1688** (Apify devcake, китайський запит + переклад): Parse 1688 — `price_usd` вже конвертована, надійність за `composite_score`/продажами/бейджами (💪power/🏭factory/✅qualified), MOQ.
- Усі 3 → **одна нода `06_Margin`** (Append/Update, **match=`margin_id`=`ключ`** — унікальний `SIG_платформа`; НЕ `product_id`, бо він спільний → перезаписувало!). У кінці — Update інбоксу `status=MARGIN`.

### Доставка (остаточне рішення)
Скрап Ali/1688-доставки **неможливий** (Ali reCAPTCHA навіть з Firecrawl stealth; 1688 віддає лише внутрішньокитайську ¥). Тому:
- **CJ** — реальна (freightCalculate)
- **AliExpress** — **$0** (Choice free shipping, підтверджено вручну + DSers)
- **1688** — CJ-оцінка (агентська доставка ≈ CJ, бо залежить від ваги, не платформи)
- Рахується у Final Verdict: `own>0?own : (Ali?0 : CJ-оцінка)`.

### Сцена 3 (фінал) — база + маржа (5-й сигнал)
Окремий сценарій: `06_Margin (Read) → 13_Verdicts (Read) → Final Verdict → 13_Verdicts Write`. Групує 06_Margin по **`product_id`** (в 06_Margin немає inbox_id!), обирає найкращу маржу серед платформ (ігнорує 🟠), накладає на базовий вердикт:
- `ПРОПУСТИТИ` → 🔴 SKIP; `ТЕСТ + маржа≥3` → 🟢 ТЕСТУВАТИ; `≥2` → 🟡 ТЕСТ (тісна); `<2` → 🔴 СТОП-МАРЖА.
- Пише **тільки маржа-колонки** (`собівартість, маржа, маржа_платформа, маржа_вердикт, постачальник_топ, фінальний_вердикт`) у **той самий `13_Verdicts`** (match=`verdict_id`, Map Auto) — Idea Verdict не чіпає (кожен пише свої поля).

### Сцена 4 (шортліст) — переможці
`Build Shortlist` читає **`$('13_Verdicts Write')`** (свіжий фінал; має стояти ПІСЛЯ Write у ланцюгу!) + базу з `13_Verdicts` + роздрібну/cj_лінк з `06_Margin`. Фільтр по ТЕКСТУ `/ТЕСТ|ПОГРАНИЧНО/i` (не по емодзі — кодпойнти можуть не збігтись). Пише в `07_Test_Products` з лінками на всі платформи (`пошук_ali`, `пошук_1688`, `пошук_cj`, `cj_лінк` — прямий товар CJ).

### Уроки цієї сесії
- **Match-колонка Google Sheets:** для 3 платформ на товар match має бути унікальний per-row (`ключ`/`margin_id`), НЕ спільний `product_id` (перезаписувало в 1 рядок).
- **`$input` vs `$('Node')`:** Filter Entry/Build Shortlist читали попередню ноду замість потрібної → завжди читати цільову ноду по імені.
- **Stale read:** нода Read віддає стан аркуша на момент СВОГО виконання; щоб бачити свіжий запис — читати write-ноду або окремий сценарій.
- **Українські vs англійські ключі:** після переходу входу на 13_Verdicts поле стало `ніша` (не `niche`) → Parse Ali/1688 фіксили `parent.ніша || parent.niche`.
- **DSers** — фулфілмент Ali/CJ вручну (без API); система дає лінк+вердикт, DSers імпортує переможця.

### Відкладено
- Дедуп по 06_Margin у Сцені 2 (зараз статусний дедуп через `status=MARGIN`).
- Розклади `*/5`–`*/15` на 4 сцени + зсув Сцени 2/3/4.
- Опційно: деталі реклами в `09_Ads` (swipe file креативів) — лише коли дійде до створення оголошень.

## 🏪 ГІЛКА КОНКУРЕНТІВ + РАПОРТ (Scene 4, 03.08.2026)

### Мета
До Telegram-звіту й аркуша додати конкурентів: **хто продає, ціна від-до, скільки продавців, рейтинг, відгуки, продажі** + бізнес-інсайт по ціні. Запит іде ТІЛЬКИ на переможцях (1 товар/прогін) — економія API.

### Ланцюг Scene 4 (фінал)
```
Trigger → 13_Verdicts Write → Seed Inbox → Prep Winners → SerpApi Shopping
  → Get Product Id → Immersive Product (HTTP) → DataForSEO Amazon → Parse Competitors ─┬→ Build Report → Telegram
                                                                                        └→ Competitors Rows → 05_Competitors
                                                                                        └→ Report Row → 14_Report (опц., плоский підсумок)
```

### Вузли
- **Prep Winners** (Code) — фільтрує переможців (`/ТЕСТ|ПОГРАНИЧНО/`), додає `seed`(=`товар` з 13_Verdicts), `location:'United States'`, `gl/hl`, і несе ВСІ поля звіту (SerpApi затирає json!). Інбокс-поля (`price/source/video_url/source_detail`) тягне з `Seed Inbox` — **нода Seed Inbox має стояти ПЕРЕД Prep Winners** (інакше `$('Seed Inbox')` порожній).
- **SerpApi Shopping** (`Search Google Shopping`): `q={{ $json.seed }}`, `location={{ $json.location }}` (повна назва країни!). `shopping_results[]`: `source`(продавець), `extracted_price`, `rating`, `reviews`, `product_id`(=catalogid), `immersive_product_page_token`, `serpapi_immersive_product_api`. **Amazon у Google Shopping НЕ показується** (Amazon пішов з Google Shopping ~2015).
- **Get Product Id** (Code) — бере `immersive_product_page_token` топ-результату + несе дані далі.
- **Immersive Product** (HTTP Request, бо в n8n SerpApi-ноді немає immersive-операції): `GET serpapi.com/search.json`, `engine=google_immersive_product`, `page_token={{ $json.imm_token }}`, Auth=Predefined SerpApi. **Замінює мертвий `google_product`** («The Google Product service is no longer offered by Google»). Віддає `product_results` (специфікації/фічі всередині; окремих `reviews_results`/`specifications` НЕМАЄ — тексти відгуків з immersive недоступні).
- **DataForSEO Amazon** (`Amazon → Get products advanced`, нативний вузол): `keyword={{ $('Get Product Id').first().json.seed }}` (по імені ноди, бо HTTP/Immersive затерли json), `location_name=United States`, **`language_name=English (United States)`** (Amazon хоче ринок у дужках, НЕ `English`/`en`!). Віддає `tasks[0].result[0].items[]`: `title`, `price_from`, `data_asin`, `rating.value`, `rating.votes_count`, `bought_past_month`(продажі), `is_best_seller`, `is_amazon_choice`.
- **Parse Competitors** (Code) — Google Shopping → `comp_list` [{s,p,big}] (BIGBOX-регекс відрізняє 🛍 незалежних/Shopify від великих мереж); Amazon → діапазон `amz_min/max/med` + `amz_best`(бестселер) + `amz_choice`.
- **Build Report** (Code) — структурований рапорт секціями: 💰 економіка + порада по ціні, 📈 попит+реклама (лінк FB Ad Library), 🏭 постачальники (назва→лінк→ціна, 🥇🥈🥉), 🏪 магазини + 🅰️ Amazon, 🕳 кут / 💬 болі / #️⃣ хештеги, 🔗 посилання, ✅ **ЩО РОБИТИ** (дія по вердикту + підняти ціну + замовити семпл + запустити рекламу).
  - **Фото товару зверху**: `img` (Amazon `image_url` топ → Google `thumbnail`) вставляється як невидиме посилання `<a href="img">​</a>` на початку тексту + Telegram **Disable WebPage Preview = OFF** → фото рендериться прев'ю над рапортом (без обмеження 1024 симв. підпису Send Photo).
  - **Конкуренти стовпчиком, назва = лінк на товар**: `comp_list` несе `link` (Google `product_link`); Amazon бестселер/Choice — лінк `amazon.com/dp/{asin}`. Кожна назва магазину/товару клікабельна.
  - **Рекомендована ціна** = `round(amz_med*0.72)` (нижче Amazon's Choice) з перерахунком маржі — виводиться в 💡 та в блок «ЩО РОБИТИ».

### Аркуш `05_Competitors` (детальна база конкурентів)
Вузол **Competitors Rows** (Code, гілка від Parse Competitors) — **по рядку на кожен товар конкурента** (Google Shopping топ-20 + Amazon топ-25 за продажами). Колонки: `row_id, product_id, seed, джерело, продавець, назва, ціна, рейтинг, відгуки, продажі, лінк, asin, дата`. `row_id`=`{product_id}_{G|A}_{djb2/asin}` → повторний прогін оновлює, не дублює. **Лінк = формула `=HYPERLINK("url";"підпис")`** (клікабельний!); Amazon-url чистий `amazon.com/dp/{asin}`. ⚠️ Google Sheets вузол має бути в режимі **USER_ENTERED**, інакше формула стане текстом. Роздільник HYPERLINK `;` або `,` залежно від локалі Sheets.

### Бізнес-інсайт (навіщо конкуренти)
На jump starter: собівартість $16.76, роздрібна в системі $42.99, а **медіана ринку Amazon $89.99** (бестселер NOCO GB40 $99.95). Тобто ціна занижена → підняти до ~$65 (нижче Amazon's Choice $69.97) → маржа 2.57x → **3.9x**, вердикт 🟡→🟢. Рекомендована ціна = `round(amz_med*0.72)` виводиться у звіт і в `рекомендована_ціна`.

### Уроки
- **Amazon дістається лише окремо** (DataForSEO/SerpApi Amazon), не з Google Shopping.
- **SerpApi Google Product мертвий** → `google_immersive_product` (через HTTP, бо n8n-нода не має операції).
- **DataForSEO мова для Amazon** = `English (United States)` (поле `_name` = повна назва + ринок), для Google = `English`/`en`.
- **Клікабельний лінк у Sheets** = `=HYPERLINK(...)` + USER_ENTERED; або чистий encoded-URL без пробілів.
- **SerpApi/HTTP затирають json** → далі читати попередні дані по імені ноди (`$('Get Product Id')`), не `$json`.
- **DataForSEO дешевший ~10-20×** за SerpApi, але task-based/складніший; при 1 товарі/прогін різниця копійчана → SerpApi для простоти, DataForSEO де нативно (Amazon).

---

## ОНОВЛЕННЯ 06.08.2026 — ГЕЙТ, СТАТУС-ЧЕРГА, МАРЖА ПО ФОТО

### Новий воркфлоу `10_DPRS_Product Gate` (`M2-validation · fn-gate · status-active`)
Фільтр-черга **МІЖ Машиною 1 і Машиною 2**. Розклад `0 8,14,20 * * *` (3×/день).
```
Schedule → 12_Seed_Inbox (Read) → Gate M2 (Code) → 12_Seed_Inbox (Update: status/gate_reason/gate_priority)
```
**Принцип:** черга живе в колонці `status` інбоксу — окрема таба НЕ потрібна.
- `NEW → (Гейт) → QUEUED / WATCH / REJECTED_CATEGORY / DUPLICATE`
- `QUEUED → (Машина 2) → VALIDATED → (Маржа) → MARGIN`
- Додано колонки в інбокс: **`gate_reason`, `gate_priority`**.

**Логіка Gate M2:**
- `PROTECT = [QUEUED,VALIDATED,MARGIN,FINAL,SENT]` — «вже в роботі», гейт НЕ чіпає (SKIP). Решту перебирає (працює і як разовий бекфіл, і на розкладі).
- REJECT: регульоване/небезпечне (`REGULATED`: car seat, baby monitor, eclipse glasses, salmon oil, insect repellent, crypto, laptop, smartphone…), габарит (`OVERSIZED`: dumbbell, kitchen sink, espresso machine, mattress, hose reel…), рейтинг<3.5, momentum SATURATED/COOLING, поганий сід.
- WATCH: ціна<$12 (тонка маржа), momentum SPIKE, бренд у назві. **Стелі ціни НЕМА** (свідоме рішення — категорії ловлять дороге сміття без цінового обмеження).
- `gate_priority`: TikTok +100, RISING +60/SPIKE +25/NEW +15, log(sold), rating; бренд −20.
- Дедуп по `generic_seed`: виводить ВСІ рядки (273=273), програшним дублям → `status=DUPLICATE` (не випадають, не зависають). Downstream-інстанс (VALIDATED тощо) перемагає новий → новий стає DUPLICATE (не ре-чергується).

**5 джерел БІЛЬШЕ НЕ пишуть status.** У кожній Sheets-write ноді джерел (TikTok/YouTube/IG/Trends Related/Trends) прибрано `status` з мапінгу → нові сіди лягають з ПОРОЖНІМ статусом (гейт заповнює), повторно знайдені — status не перезаписується (не скидає VALIDATED). Правило `<$20→WATCH` перенесено в гейт (`PRICE_THIN=12`).

### Машина 2 (`02_DPRS_Semantic Core validation`) — черга + фото
Реальний ланцюг (робочий):
```
Schedule → 12_Seed_Inbox(Read) → Pick Next 1 → Build Country Batches → Get live google search volume (DataForSEO)
  → Parse Validation → Filter STRONG →
      ├─ Get keyword suggestions (DataForSEO Labs) → Parse Semantic Core → 08_Semantic_Core
      └─ Search for ads (facebookAdLibrary) → Parse Meta Ads →
   Merge → Idea Verdict → 12_Seed_Inbox(status=VALIDATED) + 13_Verdicts (status=VERDICT, вердикт=ТЕСТ/…)
```
- **`Pick Next 1`** (Code): бере 1 товар `status=QUEUED`, сорт за `gate_priority` desc. Порожня черга → `return []` (Always Output Data=OFF).
- **Перший вердикт** (`Idea Verdict`): комбо попиту (Google volume) + реклами (FB Ad Library 30+днів). Приклад jump starter: 🟢 PROVEN, 43 реклами 30+дн, найдовша 788 днів → **вердикт ТЕСТ**.
- **Гілка ФОТО (паралельна від `Pick Next 1`):** `Need Amazon Image?` (Code: пропускає далі лише якщо фото `gstatic`/`serpapi`/порожнє — TikTok з чистим `ttcdn` стопиться) → **DataForSEO Merchant Amazon** (keyword=`generic_seed`) → `Set Amazon Image` (бере `items[0].image_url` = чистий `m.media-amazon`) → 12_Seed_Inbox Update `image_url`. TikTok через Amazon НЕ ганяємо (має своє фото).
- **Фото по джерелах:** TikTok=своє (`ttcdn`), keyword(YouTube/IG/Trends)=з Amazon (`m.media-amazon`). Google Shopping `gstatic`-мініатюра для devcake НЕ годиться (проксі). DataForSEO Merchant дешевший за SerpApi Amazon → його й беремо (SerpApi запасний).

### Маржа по фото (`03_DPRS_Prices & Margin`) — devcake Scraper by Image
```
Schedule → 12_Seed_Inbox(Read) → Pick for Margin → [AliExpress: devcake фото] ─┐
                                                    [1688: Seed→CN keyword]    ├─ Merge → Final Verdict → 13_Verdicts + status=MARGIN
                                                    [CJ: keyword]              ┘        + 06_Margin (рядок/платформа)
```
- **`Pick for Margin`** (Code): бере 1 рядок з **13_Verdicts** де вердикт `ТЕСТ/ПОГРАНИЧНО/🟢/🟡` І `маржа` порожня І є `image_url`. «Порожня маржа» = автоматично «по одному». Замінює стару `Filter Entry`.
- **Стратегія сорсингу (перевірено на jump starter):**
  - ✅ **AliExpress — ПО ФОТО** (devcake `provider=aliexpress`). Image-match точний. Дав $19.30 ⭐4.7 984зам → 2.23x 🟡.
  - ✅ **1688 — кит. KEYWORD** (гілка `Seed→CN` OpenAI → devcake 1688 queries → переклад). Дав $11.48 → 3.74x 🟢 (АЛЕ гурт CN, доставка не врахована, потрібен агент).
  - ⚠️ **CJdropshipping — KEYWORD** (image-API немає; keyword слабкий → обов'язковий фільтр релевантності).
  - ❌ **Alibaba — ПРИБРАНО** з фото: image-match дав сміття (лампу для нігтів на jump starter).
  - **1688/Alibaba по фото НЕ працюють** — image-match промахується (ваги/лампа), + китайські назви не валідуються англ. ключами.
- **devcake output (ключові поля):** `provider`, `price_min`/`price_max` (НЕ `price`!), `currency_code`, `product_url` (лінк), `title`, `image_url`. Для 1688/alibaba додатково є `rating`, `sold_count`, `years_as_gold_supplier`, `factory_inspected`. AliExpress рейтинг/продажі = **null** (image-search їх не дає).
- **`Parse Margin (Image)`:**
  - Фільтр релевантності: назва містить ключове слово сіда (`jump`/`starter`, len≥4). Нема релевантних → `🟠 нема релевантних (перевір вручну)`, маржу НЕ рахуємо (щоб сміття не давало фейкових 🔴). 1688 (кит. назви) авто-релевантність не проходить → «перевір вручну».
  - Надійність (де є дані): `рейтинг≥4.3 AND замовлень≥100` або gold/factory. AliExpress без рейтингу → floor-only.
  - `floor = роздрібна/4` (відсіює аксесуари/1шт). Собівартість = найдешевший надійний ≥ floor. Топ-3 резерв. Валюта→USD (`FX`, 1688=CNY×0.14).
  - Рядок на платформу: `margin_id = MRG-{product_id}-{ALI|1688|BABA}` (не перезаписують один одного).
- **`Final Verdict`:** найкраща РЕЛЕВАНТНА маржа серед платформ (ігнорує 🟠/⚪). **`SHIP_BUFFER` для CN** (1688/alibaba +$4 до собівартості) — щоб гурт без доставки чесно не перебивав all-in AliExpress. Комбо: маржа≥3→🟢 ТЕСТ, 2-3→🟡, <2→🔴 СТОП-МАРЖА. Пише в `13_Verdicts` (match `verdict_id`) + `12_Seed_Inbox` status=MARGIN.

### Уроки цього оновлення
- **Черга = статус, не нова таба.** Гейт наповнює (QUEUED), Машина 2 бере по 1 (LIMIT 1, `маржа`/`status` як гейт «зроблено»).
- **Гейт = єдиний власник статусу.** Джерела статус не пишуть (інакше скидають прогрес).
- **Фото по фото працює лише на AliExpress** (+ TikTok має своє). 1688/Alibaba image-match ненадійний → keyword.
- **1688 дешевший ~1.7×, але без доставки** — потрібен `SHIP_BUFFER` для чесного порівняння + агент/семпл.
- **Фільтр релевантності обов'язковий** для keyword-джерел (CJ/1688) — назва мусить містити ключ товару.

---

## CJ-ГІЛКА МАРЖІ (детально) — 06.08.2026

### Ланцюг (усі GET/POST через CJ API, ліміт QPS=1/сек!)
```
CJ Search → Parse CJ (=Select top-3) → CJ Details → CJ Inventory → CJ Reviews → CJ Freight → Parse CJ Margin → 3 рядки
```
**Тротлінг обов'язковий:** CJ = **1 запит/секунду**. Три items одночасно → `Too Many Requests, QPS limit is 1 time/1second`. Рішення: `Loop Over Items` (Batch=1) + `Wait 1.2с` між викликами, АБО в кожній HTTP-ноді `Options → Batching = 1 item / 1200ms`.

### Схема: 1 рядок = 1 постачальник (не колонки!)
По кожній платформі — **3 товари = 3 окремі рядки**. `margin_id = MRG-{product_id}-{ПЛАТФОРМА}-{ранг}`. Колонки: `товар_ціна, доставка, собівартість, маржа, рейтинг, відгуки, останній_відгук, відгуки_звіт, склади, спосіб_доставки, строк_днів, listedNum, постачальник, лінк, артикул, прапорці`.

### Вибір 3 товарів CJ (`Parse CJ` = Select)
- **топ-3 релевантних за `listedNum`** (скільки продавців імпортували = проксі попиту/довіри). У CJ **пошуку немає рейтингу/відгуків/замовлень** — тому відбір по listedNum.
- CJ САМ розширює запит: у відповіді `keyWord:"car starter"` vs `keyWordOld:"car jump starter"` (викидає «jump») → лізуть мотори/ключі/наліпки → **фільтр релевантності обов'язковий** (`head`-слово seed + виключення JUNK/MOTOR-патернів + вимога POWER-ознак).

### Мапа полів CJ (перевірено)
- **Search** `data.content[].productList[]`: `nameEn, sellPrice`(рядок «14.93 -- 18.24» → min), `listedNum, id, sku, warehouseInventoryNum`. **Немає рейтингу/відгуків.**
- **Details** `data`: `variants[]{vid, variantSellPrice, variantNameEn, variantWeight}` (найдешевший варіант = собівартість; `vid` потрібен для Freight!), `productSku, categoryName, productProEn`(рядок `'["IS_ELECTRICITY"]'` — тест через `JSON.stringify`+regex, НЕ `.some`!). **`supplierName:null` — рейтингу тут теж нема.**
- **Inventory** `data.inventories[]{countryCode, totalInventoryNum}` (склади; hasLocal якщо US/DE/GB…), `variantInventories[]`.
- **Reviews** `data{total, list[]{score, comment, commentDate, countryCode}}` — часто `total:0` (більшість товарів без відгуків). Рейтинг = середнє `score`; сортування за `commentDate` desc → звіт останніх 3 + `останній_відгук`; прапорець `🕰 відгуки старі` якщо дата < 2025.
- **Freight** `data[]{logisticPrice, taxesFee, clearanceOperationFee, logisticAging, logisticName}` — беремо найдешевшу опцію; доставка = `logisticPrice+taxes+clearance`. POST, body `{startCountryCode:CN, endCountryCode:US, products:[{quantity:1, vid: $('CJ - Product Details').item.json.data.variants[0].vid}]}`.

### Результат (jump starter, усі 🔴)
CJ #1 $33.22+$23.69=$56.91 (0.76x) · #2 $59.06+$27=$86.06 (0.50x, рейтинг 5/16 але відгуки 2022 RU) · #3 $21.75+$32.24=$53.99 (0.80x). Доставка $24–32 на важку батарею → CJ збитковий для цього товару. Підтверджує: **AliExpress $19.30 (2.23x) — єдиний робочий варіант**, jump starter маргінальний попри 788 днів реклами.

### Уроки
- CJ image-search є лише на сайті (ручний), в API нема → CJ тільки keyword + фільтр релевантності.
- CJ QPS=1/сек — завжди тротлити (Loop+Wait / Batching).
- Рейтинг/відгуки лише в Reviews-ендпоінті і рідкісні; довіра на відборі = `listedNum`.
- Кожна CJ-нода затирає json → фінальний Parse читає всі по імені (`$('CJ - ...').all()`) + вирівнює за індексом.

---

## 🏁 ФІНАЛЬНИЙ РАПОРТ + ЗАМИКАННЯ СТАТУСУ (07.08.2026) — СИСТЕМА ЗАВЕРШЕНА

### Сценарій `05_DPRS_Final Report` (`M3-shortlist · fn-report · status-active`)
Збирає дані з УСІХ таб у єдиний Telegram HTML-звіт + рядок у `07_Report_Products`. Варіант «C» = і Telegram, і аркуш.

### Ланцюг
```
Pick Winners (status=FINAL) → [Read: 12_Seed_Inbox, 05_Competitors, 04_Suppliers] + Parse Competitors (свіжий Amazon)
   → Build Final Verdict → Telegram → Mark SENT (13_Verdicts) → Mark SENT (12_Seed_Inbox)
```

### Вузол `Build Final Verdict` (усе ДИНАМІЧНЕ, нічого зашитого)
Читає: `Pick Winners` (вердикт), `12_Seed_Inbox` (фото/джерело/відео/product_url), `Parse Competitors` (свіжий Amazon у-флоу, НЕ з таби — інакше race), `05_Competitors (Read)` (Google-магазини), `04_Suppliers` (лінки на товар для маржі).
- **Хелпери:** `num, esc, b, aTag, hUrl, anyUrl`. `anyUrl` дістає URL з формули `=HYPERLINK(...)` АБО з plain-URL.
- **Динамічні бренди:** `brandOf` = перше слово назви (uppercased); `brandFreq` рахує повтори; `isBrand`=freq≥2; `domBrand`=найчастіший. Жодних зашитих брендів.
- **Відносні пороги:** «дешеві варіанти» = ціна<медіани І продажі≥медіани (самонастройка під будь-який товар). Висновок конкуренції: >50k відгуків→🔴 насичено, >10k→🟡, >0→🟢.
- **Блоки HTML:** 📸 фото (невидиме посилання `​` + Disable Web Page Preview OFF → прев'ю зверху, обходить ліміт 1024 символи підпису) · 🎯 назва+вердикт · 📈 ПОПИТ · 🏪 КОНКУРЕНТИ (🥇 бестселер + 🏬 по маркетах з лінкованими цінами + 📌 динамічний висновок) · 💰 МАРЖА (назва платформи→search-лінк, ціна→лінк на товар через `anyUrl` з 04_Suppliers) · 🔗 ПОСИЛАННЯ (video/джерело/Meta Ad Library/Google Trends) · 🔎 ПОШУК ПО ПЛАТФОРМАХ (Ali/1688/CJ/Amazon по keyword) · ✅ ВЕРДИКТ.
- **Вихід:** `звіт_html`, `report_id=RPT-{pid}`, `ніша`, `маржа`, `маржа_платформа`, `роздрібна`, `amazon_count`, `amazon_median`, `amazon_bestseller`, `дата`, `фінальний_вердикт`.

### Аркуш `07_Report_Products` (заголовок, tab-separated)
```
report_id	product_id	товар	ніша	фінальний_вердикт	маржа	маржа_платформа	роздрібна	amazon_count	amazon_median	amazon_bestseller	звіт_html	дата
```

### Telegram node
Text=`{{ $json.звіт_html }}` · Parse Mode=`HTML` · Disable Web Page Preview=**OFF** (щоб фото-прев'ю рендерилось).

### КРИТИЧНИЙ фікс парсингу Telegram HTML
Помилка `Bad Request: can't parse entities: Unsupported start tag "$59.99"` = сирий `<` перед не-тегом. Причина була в рядку висновку `Дешеві варіанти <$${az_med}` (голий `<` перед `$`). Виправлено на `дешевше $`. **Плюс глобальний запобіжник** (для будь-якого товару назавжди):
```javascript
html = html.replace(/<(?!\/?(?:b|i|a)(?:\s[^>]*)?>)/g, '&lt;');
```
Екранує кожен `<`, що НЕ є нашим `<b>/<i>/<a>` — звіт більше ніколи не впаде на чужій назві з `<`.

### Замикання статусу (SENT)
Після Telegram — 2 Update-ноди (ставляться ПІСЛЯ відправки: якщо Telegram впав, статус лишається FINAL → наступний прогін повторить):
- `Mark SENT — 13_Verdicts`: match `product_id`, set `status=SENT`, `report_id`, `sent_at={{ $now.toISO() }}`. Нові колонки: `report_id	sent_at`.
- `Mark SENT — 12_Seed_Inbox`: match `inbox_id`, set `status=SENT`.

### ПОВНИЙ ЖИТТЄВИЙ ЦИКЛ СТАТУСУ (система замкнена 🔒)
```
NEW → QUEUED → VALIDATED → MARGIN → FINAL → SENT
```
`SENT` у PROTECT-списку гейта + жодна сцена не бере цей статус як вхідний → товар більше не прокручується, API не палиться на повторах.

### Уроки цього фіналу
- **`=HYPERLINK` при читанні повертає ЛЕЙБЛ, не URL.** Тримати сирий URL окремою колонкою АБО реконструювати (Amazon з `asin`) АБО `anyUrl()` дістає з формули/plain.
- **Amazon читати у-флоу (`Parse Competitors`), не з таби** — read може випередити свіжий write (race → Amazon=0).
- **USER_ENTERED текст не має починатися з `= + - @`** (Sheets прийме за формулу → #ERROR).
- **Telegram HTML: escape ВСЕ динамічне** через `esc()` + глобальний regex-запобіжник на `<`.

---

## ⚡ ПРОДУКТИВНІСТЬ GOOGLE SHEETS (07.08.2026) — Execute Once рятує квоту

### Симптом
`429 RESOURCE_EXHAUSTED` на Sheets read: `Quota exceeded ... Read requests per minute per user ... limit 60`. Читання «довго», падає на `12_Seed_Inbox`/`05_Competitors (Read)`.

### Справжня причина (не фільтр!)
Read-нода за замовчуванням **виконується один раз на КОЖЕН вхідний item**. Якщо на вхід приходить 49 items (напр. з `Parse Competitors`), нода читає табу **49 разів** → 49 read-запитів за секунди → миттєво >60/хв → 429. Плюс дропдаун Column у фільтрі не вантажиться (той самий 429) → фільтр порожній → віддає всю табу.

### Фікс (головний)
На **кожній** Read-ноді, куди приходить >1 item: **Settings → Execute Once = ON**. Тоді читання 1 раз замість N. Одне читання таби навіть на 2499 рядків = 1 запит (ОК). Саме Execute Once усуває і 429, і гальмування.

### Додатково (на виріст таб)
- **Фільтр по product_id** у Read-ноді (`Filters → Column=product_id, Value={{ $('Pick Winners').first().json.product_id }}`, `Options → Return All Matches`) — віддає лише рядки товару, а не всю табу. Спрацьовує тільки після Execute Once (бо дропдаун колонок вантажиться через API).
- **Retry On Fail** на всіх Sheets-нодах (Max Tries 5, Wait 12000 ms) — страховка від разових піків.
- **Архів SENT-рядків** в окрему табу — тримати активні таби малими.
- gviz HTTP `SELECT WHERE` або перехід на БД (Supabase) — коли таб стане дуже багато.

### Правило
Будь-яка Sheets Read-нода з багатьма вхідними items → **Execute Once обов'язково**.

---

## 🧹 УРОК 1688 (07.08.2026) — пошук, кодування, релевантність (велике)

Довга сесія багів по 1688. Фінальні висновки:

### 1. 1688 IMAGE search = сміття (підтверджено вкотре)
devcake «Scraper by Image» на 1688 повертає нерелевантне (скраби для тіла, халати, робот-пилососи). Для 1688 — ТІЛЬКИ keyword-пошук.

### 2. Пошуковий keyword: англійська працює, китайська UTF-8 — НІ
1688 приймає **англійський** keyword (`floor scrub brush`) і показує щітки — бо багато cross-border лістингів з англ. назвами. А **китайський UTF-8** у `s.1688.com/...offer_search.htm?keywords=` дає кракозябри (`簐版潜娓呎礧鎃`) і 0 результатів, бо цей ендпоінт історично чекає **GBK**, а `encodeURIComponent` дає UTF-8. GBK у n8n Code без `iconv-lite` не згенерувати.
**Рішення:** пошуковий лінк 1688 = **англійський seed** (латиниця однакова в GBK/UTF-8):
`https://s.1688.com/selloffer/offer_search.htm?keywords=${encodeURIComponent(generic_seed)}`

### 3. Китайський ключ потрібен ЛИШЕ для фільтра релевантності (не для лінка)
`Build CN Query` (LLM) перекладає товар → китайський keyword. Промпт має бути **контекстний**: додати нішу + заборонити багатозначні дослівні переклади (`scrub` тут = 刷 щітка, НЕ 磨砂 косметичний скраб; `starter` = 启动电源, не 开胃菜). Інакше LLM дає `磨砂膏` (крем для обличчя). Правильно для floor scrub brush: `地板清洗刷`.
Сирий вивід LLM вкладений: `output[0].content[0].text = "{\"cn\":\"...\"}"` → потрібна нода-парсер, що дістає `cn` у чисте поле `keyword_cn`.

### 4. Фільтр релевантності — по КИТАЙСЬКИХ біграмах ключа
Англійський фільтр по словах пропускав косметику (в назвах є англ. «scrub» = 1 збіг). Фікс: з `keyword_cn` (地板清洗刷) будуємо біграми (`地板`,`板清`,`清洗`,`洗刷`) і вимагаємо, щоб китайська назва містила хоч одну. Справжні щітки мають `地板刷`→`地板`✓; косметика/халати/робот-частини — ні. Динамічно для будь-якого товару (напр. `汽车应急启动电源`→`汽车`,`应急`…).
Fallback (нема cnKw): англ. ≥2 слова (щоб «body scrub cream» = лише «scrub» відсіявся).

### 5. Прогресивний добір до 3 + floor-fallback
Спершу виробники з рейтингом → інші не-перепродавці → будь-хто (з релевантних). `floor` (ціна ≥ роздр./4) застосовується лише якщо після нього лишається ≥3, інакше ігнорується (щоб не відсікати дешеві справжні товари, напр. щітка $1.82 при floor $5.25).

### Результат (floor scrub brush)
2 справжні щітки з фабрики 潜山超凡制刷: V型地板刷 $1.82 (3.61x 🟢), 360°地板刷 $3.61 (2.76x 🟡). 2, а не 3 — бо в видачі лише 2 релевантні (краще 2 справжні за 3 з кремом). Більше — page 2+ devcake.

### Спільна колонка `пошук_лінк` / `пошук_1688`
Кожна margin-гілка кладе свій пошуковий лінк у колонку 04_Suppliers; звіт бере його для кнопки платформи. Ali/CJ — англ. keyword, 1688 — англ. (не китайський, через GBK).

---

## 🧭 АРХІТЕКТУРА СИГНАЛІВ SIG/PRD (08.08.2026) — фундаментальний апгрейд

Система шукає **не «одного віннера»**, а збирає **незалежні докази попиту** з 5 джерел на той самий товар, зводячи їх в один канонічний продукт.

### Дворівнева ідентифікація
- **SIG-*** = один **доказ (сигнал)** з конкретного джерела. `inbox_id` у 12_Seed_Inbox = SIG.
- **PRD-*** = **канонічний продукт**. Одному PRD належить багато SIG.
- Приклад: TikTok `cordless pressure washer` (SIG-AAA) + Instagram `battery pressure washer` (SIG-BBB) + YouTube `portable power washer` (SIG-CCC) → **усі → PRD-001** (один реальний продукт, 3 докази).

### ПРАВИЛО inbox_id (SIG) — КОРЕКЦІЯ
```javascript
inbox_id = "SIG-" + hash36(source + "|" + generic_seed)
```
- у межах ОДНОГО джерела: та сама ніша з різних відео → **один SIG** (дедуп всередині джерела);
- МІЖ джерелами: та сама ніша з TikTok/YouTube/Trends → **різні SIG** (зберігаємо 3 докази);
- **НЕ** `hash(seed)` (склеїло б джерела й знищило докази). Resolver зшиває SIG у PRD пізніше.

### 5 ДЖЕРЕЛ-СИГНАЛІВ
1. **TikTok** (`tiktok_shop`) — video_url + image_url (CDN) ОРИГІНАЛЬНІ (пріоритет над GS); перегляди/продажі/momentum з related-відео.
2. **Instagram** — Reel URL + Reel image ОРИГІНАЛЬНІ (пріоритет); перегляди, caption, хештеги.
3. **YouTube** — 26 US-запитів, YouTube API (views/views_per_day/engagement/tags), BREAKOUT/RISING/PROVEN; LLM витягує лише явно названі фізичні товари. (Незакрито: Prepare Batches → HTTP Request до OpenAI з повним промптом, 8 пакетів.)
4. **Google Trends Related** (`google_trends_related`) — related-запити; свого відео/фото НЕМА → video_url порожній, фото/лінк з Google Shopping; momentum з trend-сигналу.
5. **Google Trends Digest** (`google_trends_digest`) — trending-запити (ранг/traffic); фото/лінк з Google Shopping.

**TikTok/IG:** оригінальні фото+відео мають пріоритет над Google Shopping.
**Trends:** фото/лінк тільки з Google Shopping (свого медіа нема).
Google Shopping для всіх додає: конкурентів, comp_min/median/max, comp_count, рейтинг — **не перезаписуючи** оригінальні TikTok/IG фото/відео.

### Product Resolver (окремий flow, після YouTube)
1. Читає весь Seed Inbox.
2. Gate M2 — відсів сміття/ризиків/слабких (SATURATED/COOLING/EXCLUDE).
3. Код знаходить точні + нормалізовані дублікати.
4. LLM перевіряє лише неоднозначні збіги.
5. Створює/знаходить канонічний **PRD-***.
6. Зв'язує всі відповідні SIG з PRD.
7. Створює одну картку в `02_Products`.

### Таблиця Product_Signal_Map (PRD ↔ SIG)
Поля: `product_id (PRD) · inbox_id (SIG) · source · generic_seed · match_type · match_confidence · linked_at`.
Так сигнали не перезаписуються й не втрачаються.

### Ролі product_id
- Зараз SIG стоїть у `product_id` хештегів — **тимчасово**.
- Остаточно: **SIG = ідентифікатор сигналу**, **PRD = єдиний product_id** для маржі/звіту.

### Фінальний маршрут
```
TikTok+IG+YouTube+Trends Related+Trends Digest
 → SIG-сигнали → Seed Inbox → Gate M2 → Product Resolver → PRD-картка (02_Products)
 → Google Shopping + соц-статистика → семантика → реклама → постачальники → скоринг
```
У картці PRD збирається найкраще фото/відео + усі соц-сигнали, хештеги, конкуренти, семантика, реклама, постачальники — **один продукт з повною доказовою базою**, а не 3 розрізнені «товари».

### Momentum (нагадування — актуальність тренду)
🔥RISING (свіжі ≥20%) / ⚡SPIKE (1 свіже відео) / ⚠️COOLING (5-20%) / 💀SATURATED (0 свіжих) / 🆕NEW / ❔NO_DATA.
Gate пропускає живі (RISING/SPIKE/NEW), відсікає старі хіти (SATURATED/COOLING). «Старі хіти не потрібні».

### Filter1 дискавері (перед enrichment/записом)
Пропускати: momentum `RISING|SPIKE|NEW` + niche валідна (не REJECTED_CATEGORY/REVIEW).
Блокувати: SATURATED/COOLING (старі) + EXCLUDE-ніші/невпевнені. Економить SerpApi й тримає дані чистими.
