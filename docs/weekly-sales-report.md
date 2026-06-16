# Weekly Sales Report — Google Apps Script

## Що робить скрипт

Автоматично створює щотижневі звітні таби у Google Sheets з продажами, погодою та подіями. Запускається кожного понеділка о 7:00 AM Chicago time.

## Таблиці

| Змінна | ID | Призначення |
|--------|----|-------------|
| `SALES_SS_ID` | `1qyf8Up1...` | Toast Master — джерело даних (Fact_Daily_Sales, Events_Daily, Script_Log) |
| `REPORT_SS_ID` | `1_hZvCM6...` | Weekly Report — куди пишуться таби |

## Структура таба (8 рядків × 9 колонок)

```
Row 1  │ Merged header — дата тижня (Monday)
Row 2  │ EVENTS  │ Mon │ Tue │ Wed │ Thu │ Fri │ Sat │ Sun │ EVENTS
Row 3  │ WEATHER │ ... │ ... │ ... │ ... │ ... │ ... │ ... │ WEATHER
Row 4  │ DAY     │ m-d │ m-d │ m-d │ m-d │ m-d │ m-d │ m-d │ Week total
Row 5  │ In Store│  $  │  $  │  $  │  $  │  $  │  $  │  $  │ SUM
Row 6  │ Catering│  $  │  $  │  $  │  $  │  $  │  $  │  $  │ SUM
Row 7  │Wholesale│  $  │  $  │  $  │  $  │  $  │  $  │  $  │ SUM
Row 8  │ Total   │  $  │  $  │  $  │  $  │  $  │  $  │  $  │ SUM
```

Назва таба: `W Jun 8-14`, `W Jun 15-21` тощо.

## Джерела даних

### Продажі — `Fact_Daily_Sales`
Колонки: `business_date`, `dinein_sales`, `catering_sales`, `wholesale_sales`

### Погода — Open-Meteo API (безкоштовно, без ключа)
- Forecast: `api.open-meteo.com/v1/forecast` — майбутні тижні
- Archive: `archive-api.open-meteo.com/v1/archive` — минулі тижні
- Координати: St. Paul, MN (lat 44.9537, lon -93.0900)
- Параметри: `temperature_2m_max`, `weathercode` у Fahrenheit

### Події — два джерела, об'єднуються через ` | `
1. **US Federal Holidays** — `date.nager.at/api/v3/PublicHolidays/{year}/US`
2. **Events_Daily** (Toast Master) — колонки: `date`(A), `event`(B), `location`, `time`, `type`, `category`, `source`, `impact`, `expected_demand`, `notes`

> Timezone Events_Daily: `America/Chicago`. Таблиця має бути в тому ж timezone.

## Функції

| Функція | Коли запускати |
|---------|---------------|
| `installAllTriggers()` | Один раз при налаштуванні |
| `listTriggers()` | Перевірити встановлені тригери |
| `createWeeklyReport()` | Автоматично щопонеділка / вручну |
| `loadHistoricalWeeks()` | Один раз — заповнити з `HISTORY_START` |
| `refillAllExistingTabs()` | Перезаписати всі таби (продажі + погода + події) |
| `refillEventsAllTabs()` | Перезаписати тільки події |
| `setupScriptLog()` | Один раз — створити Script_Log якщо не існує |

## Тригер

Встановлюється через `installAllTriggers()`:
- `createWeeklyReport` — кожного понеділка о 7:00 AM `America/Chicago`

## Логування — Script_Log (Toast Master)

| Колонка | Опис |
|---------|------|
| Timestamp | Час виконання |
| Process | Назва функції |
| Status | SUCCESS / ERROR / PARTIAL |
| Source Rows | Всього рядків у джерелі |
| Existing Rows | Вже існуючих |
| New Rows | Нових створено |
| Written Rows | Записано |
| Message | Деталі |
| Script Version | `WEEKLY_REPORT_V2` |

## Константи (CONFIG)

```javascript
const HISTORY_START = '2026-05-01';  // початок завантаження історії
const FONT          = 'Montserrat';
const WEATHER_LAT   = 44.9537;       // St. Paul, MN
const WEATHER_LON   = -93.0900;
```

## Частi помилки

| Помилка | Причина | Вирішення |
|---------|---------|-----------|
| `Script_Log not found` | Таба не створена | Запусти `setupScriptLog()` |
| Events порожні | Timezone мismatch в Events_Daily | Перевір: Файл → Налаштування → America/Chicago |
| `Tab already exists` | Таб вже є | Нормально, пропускається |
| Weather error | API недоступний | Тимчасово, повторити пізніше |
