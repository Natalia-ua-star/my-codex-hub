# Dropshipping Research System

Pulls winning-product signals from TikTok, TikTok Shop, Instagram, YouTube and
Google (via SerpAPI) across English-speaking markets, scores them, and writes
everything into `results.xlsx`.

## Sources

| Source | Method | Geo scope |
|---|---|---|
| YouTube Data API v3 | `google-api-python-client` | US, GB, AU, CA, NZ (per `regionCode`) |
| TikTok organic | Apify `clockworks/tiktok-scraper` | US, GB, AU, CA, NZ (per `proxyCountryCode`) |
| TikTok Shop | Apify actor (configurable) | US, GB only — the only live TikTok Shop markets |
| Instagram | Apify `apify/instagram-scraper` | English hashtags, no geo split |
| Shopify competitors | SerpAPI (Google Search) | Global, English queries |

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
`YouTube_Winners`, `Shopify_Competitors`, `Summary`. Every row includes a
`search_date` column.

## Before your first real run

- **Apify actor schemas change.** `TIKTOK_ACTOR_ID`, `TIKTOK_SHOP_ACTOR_ID`
  and `INSTAGRAM_ACTOR_ID` in `config.py` (overridable via `.env`) point to
  commonly-used actors. Open each actor's **Input** tab on the Apify console
  and confirm the field names in `sources/*.py` `_build_input()` still match
  — especially for TikTok Shop, where several different actors exist with
  different schemas.
- **YouTube quota.** `search.list` costs ~100 quota units per call (default
  daily quota is 10,000). A full run = niches × queries × countries calls.
  Tune `YOUTUBE_MAX_QUERIES_PER_NICHE` / `--niches` / `--countries` to stay
  within budget.
- **API keys never get written to `results.xlsx` or logged.** `.env` is
  git-ignored.

## Scoring

Each platform gets a 0-100 `score`, min-max normalized *within* its
(niche[, country]) group and weighted by `config.SCORE_WEIGHTS` (views 0.4,
likes 0.3, comments 0.15, shares 0.15). Shopify competitors are ranked by how
many distinct search queries surfaced the same domain (a proxy for market
visibility), not a 0-100 score.
