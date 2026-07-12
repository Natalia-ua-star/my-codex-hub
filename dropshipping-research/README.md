# Dropshipping Research System

Pulls winning-product signals from TikTok, TikTok Shop, Instagram, YouTube,
Google (via SerpAPI) and AliExpress across English-speaking markets, scores
them, and writes everything into `results.xlsx`.

## Sources

| Source | Method | Geo scope |
|---|---|---|
| YouTube Data API v3 | `google-api-python-client` | US, GB, AU, CA, NZ (per `regionCode`) |
| TikTok organic | Apify `clockworks/tiktok-scraper` | US, GB, AU, CA, NZ (per `proxyCountryCode`) |
| TikTok Shop | Apify actor (configurable) | US, GB only — the only live TikTok Shop markets |
| Instagram | Apify `apify/instagram-scraper` | English hashtags, no geo split |
| Shopify competitors | SerpAPI (Google Search) | Global, English queries |
| AliExpress | Apify actor (configurable), sorted by `orders` | Global marketplace, no geo split |

Niches: **auto_accessories**, **pet_products**, **diy_home_improvement**,
**gardening**, **fishing**. Edit `config.py` to change niches, keywords,
hashtags, countries, or scoring weights.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# then fill in YOUTUBE_API_KEY, APIFY_API_TOKEN, SERP_API_KEY in .env
```

## Run

```bash
# Preview the workbook format with synthetic data (no API calls, no cost):
python main.py --demo

# Full run, all niches/countries/sources:
python main.py

# Narrower run to control API cost:
python main.py --niches fishing --countries US GB --skip tiktok_shop
```

Output: `results.xlsx` with tabs `TikTok_Winners`, `Instagram_Winners`,
`YouTube_Winners`, `Shopify_Competitors`, `AliExpress_Winners`, `Summary`.
Every row includes a `search_date` column.

## Google Sheets sync (daily auto-append)

`python main.py --push-to-sheets` appends today's rows into **two live Google
Sheets** (not the local `results.xlsx`) — rows accumulate day over day, they
are never overwritten:

- **Main spreadsheet** — tabs `TikTok_Winners`, `Instagram_Winners`,
  `YouTube_Winners`, `Shopify_Competitors`.
- **Separate AliExpress spreadsheet** — tab `AliExpress_Winners`.

This needs its own credential (a Google service account), separate from the
3 content API keys, because appending rows to an existing sheet requires the
real Sheets API — a plain "connect your Google account" OAuth connector can
only create/replace whole files, not append. One-time setup:

1. [console.cloud.google.com](https://console.cloud.google.com) → a project
   (can be the same one as your YouTube API key) → **APIs & Services →
   Library** → enable **Google Sheets API**.
2. **APIs & Services → Credentials → Create Credentials → Service account**
   → give it any name → **Keys → Add Key → Create new key → JSON** → download
   it, save it in this folder as `service_account.json` (already git-ignored).
3. Open the downloaded JSON, copy the `client_email` value (looks like
   `xxx@yyy.iam.gserviceaccount.com`).
4. Set `GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json` in `.env`.
5. Run `python main.py --push-to-sheets` once. On this first run
   `MAIN_SPREADSHEET_ID`/`ALIEXPRESS_SPREADSHEET_ID` are blank, so the script
   **creates both spreadsheets** and logs their IDs and URLs.
6. **Share each new spreadsheet** with the `client_email` from step 3 as
   **Editor** (File → Share in Google Sheets) — otherwise the next run can't
   write to it.
7. Copy both IDs from the logs into `MAIN_SPREADSHEET_ID` /
   `ALIEXPRESS_SPREADSHEET_ID` in `.env` so every future run appends to the
   *same* two sheets instead of creating new ones.

To actually run **every day** automatically, schedule `python main.py
--push-to-sheets` with cron (Linux/Mac), Task Scheduler (Windows), or a
Claude Code Routine (`create_trigger` with a daily `cron_expression`) that
fires this command in your project folder.

## AliExpress winner + trust analysis

`AliExpress_Winners` is sorted by order count (best-sellers) per niche and
includes, per product: `price`, `orders`, `rating`, `review_count`,
`seller_name`, `seller_rating`, `seller_positive_feedback`, and a computed
`trusted_seller` flag (seller rating ≥ `ALIEXPRESS_TRUSTED_SELLER_RATING`,
default 4.5/5, OR positive-feedback % ≥ `ALIEXPRESS_TRUSTED_SELLER_FEEDBACK_PCT`,
default 95%). Both thresholds live in `config.py`. This covers product/seller
rating analysis, not full review-text sentiment — swapping in a dedicated
reviews actor (e.g. one of the AliExpress reviews scrapers on Apify) would be
a follow-up if you need per-review text/sentiment, not just rating aggregates.

## Before your first real run

- **Apify actor schemas change.** `TIKTOK_ACTOR_ID`, `TIKTOK_SHOP_ACTOR_ID`,
  `INSTAGRAM_ACTOR_ID` and `ALIEXPRESS_ACTOR_ID` in `config.py` (overridable
  via `.env`) point to commonly-used actors. Open each actor's **Input** tab
  on the Apify console and confirm the field names in `sources/*.py`
  `_build_input()` still match — especially for TikTok Shop and AliExpress,
  where several different actors exist with different schemas.
- **YouTube quota.** `search.list` costs ~100 quota units per call (default
  daily quota is 10,000). A full run = niches × queries × countries calls.
  Tune `YOUTUBE_MAX_QUERIES_PER_NICHE` / `--niches` / `--countries` to stay
  within budget.
- **API keys never get written to `results.xlsx` or logged.** `.env` is
  git-ignored.
- **Apify calls use the REST API directly (`requests`), not the `apify-client`
  SDK.** See `sources/apify_utils.py` docstring — the SDK's HTTP backend
  failed every request in a sandboxed environment whose network policy
  otherwise allowed `api.apify.com` fine. If you're not on such a sandbox and
  prefer the SDK, swapping `apify_utils.py` back to `ApifyClient` is a small
  change.

## Scoring

Each social platform gets a 0-100 `score`, min-max normalized *within* its
(niche[, country]) group and weighted by `config.SCORE_WEIGHTS` (views 0.4,
likes 0.3, comments 0.15, shares 0.15). AliExpress uses its own
`config.ALIEXPRESS_SCORE_WEIGHTS` (orders 0.5, rating 0.3, review_count 0.2),
normalized within niche. Shopify competitors are ranked by how many distinct
search queries surfaced the same domain (a proxy for market visibility), not
a 0-100 score.
