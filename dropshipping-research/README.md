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

Niches: **dogs** (accessories/gadgets only — food, treats, grooming and health
products are filtered out), **home**, **hobby**. Edit `config.py` to change
niches, keywords, hashtags, countries, or scoring weights.

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
python main.py --niches dogs --countries US GB --skip tiktok_shop
```

Output: `results.xlsx` with tabs `TikTok_Winners`, `Instagram_Winners`,
`YouTube_Winners`, `Shopify_Competitors`, `AliExpress_Winners`, `Summary`.
Every row includes a `search_date` column.

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

## Scoring

Each social platform gets a 0-100 `score`, min-max normalized *within* its
(niche[, country]) group and weighted by `config.SCORE_WEIGHTS` (views 0.4,
likes 0.3, comments 0.15, shares 0.15). AliExpress uses its own
`config.ALIEXPRESS_SCORE_WEIGHTS` (orders 0.5, rating 0.3, review_count 0.2),
normalized within niche. Shopify competitors are ranked by how many distinct
search queries surfaced the same domain (a proxy for market visibility), not
a 0-100 score.
