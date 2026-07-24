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

## РЕЄСТР НАЗВ НОД (n8n) — джерело правди

**Правило:** назви нод у коді (`$("Ім'я")`) мають ТОЧНО збігатися з цим реєстром.
Якщо в n8n перейменували ноду — оновити і тут, і в усіх посиланнях у коді.

### Конвеєр TikTok Shop (discovery за нішею → товари + хештеги)

Потік:
```
[ScrapeCreators TikTok Shop Search]  → Parse TikTok Shop
Parse TikTok Shop → [ScrapeCreators Product Details]  (URL динамічний: {{ $json.product_url }})
[Product Details] → Parse Enrichment
Parse Enrichment → AI Extract → Build Seed Inbox → Filter (NEW)
Filter (NEW) ├─→ Google Sheets: 12_Seed_Inbox      (Append or Update, match inbox_id)
             ├─→ Explode Hashtags → Google Sheets: Hashtag_Stats  (Append or Update, match stat_id)
             └─→ Build TikTok Report → Telegram
```

| Назва ноди | Тип | Роль |
|---|---|---|
| `Parse TikTok Shop` | Code (All Items) | з Shop Search → рядки товарів, `traffic=sold_count`, будує `product_url`, MIN_SOLD, сорт по продажах |
| `Product Details` | ScrapeCreators HTTP | по `product_url` → `product_info` + `related_videos`; **Run Once for Each Item**, URL = `{{ $json.product_url }}` |
| `Parse Enrichment` | Code (All Items) | пара `$("Parse TikTok Shop")` + `$input` по індексу; органіка з `related_videos`, CUTOFF=2026-01-01, `money_hashtags` |
| `AI Extract` | OpenAI Message (JSON, Each Item) | брудний `raw_title` → `generic_seed`+`niche`+`confident` (без is_product — у Shop усе товари) |
| `Build Seed Inbox` | Code (All Items) | merge `$("Parse Enrichment")`+`$input`(AI) по індексу → 18 полів inbox + бонус; `inbox_id=SIG-hash(source_id)`, статус NEW/REVIEW/REJECTED_CATEGORY |
| `Filter (NEW)` | Filter | `{{ $json.status }}` == `NEW` |
| `Explode Hashtags` | Code (All Items) | `source_detail` → 1 хештег = 1 рядок під `Hashtag_Stats`, `stat_id=HSH-hash(tag+product)`, `product_id`=source_id |
| `Build TikTok Report` | Code (All Items) | звіт по товарах → `text` (HTML, нарізка 3800) |

**Ключові правила з'єднань (щоб пари по індексу не з'їхали):**
- `Build Seed Inbox` бере стрілку **з `AI Extract`** (не з Parse Enrichment) — інакше `$input`
  не той, `generic_seed` порожній, статус зривається в REVIEW.
- `AI Extract` і `Product Details` — режим **Run Once for Each Item** (не Execute Once).
- Пари складаються **в коді по індексу** — фізична Merge-нода НЕ потрібна, ланцюг «в рядок».

### Оновлена схема `12_Seed_Inbox` (18 колонок; +3 для TikTok)
```
inbox_id	source	source_detail	raw_title	generic_seed	price	currency	rating	rating_count	traffic	product_url	source_id	country	status	discovered_at	niche	organic_views	organic_views_all
```
`niche / organic_views / organic_views_all` заповнює лише TikTok Shop; для інших джерел порожні.

### `Hashtag_Stats` (12 колонок; +product_id) — банк грошових хештегів
```
stat_id	source	hashtag	niche	videos_total	products_found	product_rate	avg_views	total_views	product_id	top_products	checked_at
```
З TikTok Shop: `videos_total`=згадки хештега у related_videos, `products_found`=1, `total_views`=organic_views товару,
`product_id`=source_id (склейка з інбоксом), `top_products`=generic_seed. `product_rate`/`avg_views` порожні —
заповняться зворотною гілкою (скан хештега → скільки відео товарні).

### Робочі домовленості (формат відповідей)
- **Заголовки колонок — завжди через Tab** (одразу вставляються по колонках у Sheets).
- **Завжди повний код**, не сніпети.
- Ключі API — лише в n8n Credentials, ніколи в чат.
- Метод створення шапки в локалі користувача: `=SPLIT("a,b,c";",")` (роздільник аргументів `;`).
