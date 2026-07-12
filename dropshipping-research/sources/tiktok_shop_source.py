"""Apify TikTok Shop Scraper — US and GB only (currently the only active TikTok Shop markets).

There is no single canonical "TikTok Shop Scraper" actor on Apify — several
authors publish one, each with its own input schema. TIKTOK_SHOP_ACTOR_ID in
config.py (overridable via .env) picks which one to call. Before a real run,
open that actor's "Input" tab on the Apify console and confirm the field
names below match; adjust `_build_input` / `_normalize_item` if not.
"""

import logging

import config
from sources.apify_utils import run_actor_and_get_items
from sources.common import contains_excluded, safe_get, today_str

logger = logging.getLogger(__name__)


def _build_input(keywords: list, country: str) -> dict:
    return {
        "searchQueries": keywords,
        "country": country,
        "countryCode": country,
        "maxItems": config.TIKTOK_RESULTS_PER_HASHTAG,
    }


def _normalize_item(item: dict, niche_key: str, country: str) -> dict:
    title = safe_get(item, "title", "productName", "name", default="")
    price = safe_get(item, "price", "salePrice", default="")
    sold_count = safe_get(item, "soldCount", "unitsSold", "sales", default=0)
    rating = safe_get(item, "rating", "productRating", default="")
    shop_name = safe_get(item, "shopName", "sellerName", "shop", default="")

    return {
        "niche": niche_key,
        "country": country,
        "source": "TikTok Shop",
        "title": title,
        "shop_name": shop_name,
        "price": price,
        "sold_count": sold_count,
        "rating": rating,
        "url": safe_get(item, "url", "productUrl", default=""),
        "search_date": today_str(),
    }


def fetch_tiktok_shop_winners(niches: dict) -> list:
    """Only queries config.TIKTOK_SHOP_COUNTRIES (US, GB), regardless of the
    global COUNTRIES list, since TikTok Shop isn't active in AU/CA/NZ yet."""
    if not config.APIFY_API_TOKEN:
        logger.warning("APIFY_API_TOKEN is not set — skipping TikTok Shop source.")
        return []

    token = config.APIFY_API_TOKEN
    records = []

    for niche_key, niche_cfg in niches.items():
        keywords = niche_cfg["shopify_queries"]  # reuse commerce-intent keywords
        exclude_keywords = niche_cfg.get("exclude_keywords", [])

        for country in config.TIKTOK_SHOP_COUNTRIES:
            run_input = _build_input(keywords, country)
            items = run_actor_and_get_items(token, config.TIKTOK_SHOP_ACTOR_ID, run_input)

            for item in items:
                record = _normalize_item(item, niche_key, country)
                if contains_excluded(record["title"], exclude_keywords):
                    continue
                records.append(record)

    return records
